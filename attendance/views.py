import calendar
from collections import OrderedDict

from django.contrib import messages
from django.contrib.auth.models import Group
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django.utils.html import escape
from django.views.decorators.csrf import csrf_exempt
from django_datatables_view.base_datatable_view import BaseDatatableView
from weasyprint import HTML, CSS

from mamtaApp.views import check_group
from .models import *
from datetime import datetime, timedelta, date
import base64

from django.core.files.base import ContentFile

today_date = datetime.today().date()
last_3_month_date = datetime.today().date() - timedelta(days=45)


class LoginSystemListJson(BaseDatatableView):
    order_columns = ['id', 'systemName', 'location', 'username', 'password', 'datetime', 'action', ]

    def get_initial_queryset(self):

        return LoginSystem.objects.select_related().select_related().filter(isDeleted__exact=False)

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(systemName__icontains=search) | Q(location__icontains=search), isDeleted__exact=False)

        return qs

    def prepare_results(self, qs):
        json_data = []
        i = 1
        for item in qs:
            if 'Moderator' in self.request.user.groups.values_list('name', flat=True):
                action = '''N/A'''.format(item.pk)
            else:
                action = '''<span>

                                   <a class="hideModerator" data-toggle="modal" data-target="#defaultModalEdit" onclick = "getSystemData('{}','{}','{}','{}')" ><button style="background-color: #3F51B5;color: white;" type="button"
                           class="btn  waves-effect " data-toggle="modal"
                           data-target="#largeModalEdit">
                       <i class="material-icons">border_color</i></button> </a></span>'''.format(item.pk,
                                                                                                 item.systemName,
                                                                                                 item.location,
                                                                                                 item.password, item.pk)

            json_data.append([
                escape(i),
                escape(item.systemName),  # escape HTML for security reasons
                escape(item.location),  # escape HTML for security reasons
                escape(item.username),
                escape(item.password),
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),
                action
                ,

            ])
            i = i + 1
        return json_data


class EmployeeListJson(BaseDatatableView):
    order_columns = ['id', 'photo', 'name', 'phoneNumber', 'address', 'password', 'inTime', 'outTime', 'datetime',
                     'action', ]

    def get_initial_queryset(self):

        return Employee.objects.select_related().filter(isDeleted__exact=False)

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(name__icontains=search) | Q(phoneNumber__icontains=search) | Q(address__icontains=search),
                isDeleted__exact=False)

        return qs

    def prepare_results(self, qs):
        json_data = []
        i = 1
        for item in qs:
            if 'Moderator' in self.request.user.groups.values_list('name', flat=True):
                action = '''N/A'''.format(item.pk)
            else:
                action = '''<span>

                                   <a class="hideModerator" href ="/attendance/employee/edit/{}/" ><button style="background-color: #3F51B5;color: white;" type="button"
                           class="btn  waves-effect " data-toggle="modal"
                           data-target="#largeModalEdit">
                       <i class="material-icons">border_color</i></button> </a>
                        <button onclick="getStaffID('{}')" style="background-color: #e91e63;color: white;" type="button" class="btn  waves-effect " data-toggle="modal" data-target="#defaultModal">
            
            
                                                    <i class="material-icons">delete</i></button>
                       </span>'''.format(item.pk, item.pk)

            json_data.append([
                escape(i),
                '''<img class="imageTable zoom" src="{}" alt="" >'''.format(item.photo.thumbnail.url),
                escape(item.name),  # escape HTML for security reasons
                escape(item.phoneNumber),  # escape HTML for security reasons
                escape(item.address),
                escape(item.password),
                escape(item.inTime.strftime('%I:%M %p')),
                escape(item.outTime.strftime('%I:%M %p')),
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),
                action
                ,

            ])
            i = i + 1
        return json_data


class EmployeeListForAttendanceJson(BaseDatatableView):
    order_columns = ['id', 'photo', 'name', 'inTime', 'outTime', 'action', ]

    def get_initial_queryset(self):

        return Employee.objects.select_related().filter(isDeleted__exact=False)

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(name__icontains=search), isDeleted__exact=False)

        return qs

    def prepare_results(self, qs):
        json_data = []
        i = 1

        for item in qs:
            try:
                attend = EmployeeAttendance.objects.select_related().get(employeeID__id=item.pk,
                                                                         attendanceDate__icontains=datetime.today().date())
            except:
                attend = EmployeeAttendance()
                attend.employeeID_id = item.pk
                attend.attendanceDate = datetime.today().date()
                attend.save()
            action = ''

            if 'Moderator' in self.request.user.groups.values_list('name', flat=True):
                action = '''N/A'''.format(item.pk)
            else:

                if attend.loginTime is None:
                    action = action + '''<button type="button" class="btn btn-primary" data-toggle="modal"
                                                data-target="#myModal" onclick="loginModal({})">LOGIN
                                        </button>  '''.format(item.pk)
                else:
                    action = action + '''<button type="button" class="btn btn-success">{}
                                        </button>   '''.format(attend.loginTime.strftime('%I:%M %p'))

                if attend.logoutTime is None:
                    action = action + '''   <button type="button" class="btn btn-danger" data-toggle="modal"
                                                data-target="#myModal_out" onclick="logoutModal({})">LOGOUT</button>'''.format(
                        item.pk)
                else:

                    action = action + '''   <button type="button" class="btn btn-success">{}
                                        </button>'''.format(attend.logoutTime.strftime('%I:%M %p'))
                    # action = ''' <button type="button" class="btn btn-primary" data-toggle="modal"
                    #                                 data-target="#myModal" onclick="loginModal()">LOGIN
                    #                         </button>
                    #
                    #                         <button type="button" class="btn btn-danger" data-toggle="modal"
                    #                                 data-target="#myModal_out" onclick="logoutModal()">LOGOUT</button>'''.format(item.pk, item.pk)

            json_data.append([
                escape(i),
                '''<img class="imageTable zoom" src="{}" alt="" >'''.format(item.photo.thumbnail.url),
                escape(item.name),  # escape HTML for security reasons
                escape(item.inTime.strftime('%I:%M %p')),
                escape(item.outTime.strftime('%I:%M %p')),

                action
                ,

            ])
            i = i + 1
        return json_data


class EmployeeListForAttendanceAdminJson(BaseDatatableView):
    order_columns = ['id', 'photo', 'name', 'timing', 'loginTime',
                     'password', 'loginRemark', 'logoutTime',
                     'logoutPhoto', 'logoutRemark', 'action', ]

    def get_initial_queryset(self):

        return Employee.objects.select_related().filter(isDeleted__exact=False)

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(name__icontains=search), isDeleted__exact=False)

        return qs

    def prepare_results(self, qs):
        json_data = []
        i = 1
        sDate = self.request.GET.get('startDate')
        startDate = datetime.strptime(sDate, '%d/%m/%Y')

        for item in qs:
            try:
                attend = EmployeeAttendance.objects.select_related().get(employeeID__id=item.pk,
                                                                         attendanceDate__icontains=startDate.date())
            except:
                attend = EmployeeAttendance()
                attend.employeeID_id = item.pk
                attend.attendanceDate = startDate.date()
                attend.save()
            action = ''

            if attend.loginTime is None:
                loginTime = 'N/A'
                loginPhoto = 'N/A'
                loginRemark = 'N/A'
            else:
                loginTime = '''<button type="button" class="btn btn-info">{}
                                    </button>   '''.format(attend.loginTime.strftime('%I:%M %p'))
                loginPhoto = '''<img class="imageTable zoom" src="{}" alt="" >'''.format(
                    attend.loginPhoto.thumbnail.url)
                loginRemark = attend.loginRemark

            if attend.logoutTime is None:
                logoutTime = 'N/A'
                logoutPhoto = 'N/A'
                logoutRemark = 'N/A'
            else:

                logoutTime = '''<button type="button" class="btn btn-info">{}
                                    </button>'''.format(attend.logoutTime.strftime('%I:%M %p'))
                logoutPhoto = '''<img class="imageTable zoom" src="{}" alt="" >'''.format(
                    attend.logoutPhoto.thumbnail.url)
                logoutRemark = attend.logoutRemark

            timing = '''<button type="button" class="btn btn-success">{}
                                        </button> / <button type="button" class="btn btn-success">{}
                                        </button>  '''.format(item.inTime.strftime('%I:%M %p'),
                                                              item.outTime.strftime('%I:%M %p'))

            status = 'N/A'
            if attend.loginTime is None and attend.logoutTime is None:
                status = 'Absent'
            if attend.loginTime is None and attend.logoutTime is not None:
                status = 'Not Login'
            if attend.loginTime is not None and attend.logoutTime is None:
                status = 'Not Logout'

            if attend.loginTime is not None and attend.logoutTime is not None:
                if ((datetime.strptime(item.outTime.strftime('%H:%M'), "%H:%M") - datetime.strptime(
                        item.outTime.strftime('%H:%M'), "%H:%M")) >= (
                    datetime.strptime(attend.logoutTime.strftime('%H:%M'), "%H:%M") - datetime.strptime(
                        attend.loginTime.strftime('%H:%M'), "%H:%M"))):
                    status = 'Punctual'
                else:
                    status = 'Early Leaving'
            json_data.append([
                escape(i),
                '''<img class="imageTable zoom" src="{}" alt="" >'''.format(item.photo.thumbnail.url),
                escape(item.name),
                timing,
                loginPhoto,
                loginTime,
                loginRemark,
                logoutPhoto,
                logoutTime,
                logoutRemark,
                status,

            ])
            i = i + 1
        return json_data

class EmployeeListForAttendanceAdminBasicJson(BaseDatatableView):
    order_columns = ['id', 'photo', 'name', 'loginTime','loginPhoto'
                      'logoutTime', 'logoutPhoto']

    def get_initial_queryset(self):

        return Employee.objects.select_related().filter(isDeleted__exact=False)

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(name__icontains=search), isDeleted__exact=False)

        return qs

    def prepare_results(self, qs):
        json_data = []
        i = 1
        sDate = self.request.GET.get('startDate')
        startDate = datetime.strptime(sDate, '%d/%m/%Y')

        for item in qs:
            try:
                attend = EmployeeAttendance.objects.select_related().get(employeeID__id=item.pk,
                                                                         attendanceDate__icontains=startDate.date())
            except:
                attend = EmployeeAttendance()
                attend.employeeID_id = item.pk
                attend.attendanceDate = startDate.date()
                attend.save()


            if attend.loginTime is None:
                loginTime = 'N/A'

            else:
                loginTime = '''<button type="button" class="btn btn-info">{}
                                    </button>   '''.format(attend.loginTime.strftime('%I:%M %p'))


            if attend.logoutTime is None:
                logoutTime = 'N/A'

            else:

                logoutTime = '''<button type="button" class="btn btn-info">{}
                                    </button>'''.format(attend.logoutTime.strftime('%I:%M %p'))

            if not attend.loginPhoto:
                loginPhoto = 'N/A'
            else:
                loginPhoto = '''<img class="imageTable zoom" src="{}" alt="" >'''.format(attend.loginPhoto.thumbnail.url),

            if not attend.logoutPhoto:
                logoutPhoto = 'N/A'
            else:
                logoutPhoto = '''<img class="imageTable zoom" src="{}" alt="" >'''.format(attend.logoutPhoto.thumbnail.url),

            json_data.append([
                escape(i),
                '''<img class="imageTable zoom" src="{}" alt="" >'''.format(item.photo.thumbnail.url),
                escape(item.name),

                loginTime,
                loginPhoto,
                logoutTime,
                logoutPhoto
            ])
            i = i + 1
        return json_data



@check_group('System')
def attendance(request):
    date = datetime.today().date()

    context = {
        'date': date
    }

    return render(request, 'attendance/attendance.html', context)


# @check_group('Both')
def attendanceReport(request):
    request.session['nav'] = 'atten3'
    date = datetime.today().now().strftime('%d/%m/%Y')
    users = Employee.objects.select_related().filter(isDeleted__exact=False).order_by('name')

    context = {
        'date': date,
        'users': users
    }

    return render(request, 'attendance/attendanceReport.html', context)


# @check_group('Both')
def loginSystem(request):
    request.session['nav'] = 'atten1'
    return render(request, 'attendance/loginStystem.html')


# @check_group('Both')
def manageEmployee(request):
    request.session['nav'] = 'atten2'
    return render(request, 'attendance/EmployeeList.html')


# @check_group('Both')
def addEmployee(request):
    request.session['nav'] = 'atten2'
    return render(request, 'attendance/addEmployee.html')


# @check_group('Both')
def edit_employee(request, id=None):
    request.session['nav'] = 'atten2'
    instance = get_object_or_404(Employee, pk=id)
    context = {
        'instance': instance,
    }
    return render(request, 'attendance/editEmployee.html', context)


# @check_group('Both')
def add_login_system_api(request):
    if request.method == 'POST':
        try:
            Sname = request.POST.get('Sname')
            Saddress = request.POST.get('Saddress')
            Spass = request.POST.get('Spass')

            sys = LoginSystem()
            sys.systemName = Sname
            sys.location = Saddress
            sys.password = Spass

            sCount = LoginSystem.objects.select_related().count()
            username = 'SYSTEM' + str(sCount + 1)
            new_user = User()
            new_user.username = username
            new_user.set_password(Spass)

            new_user.save()
            sys.username = username
            sys.userID_id = new_user.pk

            try:
                g = Group.objects.select_related().get(name='System')
                g.user_set.add(new_user.pk)
                g.save()
            except:
                g = Group()
                g.name = "System"
                g.save()
                g.user_set.add(new_user.pk)
                g.save()

            sys.save()
            messages.success(request, 'New System added successfully.')

            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        except:
            messages.success(request, 'Error. Please try again.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# @check_group('Both')
def edit_login_system_api(request):
    if request.method == 'POST':
        try:
            id = request.POST.get('ESID')
            Sname = request.POST.get('ESname')
            Saddress = request.POST.get('ESaddress')
            Spass = request.POST.get('ESpass')

            sys = LoginSystem.objects.select_related().get(pk=int(id))
            sys.systemName = Sname
            sys.location = Saddress
            sys.password = Spass
            new_user = User.objects.select_related().get(pk=sys.userID_id)

            new_user.set_password(Spass)
            new_user.save()
            sys.save()
            messages.success(request, 'System detail edited successfully.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        except:
            messages.success(request, 'Error. Please try again.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# @check_group('Both')
def add_employee_api(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            address = request.POST.get('address')
            phoneNumber = request.POST.get('phone')
            password = request.POST.get('password')
            inTime = request.POST.get('inTime')
            outTime = request.POST.get('outTime')
            photo = request.FILES['photo']

            emp = Employee()
            emp.name = name
            emp.phoneNumber = phoneNumber
            emp.address = address
            emp.password = password
            in_time = datetime.strptime(inTime, "%I:%M %p")
            out_time = datetime.strptime(outTime, "%I:%M %p")

            emp.inTime = datetime.strftime(in_time, "%H:%M")
            emp.outTime = datetime.strftime(out_time, "%H:%M")
            emp.photo = photo

            emp.save()
            messages.success(request, 'Employee added successfully.')

            return redirect('/attendance/manageEmployee/')

        except:
            messages.success(request, 'Error. Please try again.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# @check_group('Both')
def edit_employee_api(request):
    if request.method == 'POST':
        try:
            empID = request.POST.get('empID')
            name = request.POST.get('name')
            address = request.POST.get('address')
            phoneNumber = request.POST.get('phone')
            password = request.POST.get('password')
            inTime = request.POST.get('inTime')
            outTime = request.POST.get('outTime')

            emp = Employee.objects.select_related().get(pk=int(empID))
            emp.name = name
            emp.phoneNumber = phoneNumber
            emp.address = address
            emp.password = password

            in_time = datetime.strptime(inTime, "%I:%M %p")
            out_time = datetime.strptime(outTime, "%I:%M %p")

            emp.inTime = datetime.strftime(in_time, "%H:%M")
            emp.outTime = datetime.strftime(out_time, "%H:%M")

            emp.save()
            messages.success(request, 'Employee detail edited successfully.')

            return redirect('/attendance/manageEmployee/')

        except:
            messages.success(request, 'Error. Please try again.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# @check_group('Both')
@csrf_exempt
def edit_employee_photo_api(request):
    if request.method == 'POST':
        userID = request.POST.get('empID')
        photo = request.FILES['file']
        try:
            staff = Employee.objects.select_related().get(pk=int(userID))
            staff.photo = photo
            staff.save()
            return JsonResponse({'response': 'ok'}, safe=False)
        except:

            return JsonResponse({'response': 'error'}, safe=False)


# @check_group('Both')
@csrf_exempt
def delete_employee_api(request):
    if request.method == 'POST':
        try:
            userID = request.POST.get('userID')
            staff = Employee.objects.select_related().get(pk=int(userID))
            staff.isDeleted = True

            staff.save()
            messages.success(request, 'Employee detail deleted successfully.')

            return redirect('/attendance/manageEmployee/')

        except:
            messages.success(request, 'Error. Please try again.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@csrf_exempt
def login_post_api(request):
    if request.method == 'POST':
        try:
            loginEmpID = request.POST.get('loginEmpID')
            loginPassword = request.POST.get('loginPassword')
            loginRemark = request.POST.get('loginRemark')
            photo = request.POST.get('photo')
            attend = EmployeeAttendance.objects.select_related().get(employeeID_id=int(loginEmpID),
                                                                     attendanceDate=datetime.today().date(),
                                                                     employeeID__password__exact=loginPassword)
            attend.loginTime = datetime.now().time()
            attend.loginRemark = loginRemark
            attend.loginSystemID_id = request.user.pk

            format, imgstr = photo.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='{}/temp.'.format(datetime.today().date()) + ext)  # You can save this as file instance
            attend.loginPhoto = data
            attend.save()

            return JsonResponse({'response': 'ok'}, safe=False)

        except:
            return JsonResponse({'response': 'error'}, safe=False)


@csrf_exempt
def logout_post_api(request):
    if request.method == 'POST':
        try:
            logoutEmpID = request.POST.get('logoutEmpID')
            logoutPassword = request.POST.get('logoutPassword')
            logoutRemark = request.POST.get('logoutRemark')
            photo = request.POST.get('photo')
            attend = EmployeeAttendance.objects.select_related().get(employeeID_id=int(logoutEmpID),
                                                                     attendanceDate=datetime.today().date(),
                                                                     employeeID__password__exact=logoutPassword)
            attend.logoutTime = datetime.now().time()
            attend.logoutRemark = logoutRemark

            format, imgstr = photo.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='{}/temp.'.format(datetime.today().date()) + ext)  # You can save this as file instance
            attend.logoutPhoto = data
            attend.logoutSystemID_id = request.user.pk
            attend.save()

            return JsonResponse({'response': 'ok'}, safe=False)

        except:
            return JsonResponse({'response': 'error'}, safe=False)

day_name= ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday','Sunday']
import  calendar
def genereate_attendence_report(request):
    sDate = request.GET.get('startDate')
    eDate = request.GET.get('endDate')
    staff = request.GET.get('staff')
    startDate = datetime.strptime(sDate, '%d/%m/%Y')
    endDate = datetime.strptime(eDate, '%d/%m/%Y')
    delta = endDate - startDate
    today = datetime.today().date()
    dates = [str(startDate.date()), str(endDate.date())]
    start, end = [datetime.strptime(_, "%Y-%m-%d") for _ in dates]

    if start == end:
        start = start+ timedelta(days=-1)
    x= OrderedDict(((start + timedelta(_)).strftime(r"%Y-%m"), None) for _ in range((end - start).days)).keys()
    if staff == 'all':
        data = []

        for d in list(x):

            qs = Employee.objects.select_related().filter(isDeleted__exact=False)
            emp_list = []
            for e in qs:

                p_count =0
                a_count =0
                na_count = 0
                hd_count = 0
                att = []
                for i in range(1, calendar.monthrange(start.year, start.month)[1]+1):

                    if i < 10:
                        i = "0{}".format(i)
                        day = datetime.strptime(d + "-{}".format(i), '%Y-%m-%d').weekday()

                        try:
                            attend = EmployeeAttendance.objects.select_related().get(employeeID__id=e.pk,
                                                                                     attendanceDate__icontains=d + "-{}".format(
                                                                                         i))

                            if attend.loginTime is None and attend.logoutTime is None:
                                if day_name[day] == 'Sunday':
                                    att.append('H')
                                    na_count = na_count + 1
                                else:
                                    att.append('A')
                                    a_count = a_count + 1
                            elif attend.loginTime is not None and attend.logoutTime is None:
                                att.append('HD')
                                hd_count = hd_count + 1
                            else:
                                if attend.logoutTime.strftime("%H:%M:%S") < "16:00:00":
                                    att.append('HD')
                                    hd_count = hd_count + 1
                                else:
                                    att.append('P')
                                    p_count = p_count + 1
                        except:
                            att.append('H')
                            na_count = na_count +1
                    else:
                        day = datetime.strptime(d + "-{}".format(i), '%Y-%m-%d').weekday()

                        try:
                            attend = EmployeeAttendance.objects.select_related().get(employeeID__id=e.pk,
                                                                                     attendanceDate__icontains=d + "-{}".format(
                                                                                         i))

                            if attend.loginTime is None and attend.logoutTime is None:
                                if day_name[day] == 'Sunday':
                                    att.append('H')
                                    na_count = na_count + 1
                                else:
                                    att.append('A')
                                    a_count = a_count + 1

                            elif attend.loginTime is not None and attend.logoutTime is None:

                                att.append('HD')
                                hd_count = hd_count + 1

                            else:
                                if attend.logoutTime.strftime("%H:%M:%S") < "16:00:00":
                                    att.append('HD')
                                    hd_count = hd_count + 1
                                else:
                                    att.append('P')
                                    p_count = p_count + 1
                        except:
                            att.append('H')
                            na_count = na_count + 1


                emp_dic = {
                    'Name': e.name,
                    'attendance': att,
                    'A': a_count,
                    'P': p_count,
                    'NA': na_count,
                    'HD': hd_count

                }
                emp_list.append(emp_dic)
            data_dic = {
                'month':d,
                'emp':emp_list

            }
            data.append(data_dic)


        context = {
            'data': data,
            'report': 1,
            'today': today,
            'days': range(0,calendar.monthrange(start.year, start.month)[1])

        }

        response = HttpResponse(content_type="application/pdf")
        response['Content-Disposition'] = "report.pdf"
        html = render_to_string("attendance/attendancePDFreport.html", context)

        HTML(string=html).write_pdf(response, stylesheets=[CSS(string='@page { size: A4 landscape; margin: .3cm ; }')])
        return response

    else:
        data = []

        for d in list(x):

            qs = Employee.objects.select_related().filter(isDeleted__exact=False, pk=int(staff))
            emp_list = []
            for e in qs:

                p_count = 0
                a_count = 0
                na_count = 0
                hd_count = 0
                att = []
                for i in  range(1, calendar.monthrange(start.year, start.month)[1]+1):
                    if i < 10:
                        i = "0{}".format(i)
                        day = datetime.strptime(d + "-{}".format(i), '%Y-%m-%d').weekday()

                    try:

                        attend = EmployeeAttendance.objects.select_related().get(employeeID__id=e.pk,
                                                                                 attendanceDate__icontains=d + "-{}".format(
                                                                                     i))

                        if attend.loginTime is None and attend.logoutTime is None:

                            if day_name[day] == 'Sunday':
                                att.append('H')
                                na_count = na_count + 1
                            else:
                                att.append('A')
                                a_count = a_count + 1
                        elif attend.loginTime is not None and attend.logoutTime is None:

                            att.append('HD')
                            hd_count = hd_count + 1

                        else:
                            if attend.logoutTime.strftime("%H:%M:%S") < "16:00:00":
                                att.append('HD')
                                hd_count = hd_count + 1
                            else:
                                att.append('P')
                                p_count = p_count + 1
                    except:
                        att.append('H')
                        na_count = na_count + 1

                emp_dic = {
                    'Name': e.name,
                    'attendance': att,
                    'A': a_count,
                    'P': p_count,
                    'NA': na_count,
                    'HD': hd_count

                }
                emp_list.append(emp_dic)
            data_dic = {
                'month': d,
                'emp': emp_list

            }
            data.append(data_dic)

        context = {
            'data': data,
            'report': 1,
            'today': today,
            'days':range(0,calendar.monthrange(start.year, start.month)[1])

        }

        response = HttpResponse(content_type="application/pdf")
        response['Content-Disposition'] = "report.pdf"
        html = render_to_string("attendance/attendancePDFreport.html", context)

        HTML(string=html).write_pdf(response, stylesheets=[CSS(string='@page { size: A4 landscape; margin: .3cm ; }')])
        return response


def demoReport(request):
    return render(request, 'attendance/attendancePDFreport.html')
