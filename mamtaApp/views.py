import json
from functools import wraps

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.db.models import Q, Sum
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime, timedelta

from django.template.defaultfilters import register
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt

from .models import *

from django_datatables_view.base_datatable_view import BaseDatatableView
from django.utils.html import escape

import urllib.request
import urllib.parse


def Balance():
    data = urllib.parse.urlencode({'apikey': 'zqc9vE5iO0U-jhurpShYlOIPyuJp1UZH6ZlFux7Kir'})
    data = data.encode('utf-8')
    request = urllib.request.Request("https://api.textlocal.in/balance/?")
    f = urllib.request.urlopen(request, data)
    fr = f.read()
    return (fr)





@register.filter('has_group')
def has_group(user, group_name):
    """
    Verifica se este usuário pertence a um grupo
    """
    groups = user.groups.all().values_list('name', flat=True)
    return True if group_name in groups else False


def check_group(group_name):
    def _check_group(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.groups.filter(name=group_name).exists():
                return redirect('/login/')
            return view_func(request, *args, **kwargs)

        return wrapper

    return _check_group


class BuyerListJson(BaseDatatableView):
    order_columns = ['id', 'name', 'phoneNumber', 'closingBalance', 'address', ]

    def get_initial_queryset(self):

        return Buyer.objects.filter(isDeleted__exact=False)

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(phoneNumber__icontains=search) | Q(closingBalance__icontains=search) | Q(name__icontains=search) | Q(
                    address__icontains=search), isDeleted__exact=False).order_by('-name')

        return qs

    def prepare_results(self, qs):
        json_data = []
        i = 1
        for item in qs:
            if 'Moderator' in self.request.user.groups.values_list('name',flat=True):
                action = '''<span><a href="/buyers/detail/{}"> <button style="background-color: #f77b3a;color: white;" type="button"
            class="btn  waves-effect ">
        <i class="material-icons">remove_red_eye</i></button> </a>

                </span>'''.format(item.pk)
            else:
                action = '''<span><a href="/buyers/detail/{}"> <button style="background-color: #f77b3a;color: white;" type="button"
                           class="btn  waves-effect ">
                       <i class="material-icons">remove_red_eye</i></button> </a>
    
                                   <a class="hideModerator" href="/buyers/edit/{}/"><button style="background-color: #3F51B5;color: white;" type="button"
                           class="btn  waves-effect " data-toggle="modal"
                           data-target="#largeModalEdit">
                       <i class="material-icons">border_color</i></button> </a>
    
    
    
                   <button onclick="getBuyerID('{}')" style="background-color: #e91e63;color: white;" type="button"
                           class="btn  waves-effect hideModerator " data-toggle="modal"
                           data-target="#defaultModal">
                       <i class="material-icons">delete</i></button></span>'''.format(item.pk, item.pk, item.pk)


            json_data.append([
                escape(i),
                escape(item.name),  # escape HTML for security reasons
                escape(item.phoneNumber),  # escape HTML for security reasons
                escape(item.closingBalance),
                escape(item.address),
                action
                ,

            ])
            i = i + 1
        return json_data


class ManageCreditListJson(BaseDatatableView):
    order_columns = ['id','buyerID.name', 'amount', 'remark', 'datetime']

    def get_initial_queryset(self):

        return MoneyToCollect.objects.all()

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(amount__icontains=search) | Q(remark__icontains=search) | Q(datetime__icontains=search)).order_by(
                '-name')

        return qs

    def prepare_results(self, qs):
        json_data = []
        i = 1
        for item in qs:
            json_data.append([
                escape(i),
                escape(item.buyerID.name),  # escape HTML for security reasons
                escape(item.amount),  # escape HTML for security reasons
                escape(item.remark),  # escape HTML for security reasons
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),

            ])
            i = i + 1
        return json_data


class CreditListJson(BaseDatatableView):
    order_columns = ['id', 'amount', 'remark', 'datetime']

    def get_initial_queryset(self):

        return MoneyToCollect.objects.filter(buyerID=int(self.request.GET.get('id')))

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(amount__icontains=search) | Q(remark__icontains=search) | Q(datetime__icontains=search)).order_by(
                '-name')

        return qs

    def prepare_results(self, qs):
        json_data = []
        i = 1
        for item in qs:
            json_data.append([
                escape(i),
                escape(item.amount),  # escape HTML for security reasons
                escape(item.remark),  # escape HTML for security reasons
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),

            ])
            i = i + 1
        return json_data



class DebitListJson(BaseDatatableView):
    order_columns = ['id', 'amount', 'collectedBy.name', 'paymentMode','remark', 'datetime', 'action']

    def get_initial_queryset(self):

        return MoneyCollection.objects.filter(buyerID=int(self.request.GET.get('id')))

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(amount__icontains=search) | Q(remark__icontains=search) | Q(datetime__icontains=search) | Q(
                    collectedBy__name__icontains=search)).order_by(
                '-id')

        return qs

    def prepare_results(self, qs):
        json_data = []
        i = 1
        for item in qs:
            btn = ''
            try:
                chequeImage = item.chequeImage.url
            except:
                chequeImage = 'N/A'

            if item.paymentMode == 'Cash':
                btn =  '''<button title="Location" onclick="getLocation('{}','{}')" style="background-color: #2de265;color: white;" type="button"
                           class="btn  waves-effect hideModerator " data-toggle="modal"
                           data-target="#defaultModalMap">
                       <i class="material-icons">map</i></button>'''.format(item.latitude, item.longitude)

            if item.paymentMode == 'Cheque':
                btn = '''
                 <button title="Cheque" onclick="getImage('{}')" style="background-color: #5b2982;color: white;" type="button"
                           class="btn  waves-effect hideModerator " data-toggle="modal"
                           data-target="#defaultModalImage">
                       <i class="material-icons">image</i></button>
                       <button title="Location" onclick="getLocation('{}','{}')" style="background-color: #2de265;color: white;" type="button"
                           class="btn  waves-effect hideModerator " data-toggle="modal"
                           data-target="#defaultModalMap">
                       <i class="material-icons">map</i></button>
                    
                '''.format(chequeImage, item.latitude, item.longitude)



            json_data.append([
                escape(i),
                escape(item.amount),  # escape HTML for security reasons
                escape(item.collectedBy.name),  # escape HTML for security reasons
                escape(item.paymentMode),  # escape HTML for security reasons
                escape(item.remark),  # escape HTML for security reasons
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),
                btn,

            ])
            i = i + 1
        return json_data


class CollectionListCashJson(BaseDatatableView):
    order_columns = ['id', 'buyerID.name', 'amount', 'collectedBy.name', 'remark', 'datetime','action']

    def get_initial_queryset(self):

        sDate = self.request.GET.get('startDate')
        eDate = self.request.GET.get('endDate')
        staff = self.request.GET.get('staff')
        startDate = datetime.strptime(sDate, '%d/%m/%Y')
        endDate = datetime.strptime(eDate, '%d/%m/%Y')
        if staff == 'all':
            return MoneyCollection.objects.filter(datetime__gte=startDate, datetime__lte=endDate + timedelta(days=1), paymentMode__exact='Cash')
        else:
            return MoneyCollection.objects.filter(datetime__gte=startDate, datetime__lte=endDate + timedelta(days=1), paymentMode__exact='Cash',
                                                  collectedBy=int(staff))

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(amount__icontains=search) | Q(remark__icontains=search) | Q(datetime__icontains=search) | Q(
                    collectedBy__name__icontains=search)).order_by(
                '-id')

        return qs

    def prepare_results(self, qs):
        json_data = []
        i = 1
        for item in qs:

            if item.collectedBy is None:
                createdBy = 'Admin'
            else:
                createdBy = item.collectedBy.name
            json_data.append([
                escape(i),
                escape(item.buyerID.name),
                escape(item.amount),  # escape HTML for security reasons
                createdBy,  # escape HTML for security reasons
                escape(item.remark),  # escape HTML for security reasons
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),
                '''<button title="Location" onclick="getLocation('{}','{}')" style="background-color: #2de265;color: white;" type="button"
                           class="btn  waves-effect hideModerator " data-toggle="modal"
                           data-target="#defaultModalMap">
                       <i class="material-icons">map</i></button>'''.format(item.latitude, item.longitude)

            ])
            i = i + 1
        return json_data

class CollectionListChequeJson(BaseDatatableView):
    order_columns = ['id', 'buyerID.name', 'amount', 'collectedBy.name', 'remark', 'datetime','action']

    def get_initial_queryset(self):

        sDate = self.request.GET.get('startDate')
        eDate = self.request.GET.get('endDate')
        staff = self.request.GET.get('staff')
        startDate = datetime.strptime(sDate, '%d/%m/%Y')
        endDate = datetime.strptime(eDate, '%d/%m/%Y')
        if staff == 'all':
            return MoneyCollection.objects.filter(datetime__gte=startDate, datetime__lte=endDate + timedelta(days=1), paymentMode__exact='Cheque')
        else:
            return MoneyCollection.objects.filter(datetime__gte=startDate, datetime__lte=endDate + timedelta(days=1), paymentMode__exact='Cheque',
                                                  collectedBy=int(staff))

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(amount__icontains=search) | Q(remark__icontains=search) | Q(datetime__icontains=search) | Q(
                    collectedBy__name__icontains=search)).order_by(
                '-id')

        return qs

    def prepare_results(self, qs):
        json_data = []
        i = 1
        for item in qs:
            try:
                chequeImage = item.chequeImage.url
            except:
                chequeImage = 'N/A'

            if item.collectedBy is None:
                createdBy = 'Admin'
            else:
                createdBy = item.collectedBy.name
            json_data.append([
                escape(i),
                escape(item.buyerID.name),
                escape(item.amount),  # escape HTML for security reasons
                createdBy,  # escape HTML for security reasons
                escape(item.remark),  # escape HTML for security reasons
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),
                '''
                 <button title="Cheque" onclick="getImage('{}')" style="background-color: #5b2982;color: white;" type="button"
                           class="btn  waves-effect hideModerator " data-toggle="modal"
                           data-target="#defaultModal">
                       <i class="material-icons">image</i></button>
                       <button title="Location" onclick="getLocation('{}','{}')" style="background-color: #2de265;color: white;" type="button"
                           class="btn  waves-effect hideModerator " data-toggle="modal"
                           data-target="#defaultModalMap">
                       <i class="material-icons">map</i></button>
                    
                '''.format(chequeImage, item.latitude, item.longitude)

            ])
            i = i + 1
        return json_data


class ManageCompanyListJson(BaseDatatableView):
    order_columns = ['id','name', 'phoneNumber', 'address', 'datetime']

    def get_initial_queryset(self):

        return Company.objects.filter(isDeleted__exact=False)

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(name__icontains=search) | Q(phoneNumber__icontains=search) |  Q(address__icontains=search) |
                Q(datetime__icontains=search)).order_by('-name')

        return qs

    def prepare_results(self, qs):
        json_data = []
        i = 1
        for item in qs:
            if 'Moderator' in self.request.user.groups.values_list('name', flat=True):
                action = '''N/A'''
            else:
                action = '''<span><a class="hideModerator" data-toggle="modal" data-target="#defaultModalEdit" onclick="editCompany('{}','{}','{}','{}')"><button style="background-color: #3F51B5;color: white;" type="button"
                               class="btn  waves-effect " data-toggle="modal"
                               data-target="#largeModalEdit">
                           <i class="material-icons">border_color</i></button> </a></span>'''.format(item.pk, item.name, item.phoneNumber, item.address)

            json_data.append([
                escape(i),
                escape(item.name),  # escape HTML for security reasons
                escape(item.phoneNumber),  # escape HTML for security reasons
                escape(item.address),  # escape HTML for security reasons
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),
                action,

            ])
            i = i + 1
        return json_data


class StaffListJson(BaseDatatableView):
    order_columns = ['id', 'photo', 'name', 'phoneNumber', 'companyID', 'staffTypeID','isActive','canTakePayment']

    def get_initial_queryset(self):

        return StaffUser.objects.filter(isDeleted__exact=False)

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(phoneNumber__icontains=search) |Q(name__icontains=search) | Q(address__icontains=search) | Q(companyID__name__icontains=search)
                | Q(staffTypeID__name__icontains=search), isDeleted__exact=False)

        return qs

    def prepare_results(self, qs):
        json_data = []
        i = 1
        for item in qs:
            if 'Moderator' in self.request.user.groups.values_list('name', flat=True):
                action = '''<span><a href="/staff/edit/{}"> <button style="background-color: #f77b3a;color: white;" type="button"
            class="btn  waves-effect ">
        <i class="material-icons">remove_red_eye</i></button> </a>

                </span>'''.format(item.pk)
            else:
                action = '''<span><a href="/staff/detail/{}"> <button style="background-color: #f77b3a;color: white;" type="button"
                           class="btn  waves-effect ">
                       <i class="material-icons">remove_red_eye</i></button> </a>

                                   <a class="hideModerator" href="/staff/edit/{}/"><button style="background-color: #3F51B5;color: white;" type="button"
                           class="btn  waves-effect " data-toggle="modal"
                           data-target="#largeModalEdit">
                       <i class="material-icons">border_color</i></button> </a>



                   <button onclick="getStaffID('{}')" style="background-color: #e91e63;color: white;" type="button" class="btn  waves-effect " data-toggle="modal" data-target="#defaultModal">
            
            
                                                    <i class="material-icons">delete</i></button></span>'''.format(item.pk, item.pk, item.pk)

            if item.isActive == True:
                active = 'Active'
            else:
                active = 'InActive'

            if item.canTakePayment == True:
                canTakePayment = 'Yes'
            else:
                canTakePayment = 'No'


            if item.companyID is None:
                company = 'N/A'
            else:
                company = item.companyID.name
            json_data.append([
                escape(i),
                '''<img class="imageTable zoom" src="{}" alt="">'''.format(item.photo.url),
                escape(item.name),  # escape HTML for security reasons
                escape(item.phoneNumber),  # escape HTML for security reasons
                company,
                escape(item.staffTypeID.name),
                active,
                canTakePayment,
                action,

            ])
            i = i + 1
        return json_data


class SupplierCollectionListJson(BaseDatatableView):
    order_columns = ['id', 'buyerID', 'amount', 'paymentMode', 'remark', 'datetime']

    def get_initial_queryset(self):
        return SupplierCollection.objects.filter(datetime__icontains=datetime.today().date(), collectedBy__userID_id=self.request.user.pk)


    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(paymentMode__icontains=search) |  Q(amount__icontains=search) | Q(remark__icontains=search) | Q(datetime__icontains=search) | Q(
                    buyerID__name__icontains=search))

        return qs

    def prepare_results(self, qs):
        json_data = []
        i = 1
        for item in qs:
            json_data.append([
                escape(i),
                escape(item.buyerID.name),
                escape(item.amount),  # escape HTML for security reasons
                escape(item.paymentMode),  # escape HTML for security reasons
                escape(item.remark),  # escape HTML for security reasons
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),

            ])
            i = i + 1
        return json_data


class SupplierCollectionListCashJson(BaseDatatableView):
    order_columns = ['id', 'buyerID.name', 'amount', 'collectedBy.name', 'remark', 'datetime','action']

    def get_initial_queryset(self):

        sDate = self.request.GET.get('startDate')
        eDate = self.request.GET.get('endDate')
        staff = self.request.GET.get('staff')
        startDate = datetime.strptime(sDate, '%d/%m/%Y')
        endDate = datetime.strptime(eDate, '%d/%m/%Y')
        if staff == 'all':
            return SupplierCollection.objects.filter(datetime__gte=startDate, datetime__lte=endDate + timedelta(days=1), paymentMode__exact='Cash')
        else:
            return SupplierCollection.objects.filter(datetime__gte=startDate, datetime__lte=endDate + timedelta(days=1), paymentMode__exact='Cash',
                                                  collectedBy=int(staff))

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(amount__icontains=search) | Q(remark__icontains=search) | Q(datetime__icontains=search) | Q(
                    collectedBy__name__icontains=search)| Q(
                    buyerID__name__icontains=search)).order_by(
                '-id')

        return qs

    def prepare_results(self, qs):
        json_data = []
        i = 1
        for item in qs:
            if item.isApproved == False:
                button = '''
                 <button type="button" class="btn btn-primary waves-effect" data-toggle="modal"
                           data-target="#defaultModal" onclick="approveCollection({})">PENDING</button>'''.format(item.pk)
            else:
                button = '''<button type="button" class="btn btn-success waves-effect">APPROVED</button>'''

            json_data.append([
                escape(i),
                escape(item.buyerID.name),
                escape(item.amount),  # escape HTML for security reasons
                escape(item.collectedBy.name),  # escape HTML for security reasons
                escape(item.remark),  # escape HTML for security reasons
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),
                button

            ])
            i = i + 1
        return json_data



class SupplierCollectionListChequeJson(BaseDatatableView):
    order_columns = ['id', 'buyerID.name', 'amount', 'collectedBy.name', 'remark', 'datetime','action']

    def get_initial_queryset(self):

        sDate = self.request.GET.get('startDate')
        eDate = self.request.GET.get('endDate')
        staff = self.request.GET.get('staff')
        startDate = datetime.strptime(sDate, '%d/%m/%Y')
        endDate = datetime.strptime(eDate, '%d/%m/%Y')
        if staff == 'all':
            return SupplierCollection.objects.filter(datetime__gte=startDate, datetime__lte=endDate + timedelta(days=1), paymentMode__exact='Cheque')
        else:
            return SupplierCollection.objects.filter(datetime__gte=startDate, datetime__lte=endDate + timedelta(days=1), paymentMode__exact='Cheque',
                                                  collectedBy=int(staff))

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(amount__icontains=search) | Q(remark__icontains=search) | Q(datetime__icontains=search) | Q(
                    collectedBy__name__icontains=search)| Q(
                    buyerID__name__icontains=search)).order_by(
                '-id')

        return qs

    def prepare_results(self, qs):
        json_data = []
        i = 1
        for item in qs:
            if item.isApproved == False:
                button = '''
                <button type="button" class="btn btn-primary waves-effect" data-toggle="modal"
                           data-target="#defaultModal" onclick="approveCollection({})">PENDING</button>'''.format(item.pk)
            else:
                button = '''<button type="button" class="btn btn-success waves-effect">APPROVED</button>'''

            json_data.append([
                escape(i),
                escape(item.buyerID.name),
                escape(item.amount),  # escape HTML for security reasons
                escape(item.collectedBy.name),  # escape HTML for security reasons
                escape(item.remark),  # escape HTML for security reasons
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),
                button

            ])
            i = i + 1
        return json_data



@check_group('Both')
def home(request):
    b = json.loads(Balance().decode('utf-8'))
    request.session['nav'] = '1'
    staff = StaffUser.objects.filter(isDeleted__exact=False).count()
    buyer = Buyer.objects.filter(isDeleted__exact=False).count()
    credit = MoneyCollection.objects.filter(datetime__icontains = datetime.today().date()).aggregate(Sum('amount'))
    due = Buyer.objects.aggregate(Sum('closingBalance'))
    date_list = []
    credit_list =[]
    for i in range(11):
        c = MoneyCollection.objects.filter(datetime__icontains=datetime.today().date() - timedelta(i)).aggregate(Sum('amount'))
        if c['amount__sum'] == None:
            credit_list.append(0)
        else:
            credit_list.append(c['amount__sum'])
        date_list.append(datetime.today().date() - timedelta(i))


    context ={
        'staff':staff,
        'buyer':buyer,
        'due':due['closingBalance__sum'],
        'credit':credit['amount__sum'],
        'dates':date_list[::-1],
        'c_list':credit_list[::-1],
        'sms':b['balance']['sms'],
    }

    return render(request, 'mamtaApp/index.html',context)


# --------------------------staffs -----------------------------------------------------------------
@check_group('Both')
def staff(request):
    request.session['nav'] = '2'
    users = StaffUser.objects.filter(isDeleted__exact=False).order_by('name')

    context = {
        'users': users
    }
    return render(request, 'mamtaApp/staffs.html', context)


@check_group('Both')
def add_staff(request):
    staffType = StaffType.objects.all()
    company = Company.objects.filter(isDeleted__exact=False)
    context = {
        'types':staffType,
        'company':company
    }
    return render(request, 'mamtaApp/addStaff.html',context)


@check_group('Both')
def detail_staff(request, id=None):
    instance = get_object_or_404(StaffUser, pk=id)
    context = {
        'instance': instance
    }
    return render(request, 'mamtaApp/staffDetail.html', context)


@check_group('Both')
def edit_staff(request, id=None):
    instance = get_object_or_404(StaffUser, pk=id)
    staffType = StaffType.objects.all()
    company = Company.objects.filter(isDeleted__exact=False)

    context = {
        'instance': instance,
        'types': staffType,
        'company':company
    }
    return render(request, 'mamtaApp/editStaff.html', context)


# -----------------------------staff user api ------------------------------------------------
@check_group('Both')
def add_staff_user_api(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            address = request.POST.get('address')
            phoneNumber = request.POST.get('phone')
            staffType = request.POST.get('staffType')
            companyID = request.POST.get('companyID')
            photo = request.FILES['photo']
            idProof = request.FILES['idProof']

            staff = StaffUser()
            staff.name = name
            staff.phoneNumber = phoneNumber
            staff.address = address
            staff.staffTypeID_id = int(staffType)
            staff.photo = photo
            staff.idProof = idProof
            staff.companyID_id = int(companyID)

            username = 'MAMTA' + get_random_string(length=4, allowed_chars='1234567890')
            while User.objects.filter(username__exact=username).count() > 0:
                username = 'MAMTA' + get_random_string(length=4, allowed_chars='1234567890')
            else:
                password = get_random_string(length=10, allowed_chars='1234567890')
                new_user = User()
                new_user.username = username
                new_user.set_password(password)

                new_user.save()
                staff.username = username
                staff.password = password
                staff.userID_id = new_user.pk
            if staffType == '1':
                try:
                    g = Group.objects.get(name='Staff')
                    g.user_set.add(new_user.pk)
                    g.save()
                    h = Group.objects.get(name='Collection')
                    h.user_set.add(new_user.pk)
                    h.save()
                except:
                    g = Group()
                    g.name = "Staff"
                    g.save()
                    g.user_set.add(new_user.pk)
                    g.save()
                    h = Group()
                    h.name = "Collection"
                    h.save()
                    h.user_set.add(new_user.pk)
                    h.save()
            elif staffType =='2':
                try:
                    g = Group.objects.get(name='Staff')
                    g.user_set.add(new_user.pk)
                    g.save()
                    h = Group.objects.get(name='Sales')
                    h.user_set.add(new_user.pk)
                    h.save()

                except:
                    g = Group()
                    g.name = "Staff"
                    g.save()
                    g.user_set.add(new_user.pk)
                    g.save()
                    h = Group()
                    h.name = "Sales"
                    h.save()
                    h.user_set.add(new_user.pk)
                    h.save()
            elif staffType =='3':
                try:
                    h = Group.objects.get(name='Accountant')
                    h.user_set.add(new_user.pk)
                    h.save()

                except:
                    h = Group()
                    h.name = "Accountant"
                    h.save()
                    h.user_set.add(new_user.pk)
                    h.save()
            elif staffType =='4':
                try:
                    h = Group.objects.get(name='Supply')
                    h.user_set.add(new_user.pk)
                    h.save()

                except:
                    h = Group()
                    h.name = "Supply"
                    h.save()
                    h.user_set.add(new_user.pk)
                    h.save()
            else:
                try:
                    g = Group.objects.get(name='Staff')
                    g.user_set.add(new_user.pk)
                    g.save()
                    h = Group.objects.get(name='Normal')
                    h.user_set.add(new_user.pk)
                    h.save()
                except:
                    g = Group()
                    g.name = "Staff"
                    g.save()
                    g.user_set.add(new_user.pk)
                    g.save()
                    h = Group()
                    h.name = "Normal"
                    h.save()
                    h.user_set.add(new_user.pk)
                    h.save()


            staff.save()
            messages.success(request, 'Staff user added successfully.')

            return redirect('/staff/')

        except:
            messages.success(request, 'Error. Please try again.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@check_group('Both')
def edit_staff_user_api(request):
    if request.method == 'POST':
        try:
            userID = request.POST.get('staffID')
            name = request.POST.get('name')
            address = request.POST.get('address')
            phoneNumber = request.POST.get('phone')
            isActive = request.POST.get('isActive')
            companyID = request.POST.get('companyID')
            canTakePayment = request.POST.get('canTakePayment')
            staffType = request.POST.get('staffType')
            password = request.POST.get('pass')

            staff = StaffUser.objects.get(pk=int(userID))
            staff.name = name
            staff.phoneNumber = phoneNumber
            staff.address = address
            staff.isActive = isActive
            staff.staffTypeID_id = int(staffType)
            staff.canTakePayment = canTakePayment
            staff.companyID_id = int(companyID)
            staff.password = password
            user = User.objects.get(id = staff.userID_id)
            if isActive == 'True':
                user.is_active = True
            else:
                user.is_active = False
            if staffType == '1':
                new_user = User.objects.get(pk=staff.userID_id)
                new_user.groups.clear()
                new_user.save()
                g = Group.objects.get(name='Staff')
                g.user_set.add(new_user.pk)
                g.save()
                h = Group.objects.get(name='Collection')
                h.user_set.add(new_user.pk)
                h.save()
            elif staffType == '2':
                new_user = User.objects.get(pk=staff.userID_id)
                new_user.groups.clear()
                new_user.save()
                g = Group.objects.get(name='Staff')
                g.user_set.add(new_user.pk)
                g.save()
                h = Group.objects.get(name='Sales')
                h.user_set.add(new_user.pk)
                h.save()
            elif staffType == '3':
                new_user = User.objects.get(pk=staff.userID_id)
                new_user.groups.clear()
                new_user.save()
                h = Group.objects.get(name='Accountant')
                h.user_set.add(new_user.pk)
                h.save()
            elif staffType == '4':
                new_user = User.objects.get(pk=staff.userID_id)
                new_user.groups.clear()
                new_user.save()
                h = Group.objects.get(name='Supply')
                h.user_set.add(new_user.pk)
                h.save()
            else :
                new_user = User.objects.get(pk=staff.userID_id)
                new_user.groups.clear()
                new_user.save()
                g = Group.objects.get(name='Staff')
                g.user_set.add(new_user.pk)
                g.save()
                h = Group.objects.get(name='Normal')
                h.user_set.add(new_user.pk)
                h.save()
            user.set_password(password)
            user.save()
            staff.save()
            messages.success(request, 'Staff user detail edited successfully.')

            return redirect('/staff/')

        except:
            messages.success(request, 'Error. Please try again.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@check_group('Both')
@csrf_exempt
def edit_staff_photo_api(request):
    if request.method == 'POST':
        userID = request.POST.get('staffID')
        photo = request.FILES['file']
        try:
            staff = StaffUser.objects.get(pk=int(userID))
            staff.photo = photo
            staff.save()
            return JsonResponse({'response': 'ok'}, safe=False)
        except:

            return JsonResponse({'response': 'error'}, safe=False)


@check_group('Both')
@csrf_exempt
def edit_staff_idproof_api(request):
    if request.method == 'POST':
        try:
            userID = request.POST.get('staffID')
            photo = request.FILES['file']

            staff = StaffUser.objects.get(pk=int(userID))
            staff.idProof = photo
            staff.save()
            return JsonResponse({'response': 'ok'}, safe=False)
        except:

            return JsonResponse({'response': 'error'}, safe=False)


@check_group('Both')
@csrf_exempt
def delete_staff_user_api(request):
    if request.method == 'POST':
        try:
            userID = request.POST.get('userID')
            staff = StaffUser.objects.get(pk=int(userID))
            staff.isDeleted = True
            staff.isActive = False
            user = User.objects.get(id=staff.userID_id)
            user.is_active = False
            user.save()
            staff.save()
            messages.success(request, 'Staff user detail deleted successfully.')

            return redirect('/staff/')

        except:
            messages.success(request, 'Error. Please try again.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# ---------------------------------buyers---------------------------------------------
@check_group('Both')
def buyers(request):
    request.session['nav'] = '3'
    users = Buyer.objects.filter(isDeleted__exact=False).order_by('name')

    context = {
        'users': users
    }
    return render(request, 'mamtaApp/buyersList.html', context)


@check_group('Both')
def add_buyer(request):
    return render(request, 'mamtaApp/buyersAdd.html')


@check_group('Both')
def detail_buyer(request, id=None):
    instance = get_object_or_404(Buyer, id=id)

    context = {
        'instance': instance
    }
    return render(request, 'mamtaApp/buyerDetail.html', context)


@check_group('Both')
def edit_buyer(request, id=None):
    instance = get_object_or_404(Buyer, id=id)

    context = {
        'instance': instance
    }
    return render(request, 'mamtaApp/buyerEdit.html', context)


# --------------------------buyer APi-----------------------------
@check_group('Both')
def add_buyer_api(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            address = request.POST.get('address')
            phoneNumber = request.POST.get('phone')
            closingBalance = request.POST.get('balance')

            buyer = Buyer()
            buyer.name = name
            buyer.phoneNumber = phoneNumber
            buyer.address = address
            buyer.closingBalance = float(closingBalance)

            buyer.save()
            messages.success(request, 'New buyer added successfully.')

            return redirect('/buyers/')

        except:
            messages.success(request, 'Error. Please try again.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@check_group('Both')
def edit_buyer_api(request):
    if request.method == 'POST':
        try:
            buyerID = request.POST.get('buyerID')
            name = request.POST.get('name')
            address = request.POST.get('address')
            phoneNumber = request.POST.get('phone')
            closingBalance = request.POST.get('balance')

            buyer = Buyer.objects.get(pk=int(buyerID))
            buyer.name = name
            buyer.phoneNumber = phoneNumber
            buyer.address = address
            buyer.closingBalance = closingBalance
            buyer.save()
            messages.success(request, 'Buyer details edited successfully.')

            return redirect('/buyers/')

        except:
            messages.success(request, 'Error. Please try again.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@check_group('Both')
def delete_buyer_api(request):
    if request.method == 'POST':
        try:
            buyerID = request.POST.get('userID')
            buyer = Buyer.objects.get(pk=int(buyerID))
            buyer.isDeleted = True
            buyer.save()
            messages.success(request, 'Buyer detail deleted successfully.')

            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        except:
            messages.success(request, 'Error. Please try again.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# ------------------ money to collect(credit)--------------------
@check_group('Both')
def add_money_to_be_collected_api(request):
    if request.method == 'POST':
        try:
            buyerID = request.POST.get('buyerID')
            amount = request.POST.get('amount')
            remark = request.POST.get('remark')
            money = MoneyToCollect()
            money.buyerID_id = int(buyerID)
            money.amount = float(amount)
            if remark == '':
                money.remark = 'No Remark'
            else:
                money.remark = remark
            money.save()
            buyer = Buyer.objects.get(pk=int(buyerID))
            buyer.closingBalance = buyer.closingBalance + float(amount)
            buyer.save()
            messages.success(request, 'Buyer money credited successfully.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        except:
            messages.success(request, 'Error. Please try again.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@check_group('Both')
def edit_money_to_be_collected(request):
    if request.method == 'POST':
        try:
            moneyID = request.POST.get('moneyID')
            buyerID = request.POST.get('buyerID')
            amount = request.POST.get('amount')
            money = MoneyToCollect.objects.get(int(moneyID))
            previousMoney = money.amount
            money.amount = float(amount)
            money.save()
            buyer = Buyer.objects.get(pk=int(buyerID))
            buyer.closingBalance = (buyer.closingBalance - previousMoney) + float(amount)
            buyer.save()
            messages.success(request, 'Buyer money edited successfully.')
            return redirect('/Buyer/List/')

        except:
            messages.success(request, 'Error. Please try again.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@check_group('Both')
def delete_money_to_be_collected(request):
    if request.method == 'POST':
        try:
            moneyID = request.POST.get('moneyID')
            money = MoneyToCollect.objects.get(pk=int(moneyID))
            money.isDeleted = True
            money.save()
            buyer = Buyer.objects.get(pk=int(money.buyerID_id))
            buyer.closingBalance = (buyer.closingBalance - money.amount)
            buyer.save()
            messages.success(request, 'Buyer money detail deleted successfully.')
            return redirect('/User/List/')

        except:
            messages.success(request, 'Error. Please try again.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# -----------------report-------------------
@check_group('Both')
def report(request):
    request.session['nav'] = '5'
    users = StaffUser.objects.filter(isDeleted__exact=False).order_by('name')
    date = datetime.today().now().strftime('%d/%m/%Y')
    context = {
        'users': users,
        'date': date
    }
    return render(request, 'mamtaApp/report.html', context)


# -----------------report-------------------
@check_group('Both')
def manage_credits(request):
    request.session['nav'] = '4'
    users = Buyer.objects.filter(isDeleted__exact=False).order_by('name')
    context = {
        'users': users,
    }
    return render(request, 'mamtaApp/manageCredits.html', context)



# ------------------- login ---------------------------------
def loginApp(request):
    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if 'Sales' in request.user.groups.values_list('name', flat=True):

                return redirect('/invoice/')
            if 'Accountant' in request.user.groups.values_list('name', flat=True):
                return redirect('/invoice/collection_report_accountant/')
            if 'Both' in request.user.groups.values_list('name', flat=True):
                return redirect('/')

            if 'System' in request.user.groups.values_list('name', flat=True):
                return redirect('/attendance/attendance/')
            if 'Supply' in request.user.groups.values_list('name', flat=True):
                return redirect('/supplyHome/')

        else:
            messages.success(request, "Wrong Credential! Please try again.")

            return render(request, "mamtaApp/login.html", {})
    return render(request, 'mamtaApp/login.html')


def logout_user(request):
    request.session['nav'] = '7'
    logout(request)
    return redirect('/')


# -------------------profile--------------------------------------
@check_group('Both')
def profile(request):
    request.session['nav'] = '6'

    return render(request, 'mamtaApp/Profile.html')



# -------------------change Password--------------------------------------

@check_group('Both')
def change_password_api(request):
    if request.method == 'POST':
        try:
            password = request.POST.get('password')
            data = Admin.objects.get(userID_id=request.user.pk)
            data.password = password
            data.save()
            user = User.objects.get(pk=request.user.pk)
            user.set_password(password)
            user.save()
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Password changed successfully.")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            messages.success(request, "Password changed successfully.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        except:
            messages.success(request, "Error while changing password.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# -----------------company-------------------
@check_group('Both')
def manage_company(request):
    request.session['nav'] = 'company1'
    users = Buyer.objects.filter(isDeleted__exact=False).order_by('name')
    context = {
        'users': users,
    }
    return render(request, 'mamtaApp/manageCompany.html', context)


@check_group('Both')
def add_company_api(request):
    if request.method == 'POST':
        try:
            Cname = request.POST.get('Cname')
            Cphone = request.POST.get('Cphone')
            Caddress = request.POST.get('Caddress')
            try:
                comp = Company.objects.get(name__iexact=Cname)
                messages.success(request, 'Company name already exist. Please try again with again with different name.')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            except:
                comp = Company()
                comp.name = Cname
                comp.phoneNumber = Cphone
                comp.address = Caddress

                comp.save()
                messages.success(request, 'New company added successfully.')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        except:
            messages.success(request, 'Error. Please try again.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))\


@check_group('Both')
def edit_company_api(request):
    if request.method == 'POST':
        # try:
            ECID = request.POST.get('ECID')
            ECname = request.POST.get('ECname')
            ECphone = request.POST.get('ECphone')
            ECaddress = request.POST.get('ECaddress')
            # comp = Company.objects.all().exclude(pk = int(ECID))
            try:
                comp = Company.objects.exclude(pk = int(ECID)).get(name__iexact=ECname)
                messages.success(request, 'Company name already exist. Please try again with again with different name.')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            except:

                obj = Company.objects.get(pk = int(ECID))
                obj.name = ECname
                obj.phoneNumber = ECphone
                obj.address = ECaddress

                obj.save()
                messages.success(request, 'Company details updated successfully.')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        # except:
        #     messages.success(request, 'Error. Please try again.')
        #     return HttpResponseRedirect(request.META.get('HTTP_REFERER'))



# -------------------profile--------------------------------------
@check_group('Supply')
def supply_home(request):
    request.session['nav'] = '8'

    user = StaffUser.objects.get(userID_id=request.user.pk)

    context = {
        'user':user
    }

    return render(request, 'mamtaApp/supply/supplyIndex.html', context)

@csrf_exempt
def take_collection_supplier_api(request):
    if request.method == 'POST':

        CustomerCol = request.POST.get('CustomerCol')
        AmountCol = request.POST.get('AmountCol')
        PayMethodCol = request.POST.get('PayMethodCol')
        RemarkCol = request.POST.get('RemarkCol')

        try:
            collection = SupplierCollection()
            collection.buyerID_id = int(CustomerCol)
            collection.amount = float(AmountCol)
            user = StaffUser.objects.get(userID_id=request.user.pk)
            collection.collectedBy_id = user.pk
            collection.paymentMode = PayMethodCol
            collection.remark = RemarkCol
            collection.companyID_id = user.companyID_id
            collection.save()

            return JsonResponse({'message': 'success'})

        except:
            return JsonResponse({'message': 'fail'})


@check_group('Both')
def supplier_collection_report(request):
    request.session['nav'] = '55'
    users = StaffUser.objects.filter(isDeleted__exact=False).order_by('name')
    date = datetime.today().now().strftime('%d/%m/%Y')
    context = {
        'users': users,
        'date': date
    }
    return render(request, 'mamtaApp/supply/SupplierCollectionReport.html', context)


@csrf_exempt
def approve_collection_supplier_api(request):
    if request.method == 'POST':

        collectionID = request.POST.get('collectionID')


        try:
            collection = SupplierCollection.objects.get(pk = int(collectionID))
            collection.isApproved = True

            collection.save()
            buy = Buyer.objects.get(pk=int(collection.buyerID.pk))
            buy.closingBalance = buy.closingBalance - float(collection.amount)
            buy.save()
            return JsonResponse({'message': 'success'})

        except:
            return JsonResponse({'message': 'fail'})