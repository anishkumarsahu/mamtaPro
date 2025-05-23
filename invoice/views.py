import calendar
import functools
from datetime import datetime, timedelta, date

from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.html import escape
from django.views.decorators.csrf import csrf_exempt
from django_datatables_view.base_datatable_view import BaseDatatableView
from weasyprint import HTML, CSS

from mamtaApp.views import check_group
from .models import *
from django.core.cache import cache
# Create your views here.

last_3_month_date = datetime.today().date() - timedelta(days=45)


def enable_opening_balance(request):
    try:
        try:
            user = StaffUser.objects.select_related().get(userID_id=request.user.pk)
            ex = OpeningAndClosingBalance.objects.select_related().get(isBalanceCreditedOnNextDay=False,
                                                                       balanceDate__lt=datetime.today().date()
                                                                       , companyID_id=user.companyID_id)

            ex.isBalanceCreditedOnNextDay = True
            ex.balanceCreditDate = datetime.today().date()
            ex.save()

            n = OpeningAndClosingBalance()
            n.openingAmount = ex.closingAmount
            n.createdBy_id = user.pk
            n.balanceDate = datetime.today().date()
            n.companyID_id = user.companyID_id
            n.save()
        except:
            ex = OpeningAndClosingBalance.objects.select_related().get(isBalanceCreditedOnNextDay=False,
                                                                       balanceDate__lt=datetime.today().date(),
                                                                       companyID_id=1)

            ex.isBalanceCreditedOnNextDay = True
            ex.balanceCreditDate = datetime.today().date()
            ex.save()

            n = OpeningAndClosingBalance()
            n.openingAmount = ex.closingAmount
            n.balanceDate = datetime.today().date()
            n.companyID_id = 1
            n.save()
    except:
        pass


class InvoiceSeriesListJson(BaseDatatableView):
    order_columns = ['id', 'series', 'companyID']

    def get_initial_queryset(self):

        return InvoiceSeries.objects.select_related().filter(isDeleted__exact=False)

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(series__icontains=search), Q(companyID__name__icontains=search), isDeleted__exact=False).order_by(
                '-name')

        return qs

    def prepare_results(self, qs):
        json_data = []
        i = 1
        for item in qs:
            if 'Moderator' in self.request.user.groups.values_list('name', flat=True):
                action = '''<span><a > <button style="background-color: #f77b3a;color: white;" type="button"
            class="btn  waves-effect ">
        <i class="material-icons">remove_red_eye</i></button> </a>

                </span>'''.format(item.pk)
            else:
                action = '''<span> <a onclick="getDetail('{}','{}','{}')" data-toggle="modal"
                           data-target="#defaultModalEdit"><button style="background-color: #3F51B5;color: white;" type="button"
                           class="btn  waves-effect " data-toggle="modal"
                           data-target="#largeModalEdit">
                       <i class="material-icons">border_color</i></button> </a>


                       
                       </span>'''.format(item.pk, item.series, item.pk)

            if item.companyID is None:
                company = 'N/A'
            else:
                company = item.companyID.name
            json_data.append([
                escape(i),
                escape(item.series),  # escape HTML for security reasons
                company,
                # escape(item.assignedTo.name),  # escape HTML for security reasons
                # action,

            ])
            i = i + 1
        return json_data


class InvoiceCreatedByCashListJson(BaseDatatableView):
    order_columns = ['id', 'billNumber', 'amount', 'salesType', 'InvoiceSeriesID', 'createdBy', 'datetime', 'action']

    def get_initial_queryset(self):

        sDate = self.request.GET.get('startDate')
        eDate = self.request.GET.get('endDate')
        staff = self.request.GET.get('staff')
        startDate = datetime.strptime(sDate, '%d/%m/%Y')
        endDate = datetime.strptime(eDate, '%d/%m/%Y')
        if staff == 'all':
            return Sales.objects.select_related().filter(datetime__gte=startDate,
                                                         datetime__lte=endDate + timedelta(days=1),
                                                         salesType__exact='Cash', ).exclude(
                datetime__lt=last_3_month_date)
        else:
            return Sales.objects.select_related().filter(datetime__gte=startDate,
                                                         datetime__lte=endDate + timedelta(days=1),
                                                         salesType__exact='Cash',
                                                         createdBy=int(staff)).exclude(datetime__lt=last_3_month_date)

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(InvoiceSeriesID__companyID__name__icontains=search) | Q(amount__icontains=search) | Q(
                    billNumber__icontains=search) | Q(datetime__icontains=search) | Q(
                    createdBy__name__icontains=search)).order_by(
                '-id')

        return qs

    def prepare_results(self, qs):
        json_data = []
        i = 1
        for item in qs:

            if 'Moderator' in self.request.user.groups.values_list('name', flat=True):
                action = '''<span>N/A</span>'''.format(item.pk)
            elif 'Accountant' in self.request.user.groups.values_list('name', flat=True):
                action = '''<span> <a onclick="getDetail('{}','{}','{}','{}','{}')" data-toggle="modal"
                               data-target="#defaultModalInvoiceEdit"><button style="background-color: #3F51B5;color: white;" type="button"
                               class="btn  waves-effect " data-toggle="modal"
                               data-target="#largeModalEdit">
                           <i class="material-icons">border_color</i></button> </a></span>'''.format(item.pk, item.billNumber,
                                                                                          item.salesType, item.amount,
                                                                                          item.remark,)
            else:
                action = '''<span> <a onclick="getDetail('{}','{}','{}','{}','{}')" data-toggle="modal"
                               data-target="#defaultModalInvoiceEdit"><button style="background-color: #3F51B5;color: white;" type="button"
                               class="btn  waves-effect " data-toggle="modal"
                               data-target="#largeModalEdit">
                           <i class="material-icons">border_color</i></button> </a>



                       <button onclick="deleteSale('{}')" style="background-color: #e91e63;color: white;" type="button" class="btn  waves-effect hideModerator " data-toggle="modal"
                               data-target="#defaultModal">
                           <i class="material-icons">delete</i></button></span>'''.format(item.pk, item.billNumber,
                                                                                          item.salesType, item.amount,
                                                                                          item.customerName, item.pk)

            if item.InvoiceSeriesID.companyID is None:
                company = 'N/A'
            else:
                company = item.InvoiceSeriesID.companyID.name

            if item.createdBy is None:
                createdBy = 'Admin'
            else:
                createdBy = item.createdBy.name
            json_data.append([
                escape(i),
                escape(item.billNumber),
                escape(item.amount),  # escape HTML for security reasons
                escape(item.salesType),  # escape HTML for security reasons
                company,  # escape HTML for security reasons
                createdBy,  # escape HTML for security reasons
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),
                action

            ])
            i = i + 1
        return json_data


class InvoiceCreatedByCardListJson(BaseDatatableView):
    order_columns = ['id', 'billNumber', 'amount', 'salesType', 'InvoiceSeriesID', 'createdBy', 'datetime', 'action']

    def get_initial_queryset(self):

        sDate = self.request.GET.get('startDate')
        eDate = self.request.GET.get('endDate')
        staff = self.request.GET.get('staff')
        startDate = datetime.strptime(sDate, '%d/%m/%Y')
        endDate = datetime.strptime(eDate, '%d/%m/%Y')
        if staff == 'all':
            return Sales.objects.select_related().filter(datetime__gte=startDate,
                                                         datetime__lte=endDate + timedelta(days=1),
                                                         salesType__exact='Card', ).exclude(
                datetime__lt=last_3_month_date)
        else:
            return Sales.objects.select_related().filter(datetime__gte=startDate,
                                                         datetime__lte=endDate + timedelta(days=1),
                                                         salesType__exact='Card',
                                                         createdBy=int(staff)).exclude(datetime__lt=last_3_month_date)

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(InvoiceSeriesID__companyID__name__icontains=search) | Q(amount__icontains=search) | Q(
                    billNumber__icontains=search) | Q(datetime__icontains=search) | Q(
                    createdBy__name__icontains=search)).order_by(
                '-id')

        return qs

    def prepare_results(self, qs):
        json_data = []
        i = 1
        for item in qs:

            if 'Moderator' in self.request.user.groups.values_list('name', flat=True):
                action = '''<span>N/A</span>'''.format(item.pk)

            elif 'Accountant' in self.request.user.groups.values_list('name', flat=True):
                action = '''<span> <a onclick="getDetail('{}','{}','{}','{}','{}')" data-toggle="modal"
                               data-target="#defaultModalInvoiceEdit"><button style="background-color: #3F51B5;color: white;" type="button"
                               class="btn  waves-effect " data-toggle="modal"
                               data-target="#largeModalEdit">
                           <i class="material-icons">border_color</i></button> </a></span>'''.format(item.pk, item.billNumber,
                                                                                          item.salesType, item.amount,
                                                                                          item.remark,)
            else:
                action = '''<span> <a onclick="getDetail('{}','{}','{}','{}','{}')" data-toggle="modal"
                               data-target="#defaultModalInvoiceEdit"><button style="background-color: #3F51B5;color: white;" type="button"
                               class="btn  waves-effect " data-toggle="modal"
                               data-target="#largeModalEdit">
                           <i class="material-icons">border_color</i></button> </a>



                       <button onclick="deleteSale('{}')" style="background-color: #e91e63;color: white;" type="button" class="btn  waves-effect hideModerator " data-toggle="modal"
                               data-target="#defaultModal">
                           <i class="material-icons">delete</i></button></span>'''.format(item.pk, item.billNumber,
                                                                                          item.salesType, item.amount,
                                                                                          item.customerName, item.pk)

            if item.InvoiceSeriesID.companyID is None:
                company = 'N/A'
            else:
                company = item.InvoiceSeriesID.companyID.name

            if item.createdBy is None:
                createdBy = 'Admin'
            else:
                createdBy = item.createdBy.name
            json_data.append([
                escape(i),
                escape(item.billNumber),
                escape(item.amount),  # escape HTML for security reasons
                escape(item.salesType),  # escape HTML for security reasons
                company,  # escape HTML for security reasons
                createdBy,  # escape HTML for security reasons
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),
                action

            ])
            i = i + 1
        return json_data


class InvoiceCreatedByMixListJson(BaseDatatableView):
    order_columns = ['id', 'billNumber', 'amount', 'mixCardAmount', 'salesType', 'InvoiceSeriesID', 'createdBy',
                     'datetime', 'action']

    def get_initial_queryset(self):

        sDate = self.request.GET.get('startDate')
        eDate = self.request.GET.get('endDate')
        staff = self.request.GET.get('staff')
        startDate = datetime.strptime(sDate, '%d/%m/%Y')
        endDate = datetime.strptime(eDate, '%d/%m/%Y')
        if staff == 'all':
            return Sales.objects.select_related().filter(datetime__gte=startDate,
                                                         datetime__lte=endDate + timedelta(days=1),
                                                         salesType__exact='Mix', ).exclude(
                datetime__lt=last_3_month_date)
        else:
            return Sales.objects.select_related().filter(datetime__gte=startDate,
                                                         datetime__lte=endDate + timedelta(days=1),
                                                         salesType__exact='Mix',
                                                         createdBy=int(staff)).exclude(datetime__lt=last_3_month_date)

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(InvoiceSeriesID__companyID__name__icontains=search) | Q(amount__icontains=search) |
                Q(mixCardAmount__icontains=search) | Q(
                    billNumber__icontains=search) | Q(datetime__icontains=search) | Q(
                    createdBy__name__icontains=search)).order_by(
                '-id')

        return qs

    def prepare_results(self, qs):
        json_data = []
        i = 1
        for item in qs:

            if 'Moderator' in self.request.user.groups.values_list('name', flat=True):
                action = '''<span>N/A</span>'''.format(item.pk)
            else:
                action = '''<span> <a onclick="getDetailMix('{}','{}','{}','{}','{}','{}')" data-toggle="modal"
                               data-target="#defaultModalInvoiceEditMix"><button style="background-color: #3F51B5;color: white;" type="button"
                               class="btn  waves-effect " data-toggle="modal"
                               data-target="#largeModalEdit">
                           <i class="material-icons">border_color</i></button> </a>



                       <button onclick="deleteSaleMix('{}')" style="background-color: #e91e63;color: white;" type="button" class="btn  waves-effect hideModerator " data-toggle="modal"
                               data-target="#defaultModalMix">
                           <i class="material-icons">delete</i></button></span>'''.format(item.pk, item.billNumber,
                                                                                          item.salesType, item.amount,
                                                                                          item.customerName,
                                                                                          item.mixCardAmount, item.pk)

            if item.InvoiceSeriesID.companyID is None:
                company = 'N/A'
            else:
                company = item.InvoiceSeriesID.companyID.name

            if item.createdBy is None:
                createdBy = 'Admin'
            else:
                createdBy = item.createdBy.name
            json_data.append([
                escape(i),
                escape(item.billNumber),
                escape(item.amount),  # escape HTML for security reasons
                escape(item.mixCardAmount),  # escape HTML for security reasons
                escape(item.salesType),  # escape HTML for security reasons
                company,  # escape HTML for security reasons
                createdBy,  # escape HTML for security reasons
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),
                action

            ])
            i = i + 1
        return json_data


class InvoiceCreatedByCreditListJson(BaseDatatableView):
    order_columns = ['id', 'billNumber', 'amount', 'challanNumber', 'customerName', 'salesType', 'InvoiceSeriesID',
                     'createdBy',
                     'datetime', 'action']

    def get_initial_queryset(self):

        sDate = self.request.GET.get('startDate')
        eDate = self.request.GET.get('endDate')
        staff = self.request.GET.get('staff')
        startDate = datetime.strptime(sDate, '%d/%m/%Y')
        endDate = datetime.strptime(eDate, '%d/%m/%Y')
        if staff == 'all':
            return Sales.objects.select_related().filter(datetime__gte=startDate,
                                                         datetime__lte=endDate + timedelta(days=1),
                                                         salesType__exact='Credit', ).exclude(
                datetime__lt=last_3_month_date)
        else:
            return Sales.objects.select_related().filter(datetime__gte=startDate,
                                                         datetime__lte=endDate + timedelta(days=1),
                                                         salesType__exact='Credit',
                                                         createdBy=int(staff)).exclude(datetime__lt=last_3_month_date)

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(InvoiceSeriesID__companyID__name__icontains=search) |
                Q(amount__icontains=search) | Q(challanNumber__icontains=search) | Q(billNumber__icontains=search) | Q(
                    datetime__icontains=search) | Q(
                    createdBy__name__icontains=search)).order_by(
                '-id')

        return qs

    def prepare_results(self, qs):
        json_data = []
        i = 1
        for item in qs:
            if 'Moderator' in self.request.user.groups.values_list('name', flat=True):
                action = '''<span>N/A</span>'''.format(item.pk)
            else:
                action = '''<span> <a onclick="getDetail('{}','{}','{}','{}','{}')" data-toggle="modal"
                               data-target="#defaultModalInvoiceEdit"><button style="background-color: #3F51B5;color: white;" type="button"
                               class="btn  waves-effect " data-toggle="modal"
                               data-target="#largeModalEdit">
                           <i class="material-icons">border_color</i></button> </a>



                       <button onclick="deleteSale('{}')" style="background-color: #e91e63;color: white;" type="button" class="btn  waves-effect hideModerator " data-toggle="modal"
                               data-target="#defaultModal">
                           <i class="material-icons">delete</i></button></span>'''.format(item.pk, item.billNumber,
                                                                                          item.salesType, item.amount,
                                                                                          item.customerName, item.pk)
            if item.InvoiceSeriesID.companyID is None:
                company = 'N/A'
            else:
                company = item.InvoiceSeriesID.companyID.name

            if item.createdBy is None:
                createdBy = 'Admin'
            else:
                createdBy = item.createdBy.name

            json_data.append([
                escape(i),
                escape(item.billNumber),
                escape(item.amount),  # escape HTML for security reasons
                escape(item.challanNumber),  # escape HTML for security reasons
                escape(item.customerName),  # escape HTML for security reasons
                escape(item.salesType),  # escape HTML for security reasons
                company,  # escape HTML for security reasons
                createdBy,  # escape HTML for security reasons
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),
                action,

            ])
            i = i + 1
        return json_data


class CollectionListJson(BaseDatatableView):
    order_columns = ['id', 'amount', 'buyerID.name', 'companyID', 'collectedBy', 'datetime', 'action']

    def get_initial_queryset(self):

        sDate = self.request.GET.get('startDate')
        eDate = self.request.GET.get('endDate')
        staff = self.request.GET.get('staff')
        startDate = datetime.strptime(sDate, '%d/%m/%Y')
        endDate = datetime.strptime(eDate, '%d/%m/%Y')
        if staff == 'all':
            return MoneyCollection.objects.select_related().filter(datetime__gte=startDate,
                                                                   datetime__lte=endDate + timedelta(days=1),
                                                                   isAddedInSales__exact=True).exclude(
                datetime__lt=last_3_month_date)
        else:
            return MoneyCollection.objects.select_related().filter(datetime__gte=startDate,
                                                                   datetime__lte=endDate + timedelta(days=1),
                                                                   collectedBy_id=int(staff),
                                                                   isAddedInSales__exact=True).exclude(
                datetime__lt=last_3_month_date)

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(Q(companyID__name__icontains=search) | Q(buyerID__name__icontains=search) | Q(
                amount__icontains=search) | Q(datetime__icontains=search) | Q(
                collectedBy__name__icontains=search)).order_by('-id')

        return qs

    def prepare_results(self, qs):
        json_data = []
        i = 1
        for item in qs:
            if 'Moderator' in self.request.user.groups.values_list('name', flat=True):
                action = '''<span>N/A</span>'''.format(item.pk)
            else:
                action = '''<span> <a onclick="getDetailCol('{}','{}','{}')" data-toggle="modal"
                               data-target="#defaultModalColEdit"><button style="background-color: #3F51B5;color: white;" type="button"
                               class="btn  waves-effect " data-toggle="modal"
                               data-target="#largeModalEdit">
                           <i class="material-icons">border_color</i></button> </a>



                       <button onclick="deleteCol('{}')" style="background-color: #e91e63;color: white;" type="button" class="btn  waves-effect hideModerator " data-toggle="modal"
                               data-target="#defaultModalDeleteCol">
                           <i class="material-icons">delete</i></button></span>'''.format(item.pk, item.amount,
                                                                                          item.buyerID.pk, item.pk)
            if item.collectedBy is None:
                createdBy = 'Admin'
            else:
                createdBy = item.collectedBy.name
            json_data.append([
                escape(i),
                escape(item.amount),  # escape HTML for security reasons
                escape(item.buyerID.name),  # escape HTML for security reasons
                escape(item.companyID.name),  # escape HTML for security reasons
                createdBy,  # escape HTML for security reasons
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),
                action,

            ])
            i = i + 1
        return json_data


class CashCollectionListJson(BaseDatatableView):
    order_columns = ['id', 'amount', 'buyerID.name', 'companyID', 'collectedBy', 'datetime', 'action']

    def get_initial_queryset(self):

        sDate = self.request.GET.get('startDate')
        eDate = self.request.GET.get('endDate')
        staff = self.request.GET.get('staff')
        startDate = datetime.strptime(sDate, '%d/%m/%Y')
        endDate = datetime.strptime(eDate, '%d/%m/%Y')
        if staff == 'all':
            return CashMoneyCollection.objects.select_related().filter(datetime__gte=startDate,
                                                                       datetime__lte=endDate + timedelta(days=1),
                                                                       isAddedInSales__exact=True).exclude(
                datetime__lt=last_3_month_date)
        else:
            return CashMoneyCollection.objects.select_related().filter(datetime__gte=startDate,
                                                                       datetime__lte=endDate + timedelta(days=1),
                                                                       collectedBy_id=int(staff),
                                                                       isAddedInSales__exact=True).exclude(
                datetime__lt=last_3_month_date)

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(Q(companyID__name__icontains=search) | Q(buyerID__name__icontains=search) | Q(
                amount__icontains=search) | Q(datetime__icontains=search) | Q(
                collectedBy__name__icontains=search)).order_by('-id')

        return qs

    def prepare_results(self, qs):
        json_data = []
        i = 1
        for item in qs:
            if 'Moderator' in self.request.user.groups.values_list('name', flat=True):
                action = '''<span>N/A</span>'''.format(item.pk)
            else:
                action = '''<span> <a onclick="getDetailColCash('{}','{}','{}')" data-toggle="modal"
                               data-target="#defaultModalColEditCash"><button style="background-color: #3F51B5;color: white;" type="button"
                               class="btn  waves-effect " data-toggle="modal"
                               data-target="#largeModalEdit">
                           <i class="material-icons">border_color</i></button> </a>



                       <button onclick="deleteColCash('{}')" style="background-color: #e91e63;color: white;" type="button" class="btn  waves-effect hideModerator " data-toggle="modal"
                               data-target="#defaultModalDeleteColCash">
                           <i class="material-icons">delete</i></button></span>'''.format(item.pk, item.amount,
                                                                                          item.buyerID.pk, item.pk)
            if item.collectedBy is None:
                createdBy = 'Admin'
            else:
                createdBy = item.collectedBy.name
            json_data.append([
                escape(i),
                escape(item.amount),  # escape HTML for security reasons
                escape(item.buyerID.name),  # escape HTML for security reasons
                escape(item.companyID.name),  # escape HTML for security reasons
                createdBy,  # escape HTML for security reasons
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),
                action,

            ])
            i = i + 1
        return json_data


class StaffAdvanceListJson(BaseDatatableView):
    order_columns = ['id', 'amount', 'buyerID.name', 'companyID', 'collectedBy', 'datetime', 'action']

    def get_initial_queryset(self):

        sDate = self.request.GET.get('startDate')
        eDate = self.request.GET.get('endDate')
        staff = self.request.GET.get('staff')
        startDate = datetime.strptime(sDate, '%d/%m/%Y')
        endDate = datetime.strptime(eDate, '%d/%m/%Y')
        if staff == 'all':
            return StaffAdvanceToBuyer.objects.select_related().filter(datetime__gte=startDate,
                                                                       datetime__lte=endDate + timedelta(days=1),
                                                                       ).exclude(datetime__lt=last_3_month_date)
        else:
            return StaffAdvanceToBuyer.objects.select_related().filter(datetime__gte=startDate,
                                                                       datetime__lte=endDate + timedelta(days=1),
                                                                       collectedBy_id=int(staff)).exclude(
                datetime__lt=last_3_month_date)

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(Q(companyID__name__icontains=search) | Q(buyerID__name__icontains=search) | Q(
                amount__icontains=search) | Q(datetime__icontains=search) | Q(
                collectedBy__name__icontains=search)).order_by('-id')

        return qs

    def prepare_results(self, qs):
        json_data = []
        i = 1
        for item in qs:
            if 'Moderator' in self.request.user.groups.values_list('name', flat=True):
                action = '''<span>N/A</span>'''.format(item.pk)
            else:
                action = '''<span> <a onclick="getDetailStaffAdvance('{}','{}','{}')" data-toggle="modal"
                               data-target="#defaultModalColEditStaffAdvance"><button style="background-color: #3F51B5;color: white;" type="button"
                               class="btn  waves-effect " data-toggle="modal"
                               data-target="#largeModalEdit">
                           <i class="material-icons">border_color</i></button> </a>



                       <button onclick="deleteColAdvance('{}')" style="background-color: #e91e63;color: white;" type="button" class="btn  waves-effect hideModerator " data-toggle="modal"
                               data-target="#defaultModalDeleteColAdvance">
                           <i class="material-icons">delete</i></button></span>'''.format(item.pk, item.amount,
                                                                                          item.buyerID.pk, item.pk)
            if item.collectedBy is None:
                createdBy = 'Admin'
            else:
                createdBy = item.collectedBy.name
            json_data.append([
                escape(i),
                escape(item.amount),  # escape HTML for security reasons
                escape(item.buyerID.name),  # escape HTML for security reasons
                escape(item.companyID.name),  # escape HTML for security reasons
                createdBy,  # escape HTML for security reasons
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),
                action,

            ])
            i = i + 1
        return json_data


class ReturnCollectionListJson(BaseDatatableView):
    order_columns = ['id', 'actualBillNumber', 'amount', 'companyID', 'createdBy', 'datetime', 'action']

    def get_initial_queryset(self):

        sDate = self.request.GET.get('startDate')
        eDate = self.request.GET.get('endDate')
        staff = self.request.GET.get('staff')
        startDate = datetime.strptime(sDate, '%d/%m/%Y')
        endDate = datetime.strptime(eDate, '%d/%m/%Y')
        if staff == 'all':
            return ReturnCollection.objects.select_related().filter(datetime__gte=startDate,
                                                                    datetime__lte=endDate + timedelta(days=1)).exclude(
                datetime__lt=last_3_month_date)
        else:
            return ReturnCollection.objects.select_related().filter(datetime__gte=startDate,
                                                                    datetime__lte=endDate + timedelta(days=1),
                                                                    createdBy_id=int(staff)).exclude(
                datetime__lt=last_3_month_date)

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(actualBillNumber__icontains=search) | Q(amount__icontains=search) | Q(datetime__icontains=search) | Q(
                    createdBy__name__icontains=search))

        return qs

    def prepare_results(self, qs):
        json_data = []
        i = 1
        for item in qs:
            if 'Moderator' in self.request.user.groups.values_list('name', flat=True):
                action = '''<span>N/A</span>'''.format(item.pk)
            else:
                action = '''<span> <a onclick="getDetailReturn('{}','{}','{}')" data-toggle="modal"
                               data-target="#defaultModalReturnEdit"><button style="background-color: #3F51B5;color: white;" type="button"
                               class="btn  waves-effect " data-toggle="modal"
                               data-target="#largeModalEdit">
                           <i class="material-icons">border_color</i></button> </a>



                       <button onclick="deleteReturn('{}')" style="background-color: #e91e63;color: white;" type="button" class="btn  waves-effect hideModerator " data-toggle="modal"
                               data-target="#defaultModalDeleteReturn">
                           <i class="material-icons">delete</i></button></span>'''.format(item.pk,
                                                                                          item.actualBillNumber,
                                                                                          item.amount, item.pk)
            if item.createdBy is None:
                createdBy = 'Admin'
            else:
                createdBy = item.createdBy.name
            json_data.append([
                escape(i),
                escape(item.actualBillNumber),  # escape HTML for security reasons
                '-' + str(item.amount),  # escape HTML for security reasons
                escape(item.companyID.name),  # escape HTML for security reasons
                createdBy,  # escape HTML for security reasons
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),
                action,

            ])
            i = i + 1
        return json_data


class CorrectCollectionListJson(BaseDatatableView):
    order_columns = ['id', 'actualBillNumber', 'amount', 'companyID', 'createdBy', 'datetime', 'action']

    def get_initial_queryset(self):

        sDate = self.request.GET.get('startDate')
        eDate = self.request.GET.get('endDate')
        staff = self.request.GET.get('staff')
        startDate = datetime.strptime(sDate, '%d/%m/%Y')
        endDate = datetime.strptime(eDate, '%d/%m/%Y')
        if staff == 'all':
            return CorrectCollection.objects.select_related().filter(datetime__gte=startDate,
                                                                     datetime__lte=endDate + timedelta(days=1)).exclude(
                datetime__lt=last_3_month_date)
        else:
            return CorrectCollection.objects.select_related().filter(datetime__gte=startDate,
                                                                     datetime__lte=endDate + timedelta(days=1),
                                                                     createdBy_id=int(staff)).exclude(
                datetime__lt=last_3_month_date)

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(actualBillNumber__icontains=search) | Q(amount__icontains=search) | Q(datetime__icontains=search) | Q(
                    createdBy__name__icontains=search))

        return qs

    def prepare_results(self, qs):
        json_data = []
        i = 1
        for item in qs:
            if 'Moderator' in self.request.user.groups.values_list('name', flat=True):
                action = '''<span>N/A</span>'''.format(item.pk)
            else:
                action = '''<span> <a onclick="getDetailCorrection('{}','{}','{}')" data-toggle="modal"
                               data-target="#defaultModalCorrectEdit"><button style="background-color: #3F51B5;color: white;" type="button"
                               class="btn  waves-effect " data-toggle="modal"
                               data-target="#largeModalEdit">
                           <i class="material-icons">border_color</i></button> </a>



                       <button onclick="deleteCorrection('{}')" style="background-color: #e91e63;color: white;" type="button" class="btn  waves-effect hideModerator " data-toggle="modal"
                               data-target="#defaultModalDeleteCorrection">
                           <i class="material-icons">delete</i></button></span>'''.format(item.pk,
                                                                                          item.actualBillNumber,
                                                                                          item.amount, item.pk)
            if item.createdBy is None:
                createdBy = 'Admin'
            else:
                createdBy = item.createdBy.name
            json_data.append([
                escape(i),
                escape(item.actualBillNumber),  # escape HTML for security reasons
                str(item.amount),  # escape HTML for security reasons
                escape(item.companyID.name),  # escape HTML for security reasons
                createdBy,  # escape HTML for security reasons
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),
                action,

            ])
            i = i + 1
        return json_data


class CommissionListJson(BaseDatatableView):
    order_columns = ['id', 'actualBillNumber', 'amount', 'companyID', 'createdBy', 'datetime', 'action']

    def get_initial_queryset(self):

        sDate = self.request.GET.get('startDate')
        eDate = self.request.GET.get('endDate')
        staff = self.request.GET.get('staff')
        startDate = datetime.strptime(sDate, '%d/%m/%Y')
        endDate = datetime.strptime(eDate, '%d/%m/%Y')
        if staff == 'all':
            return Commission.objects.select_related().filter(datetime__gte=startDate,
                                                              datetime__lte=endDate + timedelta(days=1)).exclude(
                datetime__lt=last_3_month_date)
        else:
            return Commission.objects.select_related().filter(datetime__gte=startDate,
                                                              datetime__lte=endDate + timedelta(days=1),
                                                              createdBy_id=int(staff)).exclude(
                datetime__lt=last_3_month_date)

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(actualBillNumber__icontains=search) | Q(amount__icontains=search) | Q(datetime__icontains=search) | Q(
                    createdBy__name__icontains=search))

        return qs

    def prepare_results(self, qs):
        json_data = []
        i = 1
        for item in qs:
            if 'Moderator' in self.request.user.groups.values_list('name', flat=True):
                action = '''<span>N/A</span>'''.format(item.pk)
            else:
                action = '''<span> <a onclick="getDetailCommission('{}','{}','{}')" data-toggle="modal"
                               data-target="#defaultModalCommissionEdit"><button style="background-color: #3F51B5;color: white;" type="button"
                               class="btn  waves-effect " data-toggle="modal"
                               data-target="#largeModalEdit">
                           <i class="material-icons">border_color</i></button> </a>



                       <button onclick="deleteCommission('{}')" style="background-color: #e91e63;color: white;" type="button" class="btn  waves-effect hideModerator " data-toggle="modal"
                               data-target="#defaultModalDeleteCommission">
                           <i class="material-icons">delete</i></button></span>'''.format(item.pk,
                                                                                          item.actualBillNumber,
                                                                                          item.amount, item.pk)
            if item.createdBy is None:
                createdBy = 'Admin'
            else:
                createdBy = item.createdBy.name
            json_data.append([
                escape(i),
                escape(item.actualBillNumber),  # escape HTML for security reasons
                '-' + str(item.amount),  # escape HTML for security reasons
                escape(item.companyID.name),  # escape HTML for security reasons
                createdBy,  # escape HTML for security reasons
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),
                action,

            ])
            i = i + 1
        return json_data


class ExpenseListJson(BaseDatatableView):
    order_columns = ['id', 'remark', 'amount', 'companyID', 'createdBy', 'datetime', 'action']

    def get_initial_queryset(self):

        sDate = self.request.GET.get('startDate')
        eDate = self.request.GET.get('endDate')
        staff = self.request.GET.get('staff')
        startDate = datetime.strptime(sDate, '%d/%m/%Y')
        endDate = datetime.strptime(eDate, '%d/%m/%Y')
        if staff == 'all':
            return Expense.objects.select_related().filter(datetime__gte=startDate,
                                                           datetime__lte=endDate + timedelta(days=1)).exclude(
                datetime__lt=last_3_month_date)
        else:
            return Expense.objects.select_related().filter(datetime__gte=startDate,
                                                           datetime__lte=endDate + timedelta(days=1),
                                                           createdBy_id=int(staff)).exclude(
                datetime__lt=last_3_month_date)

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(remark__icontains=search) | Q(amount__icontains=search) | Q(datetime__icontains=search) | Q(
                    createdBy__name__icontains=search))

        return qs

    def prepare_results(self, qs):
        json_data = []
        i = 1
        for item in qs:
            if 'Moderator' in self.request.user.groups.values_list('name', flat=True):
                action = '''<span>N/A</span>'''.format(item.pk)
            else:
                action = '''<span> <a onclick="getDetailExpense('{}','{}','{}')" data-toggle="modal"
                               data-target="#defaultModalExpenseEdit"><button style="background-color: #3F51B5;color: white;" type="button"
                               class="btn  waves-effect " data-toggle="modal"
                               data-target="#largeModalEdit">
                           <i class="material-icons">border_color</i></button> </a>



                       <button onclick="deleteExpense('{}')" style="background-color: #e91e63;color: white;" type="button" class="btn  waves-effect hideModerator " data-toggle="modal"
                               data-target="#defaultModalDeleteExpense">
                           <i class="material-icons">delete</i></button></span>'''.format(item.pk,
                                                                                          item.remark,
                                                                                          item.amount, item.pk)
            if item.createdBy is None:
                createdBy = 'Admin'
            else:
                createdBy = item.createdBy.name
            json_data.append([
                escape(i),
                escape(item.remark),  # escape HTML for security reasons
                str(item.amount),  # escape HTML for security reasons
                escape(item.companyID.name),  # escape HTML for security reasons
                createdBy,  # escape HTML for security reasons
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),
                action,

            ])
            i = i + 1
        return json_data


def index(request):
    if 'Both' in request.user.groups.values_list('name', flat=True):
        user = 'Admin'
        invoiceSerial = InvoiceSeries.objects.select_related().filter(isDeleted__exact=False).order_by('series')
    else:
        user = StaffUser.objects.select_related().get(userID_id=request.user.pk)
        invoiceSerial = InvoiceSeries.objects.select_related().filter(companyID_id=user.companyID_id,
                                                                      isDeleted__exact=False).order_by(
            'series')
    in_list = []
    for obj in invoiceSerial:
        in_dic = {
            'Series': obj.series,
            'SeriesID': obj.pk,
            # 'AssignedTo': obj.assignedTo.userID_id
        }

        in_list.append(in_dic)

    context = {
        'InvoiceSeries': in_list,
        'user': user
    }

    return render(request, 'invoice/index.html', context)


def new_index(request):
    if 'Both' in request.user.groups.values_list('name', flat=True):
        user = 'Admin'
        invoiceSerial = InvoiceSeries.objects.select_related().filter(isDeleted__exact=False).order_by('series')
    else:
        user = StaffUser.objects.select_related().get(userID_id=request.user.pk)
        invoiceSerial = InvoiceSeries.objects.select_related().filter(companyID_id=user.companyID_id,
                                                                      isDeleted__exact=False).order_by(
            'series')
    in_list = []
    for obj in invoiceSerial:
        in_dic = {
            'Series': obj.series,
            'SeriesID': obj.pk,
            # 'AssignedTo': obj.assignedTo.userID_id
        }

        in_list.append(in_dic)

    context = {
        'InvoiceSeries': in_list,
        'user': user
    }

    return render(request, 'invoice/newIndex.html', context)


def generate_serial_invoice_number(request):
    for i in range(1, 10000):
        num = str("{:05}".format(i))
        try:
            InvoiceSerial.objects.select_related().get(serials__exact=num)
        except:
            serials = InvoiceSerial()
            serials.number = num
            serials.numberMain = int(num)
            serials.save()

    return JsonResponse({'Message': 'Done'})


@functools.lru_cache(maxsize=256)
def get_invoice_series(request, *args, **kwargs):
    id = request.GET.get('id')
    if 'Both' in request.user.groups.values_list('name', flat=True):
        user = 'Admin'

    else:
        user = StaffUser.objects.select_related().get(userID_id=request.user.pk)

    if id == 'None':
        if 'Both' in request.user.groups.values_list('name', flat=True):

            invoiceByUser = InvoiceSeries.objects.select_related().filter(isDeleted__exact=False).first()
        else:
            invoiceByUser = InvoiceSeries.objects.select_related().filter(companyID_id=user.companyID_id,
                                                                          isDeleted__exact=False).first()

    else:
        if 'Both' in request.user.groups.values_list('name', flat=True):
            invoiceByUser = InvoiceSeries.objects.select_related().get(pk=int(id), isDeleted__exact=False)

        else:
            invoiceByUser = InvoiceSeries.objects.select_related().get(pk=int(id), companyID_id=user.companyID_id,
                                                                       isDeleted__exact=False)
    if 'Both' in request.user.groups.values_list('name', flat=True):

        salesID = Sales.objects.select_related().filter(InvoiceSeriesID_id=invoiceByUser.pk,
                                                        ).order_by('-numberMain')
    else:
        salesID = Sales.objects.select_related().filter(InvoiceSeriesID_id=invoiceByUser.pk,
                                                        InvoiceSeriesID__companyID_id=user.companyID_id).order_by(
            '-numberMain')

    # used
    used_invoice_id_list = []
    un_used_invoice_id_list = []
    upcoming_serials_invoice_id_list = []
    if salesID.first() == None:
        un_used = invoiceByUser.startsWith
        for i in InvoiceSerial.objects.select_related().filter(numberMain__gte=int(un_used)).order_by('numberMain')[
                 0:80]:
            un_used_invoice_id_dic = {
                'Serial': str(invoiceByUser.series) + str(i.number),
                'SeriesID': invoiceByUser.pk,
                'MainSeries': invoiceByUser.series,
                'MainNumber': i.numberMain
            }
            un_used_invoice_id_list.append(un_used_invoice_id_dic)

    else:
        un_used_first = salesID.first()
        for i in InvoiceSerial.objects.select_related().filter(numberMain__gt=int(un_used_first.numberMain - 150),
                                                               numberMain__lt=int(un_used_first.numberMain + 20),
                                                               numberMain__gte=invoiceByUser.startsWith).order_by(
            'numberMain'):
            try:
                sale = Sales.objects.select_related().get(numberMain__exact=i.numberMain,
                                                          InvoiceSeriesID_id=invoiceByUser.pk)
                used_invoice_id_dic = {
                    'Serial': str(invoiceByUser.series) + str(i.number),
                    'SeriesID': invoiceByUser.pk,
                    'MainSeries': invoiceByUser.series,
                    'MainNumber': i.numberMain
                }
                used_invoice_id_list.insert(0, used_invoice_id_dic)
            except:
                un_used_invoice_id_dic = {
                    'Serial': str(invoiceByUser.series) + str(i.number),
                    'SeriesID': invoiceByUser.pk,
                    'MainSeries': invoiceByUser.series,
                    'MainNumber': i.numberMain
                }
                un_used_invoice_id_list.append(un_used_invoice_id_dic)

    data = {
        'Used': used_invoice_id_list,
        'UnUsed': un_used_invoice_id_list,
        'Upcoming': upcoming_serials_invoice_id_list,

    }
    return JsonResponse({'data': data})


@functools.lru_cache(maxsize=256)
def get_invoice_series_load_more(request, *args, **kwargs):
    id = request.GET.get('id')
    last_id = request.GET.get('last_id')
    used_invoice_id_list = []
    un_used_invoice_id_list = []
    invoiceByUser = InvoiceSeries.objects.select_related().get(pk=int(id), isDeleted__exact=False)

    for i in InvoiceSerial.objects.filter(numberMain__gt=int(last_id)).order_by(
            'numberMain')[:20]:
        try:
            sale = Sales.objects.select_related().get(numberMain__exact=i.numberMain,
                                                      InvoiceSeriesID_id=int(id))
            used_invoice_id_dic = {
                'Serial': str(invoiceByUser.series) + str(i.number),
                'SeriesID': id,
                'MainSeries': invoiceByUser.series,
                'MainNumber': i.numberMain
            }
            used_invoice_id_list.insert(0, used_invoice_id_dic)
        except:
            un_used_invoice_id_dic = {
                'Serial': str(invoiceByUser.series) + str(i.number),
                'SeriesID': invoiceByUser.pk,
                'MainSeries': invoiceByUser.series,
                'MainNumber': i.numberMain
            }
            un_used_invoice_id_list.append(un_used_invoice_id_dic)

    data = {
        'Used': used_invoice_id_list,
        'UnUsed': un_used_invoice_id_list,
        # 'Upcoming': upcoming_serials_invoice_id_list,

    }
    return JsonResponse({'data': data})


def create_invoice(request):
    if request.method == 'POST':

        BillNumber = request.POST.get('BillNumber')
        SalesType = request.POST.get('SalesType')
        Amount = request.POST.get('Amount')
        CardAmount = request.POST.get('CardAmount')
        CustomerName = request.POST.get('CustomerName')
        SeriesID = request.POST.get('SeriesID')
        MainNumber = request.POST.get('MainNumber')
        MainSeries = request.POST.get('MainSeries')
        ChallanNumber = request.POST.get('ChallanNumber')
        cardRemark = request.POST.get('cardRemark')
        try:
            Remark = request.POST.get('Remark')
        except:
            Remark = ''
        try:
            saleExist = Sales.objects.select_related().filter(billNumber__exact=BillNumber,
                                                              InvoiceSeriesID_id=int(SeriesID))

            if saleExist.count() < 1:
                sale = Sales()
                sale.InvoiceSeriesID_id = int(SeriesID)
                sale.billNumber = BillNumber
                sale.actualBillNumber = MainNumber
                sale.numberMain = int(MainNumber)
                sale.salesType = SalesType
                sale.amount = float(Amount)
                sale.customerName = CustomerName
                if SalesType == 'Cash':
                    sale.isCash = True
                if SalesType == 'Card':
                    sale.isCash = False
                    sale.remark = Remark
                if SalesType == 'Credit':
                    sale.isCash = False
                    sale.challanNumber = ChallanNumber
                if SalesType == 'Mix':
                    sale.isCash = False
                    sale.mixCardAmount = float(CardAmount)
                    sale.remark = cardRemark
                if not 'Both' in request.user.groups.values_list('name', flat=True):
                    user = StaffUser.objects.select_related().get(userID_id=request.user.pk)
                    sale.createdBy_id = user.pk
                sale.save()
                enable_opening_balance(request)
                try:
                    by = sale.createdBy.name
                except:
                    by = 'Admin'

                data = {
                    'createdBy': by,
                    'billNo': sale.billNumber,
                    'amount': sale.amount + sale.mixCardAmount,
                    'datetime': sale.datetime.strftime('%d-%m-%Y %I:%M %p'),
                    'ModeOfPayment': sale.salesType,
                    'Remark': sale.remark
                }

                return JsonResponse({'message': 'success', 'data': data})
            else:
                data = {
                    # 'createdBy': saleExist.first().createdBy.name,
                    'billNo': saleExist.first().billNumber,
                    'amount': saleExist.first().amount,
                    'datetime': saleExist.first().datetime.strftime('%d-%m-%Y %I:%M %p')
                }

                return JsonResponse(
                    {'message': 'Bill already created with this number. Please try again.', 'data': data})

        except:
            return JsonResponse({'message': 'fail'})


def edit_invoice(request):
    if request.method == 'POST':

        invoiceID = request.POST.get('invoiceID')
        BillNumber = request.POST.get('invoiceE')
        SalesType = request.POST.get('salesE')
        Amount = request.POST.get('amountE')
        CustomerName = request.POST.get('customerE')
        invoice_series = BillNumber[:-4]
        MainNumber = BillNumber[-4:]

        try:
            isExist = InvoiceSeries.objects.select_related().get(series__exact=invoice_series, isDeleted__exact=False)
            sales = Sales.objects.select_related().filter(numberMain__exact=int(MainNumber),
                                                          InvoiceSeriesID_id=isExist.pk).exclude(
                pk=int(invoiceID)).count()

            if sales < 1:

                sale = Sales.objects.select_related().get(pk=int(invoiceID))

                sale.InvoiceSeriesID_id = isExist.pk
                sale.billNumber = BillNumber
                sale.numberMain = int(MainNumber)
                sale.salesType = SalesType
                sale.amount = float(Amount)
                sale.customerName = CustomerName
                if SalesType == 'Cash':
                    sale.isCash = True
                if SalesType == 'Card':
                    sale.isCash = False
                if SalesType == 'Credit':
                    sale.isCash = False

                sale.save()
                messages.success(request, 'Sales updated successfully.')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            else:

                messages.success(request, 'Error, Bill Number repeated.')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


        except:
            messages.success(request, 'Error, Please try again.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def edit_invoice_mix(request):
    if request.method == 'POST':

        invoiceID = request.POST.get('invoiceIDMix')
        BillNumber = request.POST.get('invoiceEMix')
        SalesType = request.POST.get('salesEMix')
        Amount = request.POST.get('amountEMix')
        CustomerName = request.POST.get('customerEMix')
        cardAmountEMix = request.POST.get('cardAmountEMix')

        invoice_series = BillNumber[0:2]
        MainNumber = BillNumber[2:]

        try:
            isExist = InvoiceSeries.objects.select_related().get(series__exact=int(invoice_series),
                                                                 isDeleted__exact=False)
            sales = Sales.objects.select_related().filter(numberMain__exact=int(MainNumber),
                                                          InvoiceSeriesID_id=isExist.pk).exclude(
                pk=int(invoiceID)).count()

            if sales < 1:

                sale = Sales.objects.select_related().get(pk=int(invoiceID))

                sale.InvoiceSeriesID_id = isExist.pk
                sale.billNumber = BillNumber
                sale.numberMain = int(MainNumber)
                sale.salesType = SalesType
                sale.amount = float(Amount)
                sale.customerName = CustomerName
                if SalesType == 'Cash':
                    sale.isCash = True
                if SalesType == 'Card':
                    sale.isCash = False
                if SalesType == 'Credit':
                    sale.isCash = False
                if SalesType == 'Mix':
                    sale.isCash = False
                    sale.mixCardAmount = float(cardAmountEMix)

                sale.save()
                messages.success(request, 'Sales updated successfully.')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            else:

                messages.success(request, 'Error, Bill Number repeated.')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


        except:
            messages.success(request, 'Error, Please try again.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def edit_collection(request):
    if request.method == 'POST':

        ColID = request.POST.get('ColID')
        Amount = request.POST.get('amountECol')
        CustomerName = request.POST.get('customerECol')
        try:
            col = MoneyCollection.objects.select_related().get(pk=int(ColID))
            realval = col.amount
            col.amount = float(Amount)
            prev_buy = col.buyerID_id
            col.buyerID_id = int(CustomerName)
            buy = Buyer.objects.select_related().get(pk=prev_buy)
            buy.closingBalance = (buy.closingBalance + realval)
            buy.save()
            col.save()
            new_buy = Buyer.objects.select_related().get(pk=int(CustomerName))
            new_buy.closingBalance = (new_buy.closingBalance - float(Amount))
            new_buy.save()
            messages.success(request, 'Collection updated successfully.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        except:
            messages.success(request, 'Error, Please try again.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def edit_collection_cash(request):
    if request.method == 'POST':

        ColID = request.POST.get('ColIDCash')
        Amount = request.POST.get('amountEColCash')
        CustomerName = request.POST.get('customerEColCash')
        try:
            col = CashMoneyCollection.objects.select_related().get(pk=int(ColID))
            realval = col.amount
            col.amount = float(Amount)
            prev_buy = col.buyerID_id
            col.buyerID_id = int(CustomerName)
            buy = Buyer.objects.select_related().get(pk=prev_buy)
            buy.closingBalance = (buy.closingBalance + realval)
            buy.save()
            col.save()
            new_buy = Buyer.objects.select_related().get(pk=int(CustomerName))
            new_buy.closingBalance = (new_buy.closingBalance - float(Amount))
            new_buy.save()
            messages.success(request, 'Cash Collection updated successfully.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        except:
            messages.success(request, 'Error, Please try again.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@check_group('Both')
def delete_sale_api(request):
    if request.method == 'POST':
        try:
            saleID = request.POST.get('saleID')
            sale = Sales.objects.select_related().get(pk=int(saleID))
            sale.delete()
            messages.success(request, 'Sales detail deleted successfully.')

            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        except:
            messages.success(request, 'Error. Please try again.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@check_group('Both')
def delete_sale_api_mix(request):
    if request.method == 'POST':
        try:
            saleID = request.POST.get('saleIDMix')
            sale = Sales.objects.select_related().get(pk=int(saleID))
            sale.delete()
            messages.success(request, 'Sales detail deleted successfully.')

            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        except:
            messages.success(request, 'Error. Please try again.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@check_group('Both')
def delete_collection_api(request):
    if request.method == 'POST':
        try:
            colDelID = request.POST.get('colDelID')
            col = MoneyCollection.objects.select_related().get(pk=int(colDelID))
            buy = Buyer.objects.select_related().get(pk=col.buyerID_id)
            buy.closingBalance = buy.closingBalance + col.amount
            buy.save()
            col.delete()

            messages.success(request, 'Collection detail deleted successfully.')

            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        except:
            messages.success(request, 'Error. Please try again.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@check_group('Both')
def delete_cash_collection_api(request):
    if request.method == 'POST':
        try:
            colDelID = request.POST.get('colDelIDCash')
            col = CashMoneyCollection.objects.select_related().get(pk=int(colDelID))
            buy = Buyer.objects.select_related().get(pk=col.buyerID_id)
            buy.closingBalance = buy.closingBalance + col.amount
            buy.save()
            col.delete()

            messages.success(request, 'Cash Collection detail deleted successfully.')

            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        except:
            messages.success(request, 'Error. Please try again.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def invoice_list(request):
    request.session['nav'] = '8'
    staff = StaffUser.objects.select_related().filter(isDeleted__exact=False,
                                                      staffTypeID__name__icontains='sale').order_by('name')
    company = Company.objects.select_related().filter(isDeleted__exact=False).order_by('name')
    context = {
        'staff': staff,
        'company': company
    }

    return render(request, 'invoice/manageInvoice.html', context)


def add_invoice_serial(request):
    if request.method == 'POST':
        try:
            # staffID = request.POST.get('buyerID')
            invoiceSeries = request.POST.get('invoiceSeries')
            companyID = request.POST.get('companyID')
            try:
                inv = InvoiceSeries.objects.select_related().get(series=invoiceSeries, companyID_id=int(companyID),
                                                                 isDeleted__exact=False)
                messages.success(request, 'Invoice Series Already Exist successfully.')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            except:
                invoice = InvoiceSeries()
                invoice.series = invoiceSeries
                # invoice.assignedTo_id = int(staffID)
                invoice.startsWith = '00001'
                invoice.companyID_id = int(companyID)
                invoice.save()
                messages.success(request, 'Invoice Series added successfully.')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        except:
            messages.success(request, 'Error. Please try again.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def edit_invoice_serial(request):
    if request.method == 'POST':
        try:
            invoiceID = request.POST.get('invoiceID')
            # staffID = request.POST.get('ebuyerID')

            invoice = InvoiceSeries.objects.select_related().get(pk=int(invoiceID))
            # invoice.assignedTo_id = int(staffID)
            invoice.save()
            messages.success(request, 'Invoice Series updated successfully.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        except:
            messages.success(request, 'Error. Please try again.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def invoice_report(request):
    request.session['nav'] = '9'
    users = StaffUser.objects.select_related().filter(isDeleted__exact=False,
                                                      staffTypeID__name__icontains='sale').order_by('name')
    date = datetime.today().now().strftime('%d/%m/%Y')
    company = Company.objects.select_related().filter(isDeleted__exact=False)
    buyers = Buyer.objects.select_related().filter(isDeleted__exact=False).order_by('name')

    context = {
        'users': users,
        'date': date,
        'company': company,
        'buyer': buyers,
    }
    return render(request, 'invoice/InvoiceReport.html', context)


def generate_net_report(request):
    user = StaffUser.objects.select_related().get(userID_id=request.user.pk)
    date = datetime.today().date()
    sales_cash = Sales.objects.select_related().filter(datetime__icontains=datetime.today().date(),
                                                       salesType__icontains='cash', isDeleted__exact=False,
                                                       InvoiceSeriesID__companyID_id=user.companyID_id).order_by(
        'InvoiceSeriesID', 'numberMain')
    sales_card = Sales.objects.select_related().filter(datetime__icontains=datetime.today().date(),
                                                       salesType__icontains='card', isDeleted__exact=False,
                                                       InvoiceSeriesID__companyID_id=user.companyID_id).order_by(
        'InvoiceSeriesID', 'numberMain')
    sales_credit = Sales.objects.select_related().filter(datetime__icontains=datetime.today().date(),
                                                         salesType__icontains='credit', isDeleted__exact=False,
                                                         InvoiceSeriesID__companyID_id=user.companyID_id).order_by(
        'InvoiceSeriesID', 'numberMain')

    sales_mix = Sales.objects.select_related().filter(datetime__icontains=datetime.today().date(),
                                                      salesType__icontains='Mix', isDeleted__exact=False,
                                                      InvoiceSeriesID__companyID_id=int(user.companyID_id)).order_by(
        'InvoiceSeriesID', 'numberMain')

    cash_total = 0.0
    for cash in sales_cash:
        cash_total = cash_total + cash.amount

    card_total = 0.0
    for card in sales_card:
        card_total = card_total + card.amount

    credit_total = 0.0
    for credit in sales_credit:
        credit_total = credit_total + credit.amount

    mix_cash_total = 0.0
    mix_card_total = 0.0
    for mix in sales_mix:
        mix_cash_total = mix_cash_total + mix.amount
        mix_card_total = mix_card_total + mix.mixCardAmount

    skipped_list = []
    invoiceByUser = InvoiceSeries.objects.select_related().filter(companyID_id=user.companyID_id,
                                                                  isCompleted__exact=False,
                                                                  isDeleted__exact=False)
    # for invoice in invoiceByUser:
    #     try:
    #         last_sale = Sales.objects.select_related().filter(InvoiceSeriesID_id=invoice.pk).order_by(
    #             '-numberMain').first()
    #
    #         for i in InvoiceSerial.objects.select_related().filter(numberMain__gte=int(invoice.startsWith),
    #                                                                numberMain__lt=int(last_sale.numberMain)
    #                                                                ).order_by('-numberMain')[0:200]:
    #             try:
    #                 sale = Sales.objects.select_related().get(numberMain__exact=i.numberMain,
    #                                                           InvoiceSeriesID_id=invoice.pk)
    #             except:
    #                 skipped_list.append(str(invoice.series) + str(i.number))
    #     except:
    #         pass
    returns = ReturnCollection.objects.select_related().filter(datetime__icontains=datetime.today().date(),
                                                               isDeleted__exact=False,
                                                               companyID_id=user.companyID_id).order_by(
        'actualBillNumber')
    corrections = CorrectCollection.objects.select_related().filter(datetime__icontains=datetime.today().date(),
                                                                    isDeleted__exact=False,
                                                                    companyID_id=user.companyID_id).order_by(
        'actualBillNumber')

    commissions = Commission.objects.select_related().filter(datetime__icontains=datetime.today().date(),
                                                             isDeleted__exact=False,
                                                             companyID_id=user.companyID_id).order_by(
        'actualBillNumber')
    expenses = Expense.objects.select_related().filter(datetime__icontains=datetime.today().date(),
                                                       isDeleted__exact=False,
                                                       companyID_id=user.companyID_id).order_by('datetime')

    return_total = 0.0
    for am in returns:
        return_total = return_total + am.amount

    correct_total = 0.0
    for ame in corrections:
        correct_total = correct_total + ame.amount

    commission_total = 0.0
    for c in commissions:
        commission_total = commission_total + c.amount

    expense_total = 0.0
    for e in expenses:
        expense_total = expense_total + e.amount
    col = MoneyCollection.objects.select_related().filter(datetime__icontains=datetime.today().date(),
                                                          companyID_id=user.companyID_id,
                                                          isAddedInSales__exact=True, isDeleted__exact=False).order_by(
        'datetime')

    advance = StaffAdvanceToBuyer.objects.select_related().filter(datetime__icontains=datetime.today().date(),
                                                                  companyID_id=int(user.companyID_id),
                                                                  isDeleted__exact=False).order_by('datetime')
    advance_total = 0.0
    for ad in advance:
        advance_total = advance_total + ad.amount
    context = {
        'sales_cash': sales_cash,
        'sales_card': sales_card,
        'sales_credit': sales_credit,
        'sales_mix': sales_mix,
        'date': date,
        'user': user,
        'skipped': skipped_list,
        'returns': returns,
        'commissions': commissions,
        'corrections': corrections,
        'expenses': expenses,
        'cash_total': cash_total,
        'card_total': card_total,
        'credit_total': credit_total,
        'mix_cash_total': mix_cash_total,
        'mix_card_total': mix_card_total,
        'return_total': return_total,
        'correct_total': correct_total,
        'commission_total': commission_total,
        'expense_total': expense_total,
        'mix_total': mix_cash_total + mix_card_total,
        'col': col,
        'advance': advance,
        'advance_total': advance_total
    }

    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = "report.pdf"
    html = render_to_string("invoice/invoicePDF.html", context)

    HTML(string=html).write_pdf(response, stylesheets=[CSS(string='@page { size: A5; margin: .3cm ; }')])
    return response


def generate_net_report_admin(request):
    companyID = request.GET.get('companyID')
    gDate = request.GET.get('gDate')
    date1 = datetime.strptime(gDate, '%d/%m/%Y')
    # date2 = datetime.strptime(endDate, '%d/%m/%Y')
    day_string = date1.strftime('%Y-%m-%d')
    date = datetime.today().date()
    sales_cash = Sales.objects.select_related().filter(datetime__icontains=day_string,
                                                       salesType__icontains='cash',
                                                       InvoiceSeriesID__companyID_id=int(companyID),
                                                       isDeleted__exact=False, ).exclude(
        datetime__lt=last_3_month_date).order_by('InvoiceSeriesID',
                                                 'numberMain')
    sales_card = Sales.objects.select_related().filter(datetime__icontains=day_string,
                                                       salesType__icontains='card',
                                                       InvoiceSeriesID__companyID_id=int(companyID),
                                                       isDeleted__exact=False, ).exclude(
        datetime__lt=last_3_month_date).order_by('InvoiceSeriesID',
                                                 'numberMain')
    sales_credit = Sales.objects.select_related().filter(datetime__icontains=day_string,
                                                         salesType__icontains='credit',
                                                         InvoiceSeriesID__companyID_id=int(companyID),
                                                         isDeleted__exact=False, ).exclude(
        datetime__lt=last_3_month_date).order_by('InvoiceSeriesID',
                                                 'numberMain')
    sales_mix = Sales.objects.select_related().filter(datetime__icontains=day_string,
                                                      salesType__icontains='Mix',
                                                      InvoiceSeriesID__companyID_id=int(companyID),
                                                      isDeleted__exact=False, ).exclude(
        datetime__lt=last_3_month_date).order_by('InvoiceSeriesID',
                                                 'numberMain')
    cash_total = 0.0
    for cash in sales_cash:
        cash_total = cash_total + cash.amount

    card_total = 0.0
    for card in sales_card:
        card_total = card_total + card.amount
    credit_cus_list = []
    credit_total = 0.0
    for credit in sales_credit:
        credit_total = credit_total + credit.amount
        credit_cus_list.append(credit.customerName)

    mix_cash_total = 0.0
    mix_card_total = 0.0
    for mix in sales_mix:
        mix_cash_total = mix_cash_total + mix.amount
        mix_card_total = mix_card_total + mix.mixCardAmount
    company = Company.objects.select_related().get(pk=int(companyID))
    invoiceByUser = InvoiceSeries.objects.select_related().filter(companyID_id=company.pk, isCompleted__exact=False,
                                                                  isDeleted__exact=False)

    skipped_list = []
    # for invoice in invoiceByUser:
    #     try:
    #         last_sale = Sales.objects.select_related().filter(InvoiceSeriesID_id=invoice.pk).order_by('-numberMain').first()
    #
    #         for i in InvoiceSerial.objects.select_related().filter(numberMain__gte=int(invoice.startsWith),
    #                                               numberMain__lt=int(last_sale.numberMain)
    #                                               ).order_by('-numberMain')[0:200]:
    #             try:
    #                 sale = Sales.objects.select_related().get(numberMain__exact=i.numberMain, InvoiceSeriesID_id=invoice.pk)
    #             except:
    #                 skipped_list.append(str(invoice.series) + str(i.number))
    #     except:
    #         pass
    returns = ReturnCollection.objects.select_related().filter(datetime__icontains=day_string,
                                                               companyID_id=int(companyID),
                                                               isDeleted__exact=False, ).exclude(
        datetime__lt=last_3_month_date).order_by('actualBillNumber')

    return_total = 0.0
    for am in returns:
        return_total = return_total + am.amount

    corrections = CorrectCollection.objects.select_related().filter(datetime__icontains=day_string,
                                                                    companyID_id=int(companyID),
                                                                    isDeleted__exact=False, ).exclude(
        datetime__lt=last_3_month_date).order_by(
        'actualBillNumber')

    correct_total = 0.0
    for ame in corrections:
        correct_total = correct_total + ame.amount

    commissions = Commission.objects.select_related().filter(datetime__icontains=day_string,
                                                             companyID_id=int(companyID),
                                                             isDeleted__exact=False, ).exclude(
        datetime__lt=last_3_month_date).order_by('actualBillNumber')

    commission_total = 0.0
    for c in commissions:
        commission_total = commission_total + c.amount

    expenses = Expense.objects.select_related().filter(datetime__icontains=day_string,
                                                       companyID_id=int(companyID), isDeleted__exact=False, ).exclude(
        datetime__lt=last_3_month_date).order_by(
        'datetime')

    expense_total = 0.0
    for e in expenses:
        expense_total = expense_total + e.amount

    col = MoneyCollection.objects.select_related().filter(datetime__icontains=day_string, companyID_id=int(companyID),
                                                          isAddedInSales__exact=True,
                                                          isDeleted__exact=False, ).exclude(
        datetime__lt=last_3_month_date).order_by('datetime')
    col_total = 0.0
    for c in col:
        col_total = col_total + c.amount

    colCash = CashMoneyCollection.objects.select_related().filter(datetime__icontains=day_string,
                                                                  companyID_id=int(companyID),
                                                                  isAddedInSales__exact=True,
                                                                  isDeleted__exact=False, ).exclude(
        datetime__lt=last_3_month_date).order_by('datetime')
    col_total_cash = 0.0
    for cash in colCash:
        col_total_cash = col_total_cash + cash.amount

    supCash = SupplierCollection.objects.select_related().filter( Q(approvedOn__isnull=False, approvedOn__icontains=day_string) |
    Q(approvedOn__isnull=True, datetime__icontains=day_string),
                                                                 companyID_id=int(companyID),
                                                                 isApproved__exact=True, paymentMode='Cash',
                                                                 isDeleted__exact=False, ).exclude(
        datetime__lt=last_3_month_date).order_by('datetime')
    sup_total_cash = 0.0
    for cash in supCash:
        sup_total_cash = sup_total_cash + cash.amount
    try:
        onc = OpeningAndClosingBalance.objects.select_related().get(balanceDate=day_string, companyID_id=int(companyID))
        opening = onc.openingAmount
        closing = onc.closingAmount
    except:
        opening = 0.0
        closing = 0.0

    advance = StaffAdvanceToBuyer.objects.select_related().filter(datetime__icontains=day_string,
                                                                  companyID_id=int(companyID),
                                                                  isDeleted__exact=False, ).exclude(
        datetime__lt=last_3_month_date).order_by('datetime')
    advance_total = 0.0
    for ad in advance:
        advance_total = advance_total + ad.amount

    rokad_value = opening + closing + float(col_total_cash) + float(sup_total_cash) + float(cash_total) + float(
        mix_cash_total) + float(correct_total) - float(expense_total) - float(commission_total) - float(
        return_total) - float(advance_total)
    context = {
        'sales_cash': sales_cash,
        'sales_card': sales_card,
        'sales_credit': sales_credit,
        'sales_mix': sales_mix,
        'date': gDate,
        'cash_total': cash_total,
        'card_total': card_total,
        'credit_total': credit_total,
        'company': company.name,
        'skipped': skipped_list,
        'returns': returns,
        'corrections': corrections,
        'correct_total': correct_total,
        'return_total': return_total,
        'commissions': commissions,
        'commission_total': commission_total,
        'mix_cash_total': mix_cash_total,
        'mix_card_total': mix_card_total,
        'mix_total': mix_cash_total + mix_card_total,
        'expense_total': expense_total,
        'expenses': expenses,
        'rokad': rokad_value,
        'opening': opening,
        'closing': closing,
        'advance': advance,
        'advance_total': advance_total,
        'credit_cus_list': len(set(credit_cus_list))
    }

    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = "report.pdf"
    html = render_to_string("invoice/invoicePDFAdmin.html", context)

    HTML(string=html).write_pdf(response, stylesheets=[CSS(string='@page { size: A5; margin: .3cm ; }')])
    return response


def generate_net_report_credit_admin(request):
    companyID = request.GET.get('companyID')
    gDate = request.GET.get('gDate')
    date1 = datetime.strptime(gDate, '%d/%m/%Y')
    day_string = date1.strftime('%Y-%m-%d')
    date = datetime.today().date()
    sales_credit = Sales.objects.select_related().filter(datetime__icontains=day_string,
                                                         salesType__icontains='credit',
                                                         InvoiceSeriesID__companyID_id=int(companyID),
                                                         isDeleted__exact=False, ).exclude(
        datetime__lt=last_3_month_date).order_by('customerName').order_by(
        'numberMain')

    party_list = []
    credit_total = 0.0
    for credit in sales_credit:
        credit_total = credit_total + credit.amount
        party_list.append(credit.customerName)
    cus_list = []
    for cre in set(party_list):
        sales_credit_by_cus = Sales.objects.select_related().filter(datetime__icontains=day_string,
                                                                    salesType__icontains='credit',
                                                                    customerName__exact=cre,
                                                                    InvoiceSeriesID__companyID_id=int(companyID),
                                                                    isDeleted__exact=False, ).exclude(
            datetime__lt=last_3_month_date).order_by(
            'InvoiceSeriesID').order_by('numberMain')
        c_total = 0
        for c in sales_credit_by_cus:
            c_total = c_total + c.amount

        c_dic = {
            'CustomerName': cre,
            'Amount': c_total

        }
        cus_list.append(c_dic)

    company = Company.objects.select_related().get(pk=int(companyID))
    context = {

        'sales_credit': sales_credit,
        'date': gDate,
        'credit_total': credit_total,
        'company': company.name,
        'cusList': cus_list,
        'credit_count': len(cus_list),

    }

    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = "report.pdf"
    html = render_to_string("invoice/invoiceCreditPDFAdmin.html", context)

    HTML(string=html).write_pdf(response, stylesheets=[CSS(string='@page { size: A5; margin: .3cm ; }')])
    return response


def generate_net_report_accountant(request):
    companyID = request.GET.get('companyID')
    gDate = request.GET.get('gDate')
    date1 = datetime.strptime(gDate, '%d/%m/%Y')
    # date2 = datetime.strptime(endDate, '%d/%m/%Y')
    day_string = date1.strftime('%Y-%m-%d')
    date = datetime.today().date()
    sales_cash = Sales.objects.select_related().filter(datetime__icontains=day_string, isDeleted__exact=False,
                                                       salesType__icontains='cash',
                                                       InvoiceSeriesID__companyID_id=int(companyID)).exclude(
        datetime__lt=last_3_month_date).order_by(
        'InvoiceSeriesID').order_by('numberMain')
    sales_card = Sales.objects.select_related().filter(datetime__icontains=day_string, isDeleted__exact=False,
                                                       salesType__icontains='card',
                                                       InvoiceSeriesID__companyID_id=int(companyID)).exclude(
        datetime__lt=last_3_month_date).order_by(
        'InvoiceSeriesID').order_by('numberMain')
    sales_credit = Sales.objects.select_related().filter(datetime__icontains=day_string, isDeleted__exact=False,
                                                         salesType__icontains='credit',
                                                         InvoiceSeriesID__companyID_id=int(companyID)).exclude(
        datetime__lt=last_3_month_date).order_by(
        'InvoiceSeriesID').order_by('numberMain')
    sales_mix = Sales.objects.select_related().filter(datetime__icontains=day_string, isDeleted__exact=False,
                                                      salesType__icontains='Mix',
                                                      InvoiceSeriesID__companyID_id=int(companyID)).exclude(
        datetime__lt=last_3_month_date).order_by(
        'InvoiceSeriesID').order_by('numberMain')

    company = Company.objects.select_related().get(pk=int(companyID))
    invoiceByUser = InvoiceSeries.objects.select_related().filter(companyID_id=company.pk, isCompleted__exact=False,
                                                                  isDeleted__exact=False)

    skipped_list = []
    for invoice in invoiceByUser:
        try:
            last_sale = Sales.objects.select_related().filter(InvoiceSeriesID_id=invoice.pk).order_by(
                '-numberMain').first()

            for i in InvoiceSerial.objects.select_related().filter(numberMain__gte=int(invoice.startsWith),
                                                                   numberMain__lt=int(last_sale.numberMain)
                                                                   ).order_by('-numberMain')[0:200]:
                try:
                    sale = Sales.objects.select_related().get(numberMain__exact=i.numberMain,
                                                              InvoiceSeriesID_id=invoice.pk)
                except:
                    skipped_list.append(str(invoice.series) + str(i.number))
        except:
            pass
    returns = ReturnCollection.objects.select_related().filter(datetime__icontains=day_string, isDeleted__exact=False,
                                                               companyID_id=int(companyID)).exclude(
        datetime__lt=last_3_month_date).order_by('actualBillNumber')

    corrections = CorrectCollection.objects.select_related().filter(datetime__icontains=day_string,
                                                                    isDeleted__exact=False,
                                                                    companyID_id=int(companyID)).exclude(
        datetime__lt=last_3_month_date).order_by(
        'actualBillNumber')

    commissions = Commission.objects.select_related().filter(datetime__icontains=day_string, isDeleted__exact=False,
                                                             companyID_id=int(companyID)).exclude(
        datetime__lt=last_3_month_date).order_by('actualBillNumber')

    expenses = Expense.objects.select_related().filter(datetime__icontains=day_string, isDeleted__exact=False,
                                                       companyID_id=int(companyID)).exclude(
        datetime__lt=last_3_month_date).order_by('datetime')
    advance = StaffAdvanceToBuyer.objects.select_related().filter(datetime__icontains=day_string,
                                                                  companyID_id=int(companyID),
                                                                  isDeleted__exact=False).exclude(
        datetime__lt=last_3_month_date).order_by('datetime')

    context = {
        'sales_cash': sales_cash,
        'sales_card': sales_card,
        'sales_credit': sales_credit,
        'sales_mix': sales_mix,
        'date': gDate,
        'company': company.name,
        'skipped': skipped_list,
        'returns': returns,
        'corrections': corrections,
        'commissions': commissions,
        'expenses': expenses,
        'advance': advance,

    }

    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = "report.pdf"
    html = render_to_string("invoice/invoicePDFAccountant.html", context)

    HTML(string=html).write_pdf(response, stylesheets=[CSS(string='@page { size: A5; margin: .3cm ; }')])
    return response


def generate_monthly_report_admin(request):
    companyID = request.GET.get('companyID')
    gDate = request.GET.get('gDate')
    date1 = datetime.strptime(gDate, '%d/%m/%Y')

    num_days = calendar.monthrange(date1.year, date1.month)[1]
    days = [date(date1.year, date1.month, day) for day in range(1, num_days + 1)]

    g_total = 0.0
    g_total_card = 0.0
    g_total_mix = 0.0
    g_total_credit = 0.0
    c_total = 0.0
    c_total_cash = 0.0
    s_total_cash = 0.0
    s_total_cheque = 0.0
    si_total_cheque = 0.0
    sale_list = []
    sale_list_card = []
    sale_list_mix = []
    sale_list_credit = []
    col_list = []
    col_list_cash = []
    s_list_cash = []
    s_list_cheque = []
    si_list_cheque = []
    entry_cash = 0
    entry_card = 0
    entry_mix = 0
    entry_credit = 0
    for d in days:
        day_string = d.strftime('%Y-%m-%d')
        sales_cash = Sales.objects.select_related().filter(datetime__contains=day_string, isDeleted__exact=False,
                                                           salesType__icontains='cash',
                                                           InvoiceSeriesID__companyID_id=int(companyID)).exclude(
            datetime__lt=last_3_month_date).order_by(
            'datetime')
        sales_card = Sales.objects.select_related().filter(datetime__contains=day_string, isDeleted__exact=False,
                                                           salesType__icontains='card',
                                                           InvoiceSeriesID__companyID_id=int(companyID)).exclude(
            datetime__lt=last_3_month_date).order_by(
            'datetime')
        sales_mix = Sales.objects.select_related().filter(datetime__contains=day_string, isDeleted__exact=False,
                                                          salesType__icontains='mix',
                                                          InvoiceSeriesID__companyID_id=int(companyID)).exclude(
            datetime__lt=last_3_month_date).order_by(
            'datetime')

        sales_credit = Sales.objects.select_related().filter(datetime__contains=day_string, isDeleted__exact=False,
                                                             salesType__icontains='credit',
                                                             InvoiceSeriesID__companyID_id=int(companyID)).exclude(
            datetime__lt=last_3_month_date).order_by(
            'datetime')
        cash_total = 0.0
        for cash in sales_cash:
            cash_total = cash_total + cash.amount
            entry_cash = entry_cash + 1

        card_total = 0.0
        for card in sales_card:
            card_total = card_total + card.amount
            entry_card = entry_card + 1

        mix_total = 0.0
        for mix in sales_mix:
            mix_total = mix_total + mix.amount
            entry_mix = entry_mix + 1

        credit_total = 0.0
        for cre in sales_credit:
            credit_total = credit_total + cre.amount
            entry_credit = entry_credit + 1

        sale_dic = {
            'Date': d,
            'Total': cash_total
        }

        g_total = g_total + cash_total

        sale_list.append(sale_dic)

        sale_card_dic = {
            'Date': d,
            'Total': card_total
        }

        g_total_card = g_total_card + card_total

        sale_list_card.append(sale_card_dic)

        sale_mix_dic = {
            'Date': d,
            'Total': mix_total
        }

        g_total_mix = g_total_mix + mix_total

        sale_list_mix.append(sale_mix_dic)

        sale_credit_dic = {
            'Date': d,
            'Total': credit_total
        }

        g_total_credit = g_total_credit + credit_total

        sale_list_credit.append(sale_credit_dic)
        col = MoneyCollection.objects.select_related().filter(datetime__icontains=day_string,
                                                              companyID_id=int(companyID), isDeleted__exact=False,
                                                              isAddedInSales__exact=True).exclude(
            datetime__lt=last_3_month_date).order_by('datetime')
        col_total = 0.0
        for c in col:
            col_total = col_total + c.amount

        col_dic = {
            'Date': d,
            'Total': col_total
        }
        c_total = c_total + col_total

        col_list.append(col_dic)

        colCash = CashMoneyCollection.objects.select_related().filter(datetime__icontains=day_string,
                                                                      companyID_id=int(companyID),
                                                                      isDeleted__exact=False,
                                                                      isAddedInSales__exact=True).exclude(
            datetime__lt=last_3_month_date).order_by('datetime')
        col_total_cash = 0.0
        for cash in colCash:
            col_total_cash = col_total_cash + cash.amount

        col_dic_cash = {
            'Date': d,
            'Total': col_total_cash
        }
        c_total_cash = c_total_cash + col_total_cash

        col_list_cash.append(col_dic_cash)

        supCash = SupplierCollection.objects.select_related().filter( Q(approvedOn__isnull=False, approvedOn__icontains=day_string) |
    Q(approvedOn__isnull=True, datetime__icontains=day_string),
                                                                     companyID_id=int(companyID),
                                                                     isDeleted__exact=False,
                                                                     isApproved__exact=True,
                                                                     paymentMode='Cash').exclude(
            datetime__lt=last_3_month_date)

        supplier_cash_total = 0.0
        for scash in supCash:
            supplier_cash_total = supplier_cash_total + scash.amount

        sup_dic_cash = {
            'Date': d,
            'Total': supplier_cash_total
        }
        s_total_cash = s_total_cash + supplier_cash_total

        s_list_cash.append(sup_dic_cash)

        supCheque = SupplierCollection.objects.select_related().filter( Q(approvedOn__isnull=False, approvedOn__icontains=day_string) |
    Q(approvedOn__isnull=True, datetime__icontains=day_string),
                                                                       companyID_id=int(companyID),
                                                                       isDeleted__exact=False,
                                                                       isApproved__exact=True,
                                                                       paymentMode='UPI').exclude(
            datetime__lt=last_3_month_date)

        supplier_cheque_total = 0.0
        for scheque in supCheque:
            supplier_cheque_total = supplier_cheque_total + scheque.amount

        sup_dic_cheque = {
            'Date': d,
            'Total': supplier_cheque_total
        }
        s_total_cheque = s_total_cheque + supplier_cheque_total

        s_list_cheque.append(sup_dic_cheque)

        si_col = SupplierCollection.objects.select_related().filter( Q(approvedOn__isnull=False, approvedOn__icontains=day_string) |
    Q(approvedOn__isnull=True, datetime__icontains=day_string),
                                                                    companyID_id=int(companyID),
                                                                    isApproved__exact=True,
                                                                    isDeleted__exact=False,
                                                                    paymentMode='Bank Transfer'
                                                                    ).exclude(
            datetime__lt=last_3_month_date).order_by('datetime')

        si_total = 0.0
        for si in si_col:
            si_total = si_total + si.amount

        si_dic = {
            'Date': d,
            'Total': si_total
        }
        si_total_cheque = si_total_cheque + si_total

        si_list_cheque.append(si_dic)
    company = Company.objects.select_related().get(pk=int(companyID))

    context = {
        'sales_cash': sale_list,
        'sales_card': sale_list_card,
        'collection': col_list,
        'collectionCash': col_list_cash,
        's_list_cash': s_list_cash,
        's_list_cheque': s_list_cheque,
        'sale_list_mix': sale_list_mix,
        'sale_list_credit': sale_list_credit,
        'si_list_cheque': si_list_cheque,
        's_total_cash': s_total_cash,
        's_total_cheque': s_total_cheque,
        'si_total_cheque': si_total_cheque,
        'Gtotal': g_total,
        'Cardtotal': g_total_card,
        'Mixtotal': g_total_mix,
        'Credittotal': g_total_credit,
        'Ctotal': c_total,
        'CtotalCash': c_total_cash,
        'Month': date1.month,
        'Year': date1.year,
        'company': company.name,
        'entry_cash': entry_cash,
        'entry_card': entry_card,
        'entry_mix': entry_mix,
        'entry_credit': entry_credit,
    }

    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = "report.pdf"
    html = render_to_string("invoice/invoiceMonthlyPDFAdmin.html", context)

    HTML(string=html).write_pdf(response, stylesheets=[CSS(string='@page { size: A5; margin: .3cm ; }')])
    return response


def generate_monthly_report_staff_advance_admin(request):
    companyID = request.GET.get('companyID')
    gDate = request.GET.get('gDate')
    date1 = datetime.strptime(gDate, '%d/%m/%Y')

    num_days = calendar.monthrange(date1.year, date1.month)[1]
    days = [date(date1.year, date1.month, day) for day in range(1, num_days + 1)]

    buyer_list = StaffAdvanceToBuyer.objects.select_related().filter(datetime__month=date1.month,
                                                                     datetime__year=date1.year,
                                                                     isDeleted__exact=False).order_by(
        'buyerID__name').values('buyerID').distinct()
    g_total = 0.0
    c_list = []
    for buyer in buyer_list:
        buyer_total = 0.0
        for d in days:
            day_string = d.strftime('%Y-%m-%d')
            sa = StaffAdvanceToBuyer.objects.select_related().filter(buyerID_id=int(buyer["buyerID"]),
                                                                     datetime__contains=day_string,
                                                                     companyID_id=int(companyID)).exclude(
                datetime__lt=last_3_month_date).order_by('datetime')

            for s in sa:
                buyer_total = buyer_total + s.amount

        b = Buyer.objects.select_related().get(pk=int(buyer["buyerID"]))
        buyer_dic = {
            'CustomerName': b.name,
            'Total': buyer_total
        }
        c_list.append(buyer_dic)
        g_total = g_total + buyer_total

    company = Company.objects.select_related().get(pk=int(companyID))

    context = {
        'customer': c_list,
        'g_total': g_total,
        'Month': date1.month,
        'Year': date1.year,
        'company': company.name,
    }

    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = "report.pdf"
    html = render_to_string("invoice/invoiceMonthlyStaffAdvancePDFAdmin.html", context)

    HTML(string=html).write_pdf(response, stylesheets=[CSS(string='@page { size: A5; margin: .3cm ; }')])
    return response


def search_invoice(request):
    if request.method == 'POST':

        sID = request.POST.get('sID')
        searchID = request.POST.get('searchID')
        try:
            obj = Sales.objects.select_related().get(InvoiceSeriesID_id=int(sID), numberMain=int(searchID))
            try:
                name = obj.createdBy.name[0:10]
            except:
                name = 'Admin'
            data = {
                'BillNumber': obj.billNumber,
                'Amount': obj.amount,
                'SalesType': obj.salesType.upper(),
                'CustomerName': obj.customerName,
                'Datetime': obj.datetime.strftime('%d-%m-%Y %I:%M %p'),
                'CreatedBy': name,
                'Remark': obj.remark
            }
            return JsonResponse({'message': 'success', 'data': data})

        except:
            try:
                invoiceByUser = InvoiceSeries.objects.select_related().get(pk=int(sID))
                invoice = InvoiceSerial.objects.select_related().get(numberMain__gte=int(invoiceByUser.startsWith),
                                                                     numberMain__lt=10000,
                                                                     numberMain__exact=int(searchID))
                dataNew = {
                    'Serial': str(invoiceByUser.series) + str(invoice.number),
                    'SeriesID': invoiceByUser.pk,
                    'MainSeries': invoiceByUser.series,
                    'MainNumber': invoice.numberMain
                }

                return JsonResponse({'message': 'notFound', 'dataNew': dataNew})
            except:
                return JsonResponse({'message': 'fail'})


@functools.lru_cache(maxsize=256)
def skipped_invoice(request):
    if 'Both' in request.user.groups.values_list('name', flat=True):
        invoiceByUser = InvoiceSeries.objects.select_related().filter(isDeleted__exact=False)


    else:
        user = StaffUser.objects.select_related().get(userID_id=request.user.pk)

        invoiceByUser = InvoiceSeries.objects.select_related().filter(companyID_id=user.companyID_id,
                                                                      isDeleted__exact=False)

    skipped_list = []
    for invoice in invoiceByUser:
        try:

            last_sale = Sales.objects.select_related().filter(InvoiceSeriesID_id=invoice.pk).order_by(
                '-numberMain').first()

            for i in InvoiceSerial.objects.select_related().filter(numberMain__gte=int(invoice.startsWith),
                                                                   numberMain__lt=int(last_sale.numberMain)
                                                                   ).order_by('numberMain'):
                try:
                    sale = Sales.objects.select_related().get(numberMain__exact=i.numberMain,
                                                              InvoiceSeriesID_id=invoice.pk)
                except:
                    skipped_invoice_id_dic = {
                        'Serial': str(invoice.series) + str(i.number),
                        'SeriesID': invoice.pk,
                        'MainSeries': invoice.series,
                        'MainNumber': i.numberMain
                    }
                    skipped_list.append(skipped_invoice_id_dic)

        except:
            pass

    data = {
        'skipped': skipped_list,

    }
    return JsonResponse({'data': data})


def take_collection(request):
    if request.method == 'POST':

        partyName = request.POST.get('partyName')
        partyAmount = request.POST.get('partyAmount')
        collectionremark = request.POST.get('collectionremark')

        try:
            collection = MoneyCollection()
            collection.buyerID_id = int(partyName)
            collection.amount = float(partyAmount)
            collection.remark = collectionremark

            collection.paymentMode = 'Cash'
            collection.isAddedInSales = True
            if not 'Both' in request.user.groups.values_list('name', flat=True):
                user = StaffUser.objects.select_related().get(userID_id=request.user.pk)
                collection.collectedBy_id = user.pk
                collection.companyID_id = user.companyID_id
            else:
                collection.companyID_id = 1

            collection.save()
            buy = Buyer.objects.select_related().get(pk=int(partyName))
            buy.closingBalance = buy.closingBalance - float(partyAmount)
            buy.save()
            enable_opening_balance(request)
            return JsonResponse({'message': 'success'})

        except:
            return JsonResponse({'message': 'fail'})


def take_cash_collection(request):
    if request.method == 'POST':

        partyName = request.POST.get('partyName')
        partyAmount = request.POST.get('partyAmount')

        try:
            collection = CashMoneyCollection()
            collection.buyerID_id = int(partyName)
            collection.amount = float(partyAmount)
            collection.paymentMode = 'Cash'
            collection.isAddedInSales = True
            if not 'Both' in request.user.groups.values_list('name', flat=True):
                user = StaffUser.objects.select_related().get(userID_id=request.user.pk)
                collection.collectedBy_id = user.pk
                collection.companyID_id = user.companyID_id
            else:
                collection.companyID_id = 1

            collection.save()
            buy = Buyer.objects.select_related().get(pk=int(partyName))
            buy.closingBalance = buy.closingBalance - float(partyAmount)
            buy.save()
            enable_opening_balance(request)
            return JsonResponse({'message': 'success'})

        except:
            return JsonResponse({'message': 'fail'})


@functools.lru_cache(maxsize=256)
def get_today_collection_by_company(request):
    if 'Both' in request.user.groups.values_list('name', flat=True):
        col = MoneyCollection.objects.select_related().filter(datetime__icontains=datetime.today().date(),
                                                              isAddedInSales__exact=True).exclude(
            datetime__lt=last_3_month_date).order_by('-datetime')
    else:
        user = StaffUser.objects.select_related().get(userID_id=request.user.pk)
        col = MoneyCollection.objects.select_related().filter(datetime__icontains=datetime.today().date(),
                                                              companyID_id=user.companyID_id,
                                                              isAddedInSales__exact=True).exclude(
            datetime__lt=last_3_month_date).order_by('-datetime')
    c_list = []
    for c in col:
        data = {
            'Amount': c.amount,
            'Customer': c.buyerID.name,
            'ID': c.pk,

        }

        c_list.append(data)

    return JsonResponse({'message': 'success', 'data': c_list})


@functools.lru_cache(maxsize=256)
def get_today_cash_collection_by_company(request):
    if 'Both' in request.user.groups.values_list('name', flat=True):
        col = CashMoneyCollection.objects.select_related().filter(datetime__icontains=datetime.today().date(),
                                                                  isAddedInSales__exact=True).exclude(
            datetime__lt=last_3_month_date).order_by('-datetime')

    else:
        user = StaffUser.objects.select_related().get(userID_id=request.user.pk)
        col = CashMoneyCollection.objects.select_related().filter(datetime__icontains=datetime.today().date(),
                                                                  companyID_id=user.companyID_id,
                                                                  isAddedInSales__exact=True).exclude(
            datetime__lt=last_3_month_date).order_by('-datetime')
    c_list = []
    for c in col:
        data = {
            'Amount': c.amount,
            'Customer': c.buyerID.name,
            'ID': c.pk,

        }

        c_list.append(data)

    return JsonResponse({'message': 'success', 'data': c_list})


@csrf_exempt
def add_party_from_sales(request):
    if request.method == 'POST':

        pName = request.POST.get('pName')
        pAddress = request.POST.get('pAddress')
        pPhone = request.POST.get('pPhone')

        try:

            buy = Buyer.objects.select_related().filter(name__iexact=pName)
            if buy.count() == 0:

                buy = Buyer()
                buy.phoneNumber = pPhone
                buy.name = pName
                buy.address = pAddress
                buy.closingBalance = 0.0
                buy.save()
                cache.delete('buyer_list_search')

                c_list = []

                data = {
                    'Name': buy.name,
                    'Phone': buy.phoneNumber,
                    'ID': buy.pk,
                    'Address': buy.address,

                }

                c_list.append(data)
                return JsonResponse({'message': 'success', 'data': c_list})
            else:
                return JsonResponse({'message': 'alreadyExist'})
        except:
            return JsonResponse({'message': 'fail'})


# def get_buyer_list(request):
#     q = request.GET.get('q', '').strip()
#     cache_key = 'buyer_list_'+q
#     data = cache.get(cache_key)
#
#     if not data:
#         buyers = Buyer.objects.filter(
#             name__icontains=q, isDeleted=False
#         ).order_by('name').values('name', 'phoneNumber', 'pk', 'address')
#         data = list(buyers)
#         cache.set(cache_key, data, timeout=60 * 10)  # Cache for 10 minutes
#     return JsonResponse({'message': 'success', 'data': data})



def get_buyer_list(request):
    q = request.GET.get('q', '')
    cache_key = str('buyer_list_search')  # Unique cache key based on the search query
    try:
        cached_data = cache.get(str(cache_key))
    except:
        cached_data = None

    if cached_data:
        filtered_data = [
            buyer for buyer in cached_data
            if buyer.get('name') and q.lower() in buyer['name'].lower()
        ]
        # If data is found in the cache, return it
        return JsonResponse({'message': 'success', 'data': filtered_data})

    # If not in cache, fetch from the database
    buyers = Buyer.objects.filter( isDeleted=False
    ).order_by('name').values('name', 'phoneNumber', 'pk', 'address')

    buyer_list = list(buyers)

    # Store the fetched data in Redis
    cache.set(cache_key, buyer_list, timeout=None)  # Cache for 1 day
    return JsonResponse({'message': 'success', 'data': buyer_list})


@csrf_exempt
def change_password_for_sales_user(request):
    if request.method == 'POST':

        nPass = request.POST.get('nPass')

        try:

            staff = StaffUser.objects.select_related().get(userID_id=request.user.pk)

            staff.password = nPass
            user = User.objects.select_related().get(id=staff.userID_id)

            user.set_password(nPass)
            user.save()
            staff.save()
            return JsonResponse({'message': 'success'})

        except:
            return JsonResponse({'message': 'fail'})


@functools.lru_cache(maxsize=256)
def get_last_three_invoices(request, *args, **kwargs):
    if 'Both' in request.user.groups.values_list('name', flat=True):
        invoiceByUser = InvoiceSeries.objects.select_related().filter(isCompleted__exact=False, isDeleted__exact=False)


    else:
        user = StaffUser.objects.select_related().get(userID_id=request.user.pk)

        invoiceByUser = InvoiceSeries.objects.select_related().filter(companyID_id=user.companyID_id,
                                                                      isCompleted__exact=False,
                                                                      isDeleted__exact=False)
    last_three = []

    for inv in invoiceByUser:
        if 'Both' in request.user.groups.values_list('name', flat=True):
            salesID = Sales.objects.select_related().filter(InvoiceSeriesID_id=inv.pk,
                                                            ).order_by('-id')[0:3]

        else:
            salesID = Sales.objects.select_related().filter(InvoiceSeriesID_id=inv.pk,
                                                            InvoiceSeriesID__companyID_id=user.companyID_id).order_by(
                '-id')[0:3]
        for sale in salesID:
            used_invoice_id_dic = {
                'Serial': sale.billNumber,

            }
            last_three.append(used_invoice_id_dic)

    data = {
        'Used': last_three,

    }
    return JsonResponse({'data': data})


def generate_collection_report_accounts(request):
    companyID = request.GET.get('companyID')
    gDate = request.GET.get('gDate')
    date1 = datetime.strptime(gDate, '%d/%m/%Y')
    day_string = date1.strftime('%Y-%m-%d')

    company = Company.objects.select_related().get(pk=int(companyID))
    col = MoneyCollection.objects.select_related().filter(datetime__icontains=day_string, companyID_id=int(companyID),
                                                          isDeleted__exact=False,
                                                          isAddedInSales__exact=True).exclude(
        datetime__lt=last_3_month_date).order_by('datetime')
    col_total = 0.0
    for c in col:
        col_total = col_total + c.amount

    colCash = CashMoneyCollection.objects.select_related().filter(datetime__icontains=day_string,
                                                                  companyID_id=int(companyID),
                                                                  isDeleted__exact=False,
                                                                  isAddedInSales__exact=True).exclude(
        datetime__lt=last_3_month_date).order_by('datetime')
    col_total_cash = 0.0
    for cash in colCash:
        col_total_cash = col_total_cash + cash.amount

    supCash = SupplierCollection.objects.select_related().filter( Q(approvedOn__isnull=False, approvedOn__icontains=day_string) |
    Q(approvedOn__isnull=True, datetime__icontains=day_string),
                                                                 companyID_id=int(companyID), isDeleted__exact=False,
                                                                 isApproved__exact=True, paymentMode='Cash').exclude(
        datetime__lt=last_3_month_date).order_by(
        'datetime')
    sup_total_cash = 0.0
    for cash in supCash:
        sup_total_cash = sup_total_cash + cash.amount

    supUpi = SupplierCollection.objects.select_related().filter( Q(approvedOn__isnull=False, approvedOn__icontains=day_string) |
    Q(approvedOn__isnull=True, datetime__icontains=day_string),
                                                                companyID_id=int(companyID),
                                                                isDeleted__exact=False,
                                                                isApproved__exact=True,
                                                                paymentMode='UPI').exclude(
        datetime__lt=last_3_month_date).order_by('datetime')

    supBank = SupplierCollection.objects.select_related().filter( Q(approvedOn__isnull=False, approvedOn__icontains=day_string) |
    Q(approvedOn__isnull=True, datetime__icontains=day_string),
                                                                 companyID_id=int(companyID),
                                                                 isDeleted__exact=False,
                                                                 isApproved__exact=True,
                                                                 paymentMode='Bank Transfer').exclude(
        datetime__lt=last_3_month_date).order_by('datetime')
    sup_total_Upi = 0.0
    for obj in supUpi:
        sup_total_Upi = sup_total_Upi + obj.amount

    supInvoice = SupplierInvoiceCollection.objects.select_related().filter(datetime__icontains=day_string,
                                                                           companyID_id=int(companyID),
                                                                           isApproved__exact=True,
                                                                           isDeleted__exact=False,
                                                                           ).exclude(
        datetime__lt=last_3_month_date).order_by('datetime')
    sup_total_inv = 0.0
    for inv in supInvoice:
        sup_total_inv = sup_total_inv + inv.amount

    supInvoice_pending = SupplierInvoiceCollection.objects.select_related().filter(datetime__icontains=day_string,
                                                                                   companyID_id=int(companyID),
                                                                                   isApproved__exact=False,
                                                                                   isDeleted__exact=False,
                                                                                   ).exclude(
        datetime__lt=last_3_month_date).order_by('datetime')
    supCash_pending = SupplierCollection.objects.select_related().filter(datetime__icontains=day_string,
                                                                         companyID_id=int(companyID),
                                                                         isApproved__exact=False,
                                                                         isDeleted__exact=False,
                                                                         isCancelled=False,
                                                                         paymentMode='Cash').exclude(
        datetime__lt=last_3_month_date).order_by('datetime')

    supUpi_pending = SupplierCollection.objects.select_related().filter(datetime__icontains=day_string,
                                                                        companyID_id=int(companyID),
                                                                        isApproved__exact=False,
                                                                        isDeleted__exact=False,
                                                                        isCancelled=False,
                                                                        paymentMode='UPI').exclude(
        datetime__lt=last_3_month_date).order_by('datetime')

    supBank_pending = SupplierCollection.objects.select_related().filter(datetime__icontains=day_string,
                                                                         companyID_id=int(companyID),
                                                                         isApproved__exact=False,
                                                                         isCancelled=False,
                                                                         isDeleted__exact=False,
                                                                         paymentMode='Bank Transfer').exclude(
        datetime__lt=last_3_month_date).order_by('datetime')

    supCash_cancel = SupplierCollection.objects.select_related().filter(datetime__icontains=day_string,
                                                                         companyID_id=int(companyID),
                                                                         isApproved__exact=False,
                                                                         isCancelled=True,
                                                                         isDeleted__exact=False).exclude(
        datetime__lt=last_3_month_date).order_by('datetime')
    context = {
        'date': gDate,
        'company': company.name,
        'col': col,
        'col_total': 0,
        'colCash': colCash,
        'col_total_cash': 0,
        'supCash': supCash,
        'sup_total_cash': 0,
        'supUpi': supUpi,
        'supUpi_pending': supUpi_pending,
        'sup_total_cheque': 0,
        'invoice_total': 0,
        'invoices': supInvoice,
        'supInvoice_pending': supInvoice_pending,
        'supCash_pending': supCash_pending,
        'supBank': supBank,
        'supBank_pending': supBank_pending,
        'supCash_cancel': supCash_cancel,

    }

    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = "report.pdf"
    html = render_to_string("invoice/CollectionPDFAccounts.html", context)

    HTML(string=html).write_pdf(response, stylesheets=[CSS(string='@page { size: A5;  }')])
    return response


def generate_collection_report_admin(request):
    companyID = request.GET.get('companyID')
    gDate = request.GET.get('gDate')
    date1 = datetime.strptime(gDate, '%d/%m/%Y')
    day_string = date1.strftime('%Y-%m-%d')

    company = Company.objects.select_related().get(pk=int(companyID))
    col = MoneyCollection.objects.select_related().filter(datetime__icontains=day_string, companyID_id=int(companyID),
                                                          isDeleted__exact=False,
                                                          isAddedInSales__exact=True).exclude(
        datetime__lt=last_3_month_date).order_by('datetime')
    col_total = 0.0
    for c in col:
        col_total = col_total + c.amount

    colCash = CashMoneyCollection.objects.select_related().filter(datetime__icontains=day_string,
                                                                  companyID_id=int(companyID),
                                                                  isDeleted__exact=False,
                                                                  isAddedInSales__exact=True).exclude(
        datetime__lt=last_3_month_date).order_by('datetime')
    col_total_cash = 0.0
    for cash in colCash:
        col_total_cash = col_total_cash + cash.amount

    supCash = SupplierCollection.objects.select_related().filter(Q(approvedOn__isnull=False, approvedOn__icontains=day_string) |
    Q(approvedOn__isnull=True, datetime__icontains=day_string),
    companyID_id=int(companyID),
    isDeleted__exact=False,
    isApproved__exact=True,
    paymentMode='Cash'
).exclude(
    datetime__lt=last_3_month_date
).order_by('datetime')
    sup_total_cash = 0.0
    for cash in supCash:
        sup_total_cash = sup_total_cash + cash.amount

    supUpi = SupplierCollection.objects.select_related().filter( Q(approvedOn__isnull=False, approvedOn__icontains=day_string) |
    Q(approvedOn__isnull=True, datetime__icontains=day_string),
                                                                   companyID_id=int(companyID),
                                                                   isDeleted__exact=False,
                                                                   isApproved__exact=True,
                                                                   paymentMode='UPI').exclude(
        datetime__lt=last_3_month_date).order_by('datetime')
    sup_total_upi = 0.0
    for obj in supUpi:
        sup_total_upi = sup_total_upi + obj.amount

    supBank = SupplierCollection.objects.select_related().filter( Q(approvedOn__isnull=False, approvedOn__icontains=day_string) |
    Q(approvedOn__isnull=True, datetime__icontains=day_string),
                                                                   companyID_id=int(companyID),
                                                                   isDeleted__exact=False,
                                                                   isApproved__exact=True,
                                                                   paymentMode='Bank Transfer').exclude(
        datetime__lt=last_3_month_date).order_by('datetime')
    sup_total_bank = 0.0
    for obj in supBank:
        sup_total_bank = sup_total_bank + obj.amount

    supInvoice = SupplierInvoiceCollection.objects.select_related().filter(datetime__icontains=day_string,
                                                                           companyID_id=int(companyID),
                                                                           isApproved__exact=True,
                                                                           isDeleted__exact=False,
                                                                           ).exclude(
        datetime__lt=last_3_month_date).order_by('datetime')
    sup_total_inv = 0.0
    for inv in supInvoice:
        sup_total_inv = sup_total_inv + inv.amount

    supInvoice_pending = SupplierInvoiceCollection.objects.select_related().filter(datetime__icontains=day_string,
                                                                                   companyID_id=int(companyID),
                                                                                   isApproved__exact=False,
                                                                                   isDeleted__exact=False,
                                                                                   ).exclude(
        datetime__lt=last_3_month_date).order_by('datetime')
    supCash_pending = SupplierCollection.objects.select_related().filter(datetime__icontains=day_string,
                                                                         companyID_id=int(companyID),
                                                                         isApproved__exact=False,
                                                                         isCancelled=False,
                                                                         isDeleted__exact=False,
                                                                         paymentMode='Cash').exclude(
        datetime__lt=last_3_month_date).order_by('datetime')

    supUpi_pending = SupplierCollection.objects.select_related().filter(datetime__icontains=day_string,
                                                                        companyID_id=int(companyID),
                                                                        isDeleted__exact=False,
                                                                        isApproved__exact=False,
                                                                        isCancelled=False,
                                                                        paymentMode='UPI').exclude(
        datetime__lt=last_3_month_date).order_by('datetime')
    sup_total_upi = 0.0
    for obj in supUpi:
        sup_total_upi = sup_total_upi + obj.amount

    supBank_pending = SupplierCollection.objects.select_related().filter(datetime__icontains=day_string,
                                                                         companyID_id=int(companyID),
                                                                         isDeleted__exact=False,
                                                                         isApproved__exact=False,
                                                                         isCancelled=False,
                                                                         paymentMode='Bank Transfer').exclude(
        datetime__lt=last_3_month_date).order_by('datetime')

    supCash_cancel = SupplierCollection.objects.select_related().filter(datetime__icontains=day_string,
                                                                         companyID_id=int(companyID),
                                                                         isApproved__exact=False,
                                                                         isCancelled=True,
                                                                         isDeleted__exact=False).exclude(
        datetime__lt=last_3_month_date).order_by('datetime')
    context = {
        'date': gDate,
        'company': company.name,
        'col': col,
        'col_total': col_total,
        'colCash': colCash,
        'col_total_cash': col_total_cash,
        'supCash': supCash,
        'sup_total_cash': sup_total_cash,
        'supUpi': supUpi,
        'sup_total_upi': sup_total_upi,
        'supBank': supBank,
        'sup_total_bank': sup_total_bank,
        'invoice_total': sup_total_inv,
        'invoices': supInvoice,
        'supInvoice_pending': supInvoice_pending,
        'supCash_pending': supCash_pending,
        'supUpi_pending': supUpi_pending,
        'supBank_pending': supBank_pending,
        'supCash_cancel': supCash_cancel,

    }

    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = "report.pdf"
    html = render_to_string("invoice/CollectionPDFAdmin.html", context)

    HTML(string=html).write_pdf(response, stylesheets=[CSS(string='@page { size: A5;  }')])
    return response


def generate_collection_report_supplier(request):
    user = StaffUser.objects.select_related().get(userID_id=request.user.pk)
    day_string = datetime.today().date()

    supCash = SupplierCollection.objects.select_related().filter( Q(approvedOn__isnull=False, approvedOn__icontains=day_string) |
    Q(approvedOn__isnull=True, datetime__icontains=day_string),
                                                                 collectedBy__userID_id=request.user.pk,
                                                                 paymentMode='Cash', isDeleted__exact=False, ).exclude(
        datetime__lt=last_3_month_date).order_by(
        'datetime')
    sup_total_cash = 0.0
    for cash in supCash:
        sup_total_cash = sup_total_cash + cash.amount

    supUpi = SupplierCollection.objects.select_related().filter( Q(approvedOn__isnull=False, approvedOn__icontains=day_string) |
    Q(approvedOn__isnull=True, datetime__icontains=day_string),
                                                                collectedBy__userID_id=request.user.pk,
                                                                paymentMode='UPI',
                                                                isDeleted__exact=False, ).exclude(
        datetime__lt=last_3_month_date).order_by('datetime')
    sup_total_upi = 0.0
    for upi in supUpi:
        sup_total_upi = sup_total_upi + upi.amount

    supBank = SupplierCollection.objects.select_related().filter( Q(approvedOn__isnull=False, approvedOn__icontains=day_string) |
    Q(approvedOn__isnull=True, datetime__icontains=day_string),
                                                                 collectedBy__userID_id=request.user.pk,
                                                                 paymentMode='Bank Transfer',
                                                                 isDeleted__exact=False, ).exclude(
        datetime__lt=last_3_month_date).order_by('datetime')
    sup_total_supBank = 0.0
    for obj in supBank:
        sup_total_supBank = sup_total_supBank + obj.amount

    supInvoice = SupplierInvoiceCollection.objects.select_related().filter(datetime__icontains=datetime.today().date(),
                                                                           collectedBy__userID_id=request.user.pk,
                                                                           isDeleted__exact=False, ).exclude(
        datetime__lt=last_3_month_date).order_by(
        'datetime')
    sup_total_inv = 0.0
    for inv in supInvoice:
        sup_total_inv = sup_total_inv + inv.amount
    context = {
        'date': datetime.today().date(),
        'company': user.name,
        'supCash': supCash,
        'sup_total_cash': sup_total_cash,
        'supUpi': supUpi,
        'sup_total_upi': sup_total_upi,
        'supBank': supBank,
        'sup_total_supBank': sup_total_supBank,
        'invoice_total': sup_total_inv,
        'invoices': supInvoice

    }

    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = "report.pdf"
    html = render_to_string("invoice/CollectionPDFSupplier.html", context)

    HTML(string=html).write_pdf(response, stylesheets=[CSS(string='@page { size: A5; margin: .3cm ; }')])
    return response


def generate_collection_report(request):
    user = StaffUser.objects.select_related().get(userID_id=request.user.pk)
    date = datetime.today().date()
    col = MoneyCollection.objects.select_related().filter(datetime__icontains=datetime.today().date(),
                                                          companyID_id=user.companyID_id,
                                                          isAddedInSales__exact=True,
                                                          isDeleted__exact=False, ).exclude(
        datetime__lt=last_3_month_date).order_by('datetime')

    colCash = CashMoneyCollection.objects.select_related().filter(datetime__icontains=datetime.today().date(),
                                                                  companyID_id=user.companyID_id,
                                                                  isAddedInSales__exact=True,
                                                                  isDeleted__exact=False, ).exclude(
        datetime__lt=last_3_month_date).order_by(
        'datetime')

    context = {

        'date': date,
        'user': user,
        'col': col,
        'colCash': colCash,

    }

    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = "report.pdf"
    html = render_to_string("invoice/collectionPDF.html", context)

    HTML(string=html).write_pdf(response, stylesheets=[CSS(string='@page { size: A5; margin: .3cm ; }')])
    return response


@check_group('Accountant')
def collection_report_accountant(request):
    request.session['nav'] = '9'
    users = StaffUser.objects.select_related().filter(isDeleted__exact=False,
                                                      staffTypeID__name__icontains='sale').order_by('name')
    date = datetime.today().now().strftime('%d/%m/%Y')
    company = Company.objects.select_related().filter(isDeleted__exact=False)
    buyers = Buyer.objects.select_related().filter(isDeleted__exact=False).order_by('name')

    context = {
        'users': users,
        'date': date,
        'company': company,
        'buyer': buyers,
    }
    return render(request, 'invoice/CollectionReportAccountant.html', context)


def return_collection(request):
    if request.method == 'POST':

        sIDReturn = request.POST.get('sIDReturn')
        invoiceNumberReturn = request.POST.get('invoiceNumberReturn')
        AmountReturn = request.POST.get('AmountReturn')

        try:
            re = ReturnCollection()
            re.numberMain = int(invoiceNumberReturn)
            re.actualBillNumber = sIDReturn + str(invoiceNumberReturn).zfill(4)
            re.amount = float(AmountReturn)
            if not 'Both' in request.user.groups.values_list('name', flat=True):
                user = StaffUser.objects.select_related().get(userID_id=request.user.pk)
                re.createdBy_id = user.pk
                re.companyID_id = user.companyID_id
            else:
                c = InvoiceSeries.objects.select_related().get(series__iexact=sIDReturn, isDeleted__exact=False,
                                                               isCompleted__exact=False)

                re.companyID_id = c.companyID_id
            re.save()
            enable_opening_balance(request)
            return JsonResponse({'message': 'success'})

        except:
            return JsonResponse({'message': 'fail'})


def correct_collection(request):
    if request.method == 'POST':

        sIDReturn = request.POST.get('sIDReturn')
        invoiceNumberReturn = request.POST.get('invoiceNumberReturn')
        AmountReturn = request.POST.get('AmountReturn')

        try:
            re = CorrectCollection()
            re.numberMain = int(invoiceNumberReturn)
            re.actualBillNumber = sIDReturn + str(invoiceNumberReturn).zfill(4)
            re.amount = float(AmountReturn)
            if not 'Both' in request.user.groups.values_list('name', flat=True):
                user = StaffUser.objects.select_related().get(userID_id=request.user.pk)
                re.createdBy_id = user.pk
                re.companyID_id = user.companyID_id
            else:
                c = InvoiceSeries.objects.select_related().get(series__iexact=sIDReturn, isDeleted__exact=False,
                                                               isCompleted__exact=False)

                re.companyID_id = c.companyID_id
            re.save()
            enable_opening_balance(request)
            try:
                by = re.createdBy.name
            except:
                by = 'Admin'

            data = {
                'createdBy': by,
                'billNo': re.actualBillNumber,
                'amount': re.amount,
                'datetime': re.datetime.strftime('%d-%m-%Y %I:%M %p'),
                'ModeOfPayment': "Correction"
            }

            return JsonResponse({'message': 'success', 'data': data})
        except:
            return JsonResponse({'message': 'fail'})


def get_today_return_by_company(request):
    if 'Both' in request.user.groups.values_list('name', flat=True):
        col = ReturnCollection.objects.select_related().filter(datetime__icontains=datetime.today().date()).exclude(
            datetime__lt=last_3_month_date).order_by(
            '-datetime')

    else:
        user = StaffUser.objects.select_related().get(userID_id=request.user.pk)
        col = ReturnCollection.objects.select_related().filter(datetime__icontains=datetime.today().date(),
                                                               companyID_id=user.companyID_id).exclude(
            datetime__lt=last_3_month_date).order_by('-datetime')
    c_list = []
    for c in col:
        data = {
            'InvoiceNumber': c.actualBillNumber,
            'Amount': c.amount,
            'ID': c.pk,

        }

        c_list.append(data)

    return JsonResponse({'message': 'success', 'data': c_list})


def get_today_correction_by_company(request):
    if 'Both' in request.user.groups.values_list('name', flat=True):
        col = CorrectCollection.objects.select_related().filter(datetime__icontains=datetime.today().date()).exclude(
            datetime__lt=last_3_month_date).order_by(
            '-datetime')

    else:
        user = StaffUser.objects.select_related().get(userID_id=request.user.pk)
        col = CorrectCollection.objects.select_related().filter(datetime__icontains=datetime.today().date(),
                                                                companyID_id=user.companyID_id).exclude(
            datetime__lt=last_3_month_date).order_by('-datetime')
    c_list = []
    for c in col:
        data = {
            'InvoiceNumber': c.actualBillNumber,
            'Amount': c.amount,
            'ID': c.pk,

        }

        c_list.append(data)

    return JsonResponse({'message': 'success', 'data': c_list})


def edit_return(request):
    if request.method == 'POST':

        ColID = request.POST.get('ReturnID')
        Amount = request.POST.get('amountEReturn')
        invoice = request.POST.get('invoiceEReturn')
        try:
            ret = ReturnCollection.objects.select_related().get(pk=int(ColID))
            ret.amount = float(Amount)
            ret.actualBillNumber = invoice

            ret.save()

            messages.success(request, 'Return updated successfully.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        except:
            messages.success(request, 'Error, Please try again.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def edit_correction(request):
    if request.method == 'POST':

        ColID = request.POST.get('CorrectionID')
        Amount = request.POST.get('amountECorrection')
        invoice = request.POST.get('invoiceECorrection')
        try:
            ret = CorrectCollection.objects.select_related().get(pk=int(ColID))
            ret.amount = float(Amount)
            ret.actualBillNumber = invoice

            ret.save()

            messages.success(request, 'Correction updated successfully.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        except:
            messages.success(request, 'Error, Please try again.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@check_group('Both')
def delete_return_api(request):
    if request.method == 'POST':
        try:
            returnDelID = request.POST.get('returnDelID')
            col = ReturnCollection.objects.select_related().get(pk=int(returnDelID))
            col.delete()
            messages.success(request, 'Return detail deleted successfully.')

            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        except:
            messages.success(request, 'Error. Please try again.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@check_group('Both')
def delete_correction_api(request):
    if request.method == 'POST':
        try:
            returnDelID = request.POST.get('correctionDelID')
            col = CorrectCollection.objects.select_related().get(pk=int(returnDelID))
            col.delete()
            messages.success(request, 'Correction detail deleted successfully.')

            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        except:
            messages.success(request, 'Error. Please try again.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def commission_collection(request):
    if request.method == 'POST':

        sIDReturn = request.POST.get('sIDReturn')
        invoiceNumberReturn = request.POST.get('invoiceNumberReturn')
        AmountReturn = request.POST.get('AmountReturn')

        try:
            re = Commission()
            re.numberMain = int(invoiceNumberReturn)
            re.actualBillNumber = sIDReturn + str(invoiceNumberReturn).zfill(4)
            re.amount = float(AmountReturn)

            if not 'Both' in request.user.groups.values_list('name', flat=True):
                user = StaffUser.objects.select_related().get(userID_id=request.user.pk)
                re.createdBy_id = user.pk
                re.companyID_id = user.companyID_id
            else:
                c = InvoiceSeries.objects.select_related().get(series__iexact=sIDReturn, isDeleted__exact=False,
                                                               isCompleted__exact=False)

                re.companyID_id = c.companyID_id

            re.save()
            enable_opening_balance(request)
            return JsonResponse({'message': 'success'})

        except:
            return JsonResponse({'message': 'fail'})


def get_today_commission_by_company(request):
    if 'Both' in request.user.groups.values_list('name', flat=True):
        col = Commission.objects.select_related().filter(datetime__icontains=datetime.today().date()
                                                         ).exclude(
            datetime__lt=last_3_month_date).order_by('-datetime')

    else:
        user = StaffUser.objects.select_related().get(userID_id=request.user.pk)
        col = Commission.objects.select_related().filter(datetime__icontains=datetime.today().date(),
                                                         companyID_id=user.companyID_id).exclude(
            datetime__lt=last_3_month_date).order_by('-datetime')
    c_list = []
    for c in col:
        data = {
            'InvoiceNumber': c.actualBillNumber,
            'Amount': c.amount,
            'ID': c.pk,

        }

        c_list.append(data)

    return JsonResponse({'message': 'success', 'data': c_list})


def edit_commission(request):
    if request.method == 'POST':

        ColID = request.POST.get('CommissionID')
        Amount = request.POST.get('amountECommission')
        invoice = request.POST.get('invoiceECommission')
        try:
            ret = Commission.objects.select_related().get(pk=int(ColID))
            ret.amount = float(Amount)
            ret.actualBillNumber = invoice

            ret.save()

            messages.success(request, 'Commission updated successfully.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        except:
            messages.success(request, 'Error, Please try again.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@check_group('Both')
def delete_commission_api(request):
    if request.method == 'POST':
        try:
            returnDelID = request.POST.get('commissionDelID')
            col = Commission.objects.select_related().get(pk=int(returnDelID))
            col.delete()
            messages.success(request, 'Commission detail deleted successfully.')

            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        except:
            messages.success(request, 'Error. Please try again.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# Expense


def add_expense(request):
    if request.method == 'POST':

        exAmount = request.POST.get('exAmount')
        exRemark = request.POST.get('exRemark')

        try:
            ex = Expense()
            ex.remark = exRemark
            ex.amount = float(exAmount)
            try:
                user = StaffUser.objects.select_related().get(userID_id=request.user.pk)
                ex.createdBy_id = user.pk
                ex.companyID_id = user.companyID_id
            except:
                ex.companyID_id = 1
            ex.save()
            enable_opening_balance(request)

            return JsonResponse({'message': 'success', })
        except:
            return JsonResponse({'message': 'fail'})


def get_today_expense_by_company(request):
    if 'Both' in request.user.groups.values_list('name', flat=True):
        col = Expense.objects.select_related().filter(datetime__icontains=datetime.today().date()
                                                      ).exclude(
            datetime__lt=last_3_month_date).order_by('-datetime')

    else:
        user = StaffUser.objects.select_related().get(userID_id=request.user.pk)
        col = Expense.objects.select_related().filter(datetime__icontains=datetime.today().date(),
                                                      companyID_id=user.companyID_id).exclude(
            datetime__lt=last_3_month_date).order_by('-datetime')
    c_list = []
    for c in col:
        data = {
            'Remark': c.remark,
            'Amount': c.amount,
            'ID': c.pk,

        }

        c_list.append(data)

    return JsonResponse({'message': 'success', 'data': c_list})


def edit_expense(request):
    if request.method == 'POST':

        ColID = request.POST.get('ExpenseID')
        Amount = request.POST.get('amountEExpense')
        remark = request.POST.get('remarkEExpense')
        try:
            ret = Expense.objects.select_related().get(pk=int(ColID))
            ret.amount = float(Amount)
            ret.remark = remark

            ret.save()

            messages.success(request, 'Expense updated successfully.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        except:
            messages.success(request, 'Error, Please try again.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@check_group('Both')
def delete_expense_api(request):
    if request.method == 'POST':
        try:
            returnDelID = request.POST.get('expenseDelID')
            col = Expense.objects.select_related().get(pk=int(returnDelID))
            col.delete()
            messages.success(request, 'Expense detail deleted successfully.')

            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        except:
            messages.success(request, 'Error. Please try again.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@csrf_exempt
def add_closing_balance_api(request):
    if request.method == 'POST':
        Balance = request.POST.get('Balance')
        try:
            try:
                user = StaffUser.objects.select_related().get(userID_id=request.user.pk)
                ex = OpeningAndClosingBalance.objects.select_related().get(balanceDate=datetime.today().date(),
                                                                           isBalanceCreditedOnNextDay=False,
                                                                           companyID_id=user.companyID_id)
                if ex.closingAmount == 0.0:
                    ex.closingAmount = float(Balance)
                    ex.createdBy_id = user.pk
                    ex.save()
                    return JsonResponse({'message': 'success', })
                else:
                    return JsonResponse({'message': 'Already Added.'})

            except:

                ex = OpeningAndClosingBalance.objects.select_related().get(balanceDate=datetime.today().date(),
                                                                           isBalanceCreditedOnNextDay=False,
                                                                           companyID_id=1)
                if ex.closingAmount == 0.0:
                    ex.closingAmount = float(Balance)
                    ex.save()
                    return JsonResponse({'message': 'success', })
                else:
                    return JsonResponse({'message': 'Already Added.'})

        except:
            return JsonResponse({'message': 'fail'})


# staff Advance

def staff_advance_post(request):
    if request.method == 'POST':

        partyName = request.POST.get('partyName')
        partyAmount = request.POST.get('partyAmount')

        try:
            sa = StaffAdvanceToBuyer()
            sa.buyerID_id = int(partyName)
            sa.amount = float(partyAmount)
            if not 'Both' in request.user.groups.values_list('name', flat=True):
                user = StaffUser.objects.select_related().get(userID_id=request.user.pk)
                sa.collectedBy_id = user.pk
                sa.companyID_id = user.companyID_id
                sa.save()
            else:
                sa.companyID_id = 1

                sa.save()
            enable_opening_balance(request)
            return JsonResponse({'message': 'success'})

        except:
            return JsonResponse({'message': 'fail'})


def get_today_staff_advance_by_company(request):
    if 'Both' in request.user.groups.values_list('name', flat=True):
        col = StaffAdvanceToBuyer.objects.select_related().filter(datetime__icontains=datetime.today().date(),
                                                                  ).exclude(
            datetime__lt=last_3_month_date).order_by('-datetime')

    else:
        user = StaffUser.objects.select_related().get(userID_id=request.user.pk)
        col = StaffAdvanceToBuyer.objects.select_related().filter(datetime__icontains=datetime.today().date(),
                                                                  companyID_id=user.companyID_id,
                                                                  ).exclude(
            datetime__lt=last_3_month_date).order_by('-datetime')
    c_list = []
    for c in col:
        data = {
            'Amount': c.amount,
            'Customer': c.buyerID.name,
            'ID': c.pk,

        }

        c_list.append(data)

    return JsonResponse({'message': 'success', 'data': c_list})


def edit_staff_advance(request):
    if request.method == 'POST':

        ColID = request.POST.get('ColIDAdvance')
        Amount = request.POST.get('amountEColAdvance')
        CustomerName = request.POST.get('customerEColAdvance')
        try:
            col = StaffAdvanceToBuyer.objects.select_related().get(pk=int(ColID))
            col.amount = float(Amount)
            col.buyerID_id = int(CustomerName)
            col.save()
            messages.success(request, 'Staff Advance updated successfully.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        except:
            messages.success(request, 'Error, Please try again.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@check_group('Both')
def delete_staff_advance_api(request):
    if request.method == 'POST':
        try:
            ID = request.POST.get('colDelIDAdvance')
            col = StaffAdvanceToBuyer.objects.select_related().get(pk=int(ID))

            col.delete()
            messages.success(request, 'Staff Advance detail deleted successfully.')

            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        except:
            messages.success(request, 'Error. Please try again.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# cashier Report
def generate_collection_report_for_cashier(request):
    user = StaffUser.objects.select_related().get(userID_id=request.user.pk)
    gDate = request.GET.get('gDate')
    date1 = datetime.strptime(gDate, '%d/%m/%Y')
    day_string = date1.strftime('%Y-%m-%d')
    total = 0.0
    cashcollection = SupplierCollection.objects.select_related().filter(datetime__icontains=day_string,
                                                                        isApproved__exact=True,
                                                                        approvedBy__iexact=user.name).exclude(
        datetime__lt=last_3_month_date)
    invoicecollection = SupplierInvoiceCollection.objects.select_related().filter(datetime__icontains=day_string,
                                                                                  isApproved__exact=True,
                                                                                  approvedBy__iexact=user.name).exclude(
        datetime__lt=last_3_month_date)

    for a in cashcollection:
        total = total + a.amount

    for b in invoicecollection:
        total = total + b.amount

    context = {
        'date': gDate,
        'user': user,
        'cashcollection': cashcollection,
        'invoicecollection': invoicecollection,
        'total': total

    }

    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = "report.pdf"
    html = render_to_string("invoice/CashierCollectionPDFReport.html", context)

    HTML(string=html).write_pdf(response, stylesheets=[CSS(string='@page { size: A5; margin: .3cm ; }')])
    return response


import base64


def share_order_to_whatsapp_pdf(request):
    date = datetime.today().date()
    ID = request.GET.get('ID')
    col = TakeOrder.objects.select_related().get(isDeleted__exact=False, pk=int(ID))
    try:
        from PIL import Image
        from io import BytesIO
        image_file = col.orderPic.file
        image = Image.open(image_file)

        # Convert to RGB if it's not
        if image.mode != 'RGB':
            image = image.convert('RGB')

        scale_ratio = 0.5  # 50% of original size

        width, height = image.size
        new_size = (int(width * scale_ratio), int(height * scale_ratio))

        image = image.resize(new_size, Image.LANCZOS)

        # # Resize or compress if needed (optional but useful for speed)
        # image.thumbnail((600, 600), Image.LANCZOS)

        buffer = BytesIO()
        image.save(buffer, format='JPEG', quality=90, optimize=True)
        buffer.seek(0)

        # Encode to base64 and decode to string
        my_string = base64.b64encode(buffer.read()).decode('utf-8')
    except:
        my_string = "NAN"
    # img = str(my_string).split("b'")
    context = {

        'date': date,
        'col': col,
        'url1': "https://123dacn.in",
        'url2': "http://localhost:8000",
        'img': my_string

    }

    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = "order.pdf"
    html = render_to_string("invoice/shareOrderPDF.html", context)

    HTML(string=html).write_pdf(response, stylesheets=[CSS(string='@page { size: A5; margin: .3cm ; }')])
    return response


def generate_order_report_admin(request):
    companyID = request.GET.get('companyID')
    gDate = request.GET.get('gDate')
    date1 = datetime.strptime(gDate, '%d/%m/%Y')
    day_string = date1.strftime('%Y-%m-%d')

    company = Company.objects.select_related().get(pk=int(companyID))
    col = TakeOrder.objects.select_related().filter(datetime__icontains=day_string, companyID_id=int(companyID),
                                                    isDeleted__exact=False).exclude(
        datetime__lt=last_3_month_date).order_by('datetime')

    context = {
        'date': gDate,
        'company': company.name,
        'col': col,

    }

    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = "report.pdf"
    html = render_to_string("invoice/OrderPDFAdmin.html", context)

    HTML(string=html).write_pdf(response, stylesheets=[CSS(string='@page { size: A5;  }')])
    return response


def generate_order_report_manager(request):
    gDate = request.GET.get('gDate')
    date1 = datetime.strptime(gDate, '%d/%m/%Y')
    day_string = date1.strftime('%Y-%m-%d')
    a_list = []
    s_list = []
    user = StaffUser.objects.get(userID_id=request.user.pk)
    assigned_objs = OrderManagerStaff.objects.filter(isDeleted=False, managerID__userID_id=request.user.pk)
    for a in assigned_objs:
        if a.staffID is not None:
            a_list.append(a.staffID_id)

    assigned_stocks = ManagerAssignedStockGroup.objects.filter(isDeleted=False, managerID__userID_id=request.user.pk)
    for b in assigned_stocks:
        if b.stockGroupID is not None:
            s_list.append(b.stockGroupID.name)
    col = TakeOrder.objects.select_related().filter(datetime__icontains=day_string,
                                                    isDeleted__exact=False, orderTakenBy__in=a_list,
                                                    stockGroup__in=s_list).exclude(
        datetime__lt=last_3_month_date).order_by('datetime')

    context = {
        'name': user.name,
        'date': gDate,
        'col': col,

    }

    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = "report.pdf"
    html = render_to_string("invoice/OrderPDFManager.html", context)

    HTML(string=html).write_pdf(response, stylesheets=[CSS(string='@page { size: A5;  }')])
    return response

@csrf_exempt
def edit_invoice_by_accountant(request):
    if request.method == 'POST':
        invoiceID = request.POST.get('invoiceID')
        SalesType = request.POST.get('salesE')
        remarkE = request.POST.get('remarkE')
        try:
            sale = Sales.objects.get(pk=int(invoiceID))

            if sale.datetime.date()== datetime.today().date():
                sale.salesType = SalesType
                if SalesType == 'Cash':
                    sale.isCash = True
                if SalesType == 'Card':
                    sale.isCash = False
                    sale.remark = remarkE
                user = StaffUser.objects.select_related().get(userID_id=request.user.pk)
                sale.createdBy_id = user.pk
                sale.save()
                return JsonResponse({'message': 'success'})
            else:
                return JsonResponse({'message': 'updateError'})
        except:
            return JsonResponse({'message': 'error'})
    else:
        return JsonResponse({'message': 'error'})

