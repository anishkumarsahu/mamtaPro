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

from invoice.models import Sales
from .models import *

from django_datatables_view.base_datatable_view import BaseDatatableView
from django.utils.html import escape

import urllib.request
import urllib.parse
last_3_month_date = datetime.today().date() - timedelta(days=45)


def Balance():
    data = urllib.parse.urlencode({'apikey': 'zqc9vE5iO0U-jhurpShYlOIPyuJp1UZH6ZlFux7Kir'})
    data = data.encode('utf-8')
    request = urllib.request.Request("https://api.textlocal.in/balance/?")
    f = urllib.request.urlopen(request, data)
    fr = f.read()
    return (fr)


def login_or_logout(request, type):
    data = LoginAndLogoutStatus()
    data.statusType = type

    data.userID_id = request.user.pk
    if request.user.username !='anish':
        data.save()



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


class InvoicePrintListJson(BaseDatatableView):
    order_columns = ['billNumber', 'createdBy','amount', 'salesType',  'datetime']

    def get_initial_queryset(self):

        sDate = self.request.GET.get('startDate')
        eDate = self.request.GET.get('endDate')
        staff = self.request.GET.get('staff')
        startDate = datetime.strptime(sDate, '%d/%m/%Y')
        endDate = datetime.strptime(eDate, '%d/%m/%Y')
        if staff == 'all':
            return Sales.objects.select_related().filter(datetime__gte=startDate,
                                                         datetime__lte=endDate + timedelta(days=1),
                                                         ).exclude(salesType__exact='Card').exclude(
                datetime__lt=last_3_month_date)
        else:
            return Sales.objects.select_related().filter(datetime__gte=startDate,
                                                         datetime__lte=endDate + timedelta(days=1),
                                                         createdBy=int(staff)).exclude(salesType__exact='Card').exclude(
                datetime__lt=last_3_month_date)

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(amount__icontains=search) | Q(
                    billNumber__icontains=search) | Q(datetime__icontains=search) | Q(
                    createdBy__name__icontains=search)).order_by(
                '-id')

        return qs

    def prepare_results(self, qs):
        json_data = []
        for item in qs:
            if item.createdBy is None:
                createdBy = 'Admin'
            else:
                createdBy = item.createdBy.name

            if item.salesType == 'Mix':
                amount = item.amount+item.mixCardAmount
            else:
                amount = item.amount
            json_data.append([
                escape(item.billNumber),
                createdBy,  # escape HTML for security reasons
                escape(amount),  # escape HTML for security reasons
                escape(item.salesType),  # escape HTML for security reasons
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),


            ])
        return json_data



class LoginListJson(BaseDatatableView):
    order_columns = ['id', 'userID', 'statusType', 'datetime', ]

    def get_initial_queryset(self):

        return LoginAndLogoutStatus.objects.select_related().filter(isDeleted__exact=False,
                                                                    statusType__exact='Login').exclude(
            datetime__lt=last_3_month_date)

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(userID__username__icontains=search) | Q(statusType__icontains=search) | Q(datetime__icontains=search) , isDeleted__exact=False)

        return qs

    def prepare_results(self, qs):
        json_data = []
        i = 1
        for item in qs:
            try:
                u = item.userID.username
            except:
                u ="Admin"

            json_data.append([
                escape(i),
                u,  # escape HTML for security reasons
                escape(item.statusType),  # escape HTML for security reasons
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),


            ])
            i = i + 1
        return json_data


class LogoutListJson(BaseDatatableView):
    order_columns = ['id', 'userID', 'statusType', 'datetime', ]

    def get_initial_queryset(self):

        return LoginAndLogoutStatus.objects.select_related().filter(isDeleted__exact=False,
                                                                    statusType__exact='Logout').exclude(
            datetime__lt=last_3_month_date)

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(userID__username__icontains=search) | Q(statusType__icontains=search) | Q(datetime__icontains=search),
                isDeleted__exact=False)

        return qs

    def prepare_results(self, qs):
        json_data = []
        i = 1
        for item in qs:
            try:
                u = item.userID.username
            except:
                u ="Admin"
            json_data.append([
                escape(i),
                u,  # escape HTML for security reasons
                escape(item.statusType),  # escape HTML for security reasons
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),

            ])
            i = i + 1
        return json_data


class BuyerListJson(BaseDatatableView):
    order_columns = ['id', 'name', 'phoneNumber', 'closingBalance', 'address', ]

    def get_initial_queryset(self):

        return Buyer.objects.select_related().filter(isDeleted__exact=False)

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

        return MoneyToCollect.objects.select_related().exclude(
            datetime__lt=last_3_month_date)

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

        return MoneyToCollect.objects.select_related().filter(buyerID=int(self.request.GET.get('id'))).exclude(
            datetime__lt=last_3_month_date)

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

        return MoneyCollection.objects.select_related().filter(buyerID=int(self.request.GET.get('id'))).exclude(
            datetime__lt=last_3_month_date)

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

            try:
                name = escape(item.collectedBy.name)
            except:
                name = "Admin"
            json_data.append([
                escape(i),
                escape(item.amount),  # escape HTML for security reasons
                name,  # escape HTML for security reasons
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
            return MoneyCollection.objects.select_related().filter(datetime__gte=startDate,
                                                                   datetime__lte=endDate + timedelta(days=1),
                                                                   paymentMode__exact='Cash').exclude(
                datetime__lt=last_3_month_date)
        else:
            return MoneyCollection.objects.select_related().filter(datetime__gte=startDate,
                                                                   datetime__lte=endDate + timedelta(days=1),
                                                                   paymentMode__exact='Cash',
                                                                   collectedBy=int(staff)).exclude(
                datetime__lt=last_3_month_date)

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
            return MoneyCollection.objects.select_related().filter(datetime__gte=startDate,
                                                                   datetime__lte=endDate + timedelta(days=1),
                                                                   paymentMode__exact='Cheque').exclude(
                datetime__lt=last_3_month_date)
        else:
            return MoneyCollection.objects.select_related().filter(datetime__gte=startDate,
                                                                   datetime__lte=endDate + timedelta(days=1),
                                                                   paymentMode__exact='Cheque',
                                                                   collectedBy=int(staff)).exclude(
                datetime__lt=last_3_month_date)

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

        return Company.objects.select_related().filter(isDeleted__exact=False)

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

        return StaffUser.objects.select_related().filter(isDeleted__exact=False)

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
        sDate = self.request.GET.get('startDate')
        startDate = datetime.strptime(sDate, '%d/%m/%Y')
        return SupplierCollection.objects.select_related().filter(datetime__icontains=startDate.date(),
                                                                  collectedBy__userID_id=self.request.user.pk,
                                                                  isDeleted__exact=False).exclude(
            datetime__lt=last_3_month_date)


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


class SupplierInvoiceCollectionListJson(BaseDatatableView):
    order_columns = ['id', 'buyerID', 'amount', 'invoiceNumber', 'remark', 'datetime']

    def get_initial_queryset(self):
        sDate = self.request.GET.get('startDate')
        startDate = datetime.strptime(sDate, '%d/%m/%Y')
        return SupplierInvoiceCollection.objects.select_related().filter(datetime__icontains=startDate.date(),
                                                                         collectedBy__userID_id=self.request.user.pk,
                                                                         isDeleted__exact=False).exclude(
            datetime__lt=last_3_month_date)


    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(invoiceNumber__icontains=search) |  Q(amount__icontains=search) | Q(remark__icontains=search) | Q(datetime__icontains=search) | Q(
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
                escape(item.invoiceNumber),  # escape HTML for security reasons
                escape(item.remark),  # escape HTML for security reasons
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),

            ])
            i = i + 1
        return json_data




class SupplierCollectionListCashJson(BaseDatatableView):
    order_columns = ['id', 'buyerID.name', 'amount', 'collectedBy.name', 'remark','Location', 'datetime','action']

    def get_initial_queryset(self):

        sDate = self.request.GET.get('startDate')
        eDate = self.request.GET.get('endDate')
        staff = self.request.GET.get('staff')
        startDate = datetime.strptime(sDate, '%d/%m/%Y')
        endDate = datetime.strptime(eDate, '%d/%m/%Y')
        user = StaffUser.objects.select_related().get(userID_id=self.request.user.pk)
        if staff == 'all':
            return SupplierCollection.objects.select_related().filter(datetime__gte=startDate,
                                                                      datetime__lte=endDate + timedelta(days=1),
                                                                      paymentMode__exact='Cash',
                                                                      collectedBy__companyID_id=user.companyID_id,
                                                                      isDeleted__exact=False).exclude(
                datetime__lt=last_3_month_date)
        else:
            return SupplierCollection.objects.select_related().filter(datetime__gte=startDate,
                                                                      datetime__lte=endDate + timedelta(days=1),
                                                                      paymentMode__exact='Cash',
                                                                      collectedBy__companyID_id=user.companyID_id,
                                                                      isDeleted__exact=False,
                                                                      collectedBy=int(staff)).exclude(
                datetime__lt=last_3_month_date)

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(Location__icontains=search) | Q(amount__icontains=search) | Q(remark__icontains=search) | Q(datetime__icontains=search) | Q(
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
                escape(item.Location),  # escape HTML for security reasons
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),
                button

            ])
            i = i + 1
        return json_data



class SupplierCollectionAdminListCashJson(BaseDatatableView):
    order_columns = ['id', 'buyerID.name', 'amount', 'collectedBy.name','approvedBy', 'remark','Location', 'datetime','action','action1']

    def get_initial_queryset(self):

        sDate = self.request.GET.get('startDate')
        eDate = self.request.GET.get('endDate')
        staff = self.request.GET.get('staff')
        startDate = datetime.strptime(sDate, '%d/%m/%Y')
        endDate = datetime.strptime(eDate, '%d/%m/%Y')
        if staff == 'all':
            return SupplierCollection.objects.select_related().filter(datetime__gte=startDate,
                                                                      datetime__lte=endDate + timedelta(days=1),
                                                                      paymentMode__exact='Cash',
                                                                      isDeleted__exact=False).exclude(
                datetime__lt=last_3_month_date)
        else:
            return SupplierCollection.objects.select_related().filter(datetime__gte=startDate,
                                                                      datetime__lte=endDate + timedelta(days=1),
                                                                      paymentMode__exact='Cash', isDeleted__exact=False,
                                                                      collectedBy=int(staff)).exclude(
                datetime__lt=last_3_month_date)

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(Location__icontains=search) | Q(amount__icontains=search) | Q(remark__icontains=search) | Q(datetime__icontains=search) | Q(
                    collectedBy__name__icontains=search)| Q(
                    buyerID__name__icontains=search)).order_by(
                '-id')

        return qs

    def prepare_results(self, qs):
        json_data = []
        i = 1
        for item in qs:
            action = '''<span><a onclick="getSupplierDetail('{}','{}','{}','{}','{}','{}')" class="hideModerator" ><button style="background-color: #3F51B5;color: white;" type="button"
                                       class="btn  waves-effect " data-toggle="modal"
                                       data-target="#CollectionModal">
                                   <i class="material-icons">border_color</i></button> </a>



                               <button onclick="deleteCollection('{}')" style="background-color: #e91e63;color: white;" type="button" class="btn  waves-effect " data-toggle="modal" data-target="#defaultModal">


                                                                <i class="material-icons">delete</i></button></span>'''.format(
                item.pk, item.buyerID.name,item.buyerID.pk, item.amount, item.paymentMode, item.remark, item.pk)

            if item.isApproved == False:
                button = '''
                 <button type="button" class="btn btn-primary waves-effect" data-toggle="modal"
                           data-target="#defaultModalApprove" onclick="approveCollection({})">PENDING</button>'''.format(item.pk)
            else:
                button = '''<button type="button" class="btn btn-success waves-effect">APPROVED</button>'''

            json_data.append([
                escape(i),
                escape(item.buyerID.name),
                escape(item.amount),  # escape HTML for security reasons
                escape(item.collectedBy.name),  # escape HTML for security reasons
                escape(item.approvedBy),  # escape HTML for security reasons
                escape(item.remark),  # escape HTML for security reasons
                escape(item.Location),  # escape HTML for security reasons
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),
                button,
                action

            ])
            i = i + 1
        return json_data


class SupplierCollectionAdminListChequeJson(BaseDatatableView):
    order_columns = ['id', 'buyerID.name', 'amount', 'collectedBy.name', 'approvedBy', 'remark','Location', 'datetime','action', 'action1']

    def get_initial_queryset(self):

        sDate = self.request.GET.get('startDate')
        eDate = self.request.GET.get('endDate')
        staff = self.request.GET.get('staff')
        startDate = datetime.strptime(sDate, '%d/%m/%Y')
        endDate = datetime.strptime(eDate, '%d/%m/%Y')

        if staff == 'all':
            return SupplierCollection.objects.select_related().filter(datetime__gte=startDate,
                                                                      datetime__lte=endDate + timedelta(days=1),
                                                                      paymentMode__exact='Cheque',
                                                                      isDeleted__exact=False).exclude(
                datetime__lt=last_3_month_date)
        else:
            return SupplierCollection.objects.select_related().filter(datetime__gte=startDate,
                                                                      datetime__lte=endDate + timedelta(days=1),
                                                                      paymentMode__exact='Cheque',
                                                                      isDeleted__exact=False,
                                                                      collectedBy=int(staff)).exclude(
                datetime__lt=last_3_month_date)

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(Location__icontains=search) |Q(amount__icontains=search) | Q(remark__icontains=search) | Q(datetime__icontains=search) | Q(
                    collectedBy__name__icontains=search)| Q(
                    buyerID__name__icontains=search)).order_by(
                '-id')

        return qs

    def prepare_results(self, qs):
        json_data = []
        i = 1
        for item in qs:
            action = '''<span><a onclick="getSupplierDetail('{}','{}','{}','{}','{}','{}')" class="hideModerator" ><button style="background-color: #3F51B5;color: white;" type="button"
                                              class="btn  waves-effect " data-toggle="modal"
                                              data-target="#CollectionModal">
                                          <i class="material-icons">border_color</i></button> </a>



                                      <button onclick="deleteCollection('{}')" style="background-color: #e91e63;color: white;" type="button" class="btn  waves-effect " data-toggle="modal" data-target="#defaultModal">


                                                                       <i class="material-icons">delete</i></button></span>'''.format(
                item.pk, item.buyerID.name, item.buyerID.pk, item.amount, item.paymentMode, item.remark, item.pk)

            if item.isApproved == False:
                button = '''
                <button type="button" class="btn btn-primary waves-effect" data-toggle="modal"
                           data-target="#defaultModalApprove" onclick="approveCollection({})">PENDING</button>'''.format(item.pk)
            else:
                button = '''<button type="button" class="btn btn-success waves-effect">APPROVED</button>'''

            json_data.append([
                escape(i),
                escape(item.buyerID.name),
                escape(item.amount),  # escape HTML for security reasons
                escape(item.collectedBy.name),  # escape HTML for security reasons
                escape(item.approvedBy),  # escape HTML for security reasons
                escape(item.remark),  # escape HTML for security reasons
                escape(item.Location),  # escape HTML for security reasons
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),
                button,
                action

            ])
            i = i + 1
        return json_data


class SupplierCollectionListChequeJson(BaseDatatableView):
    order_columns = ['id', 'buyerID.name', 'amount', 'collectedBy.name', 'remark','Location', 'datetime','action']

    def get_initial_queryset(self):

        sDate = self.request.GET.get('startDate')
        eDate = self.request.GET.get('endDate')
        staff = self.request.GET.get('staff')
        startDate = datetime.strptime(sDate, '%d/%m/%Y')
        endDate = datetime.strptime(eDate, '%d/%m/%Y')

        user = StaffUser.objects.select_related().get(userID_id=self.request.user.pk)
        if staff == 'all':
            return SupplierCollection.objects.select_related().filter(datetime__gte=startDate,
                                                                      datetime__lte=endDate + timedelta(days=1),
                                                                      paymentMode__exact='Cheque',
                                                                      collectedBy__companyID_id=user.companyID_id,
                                                                      isDeleted__exact=False).exclude(
                datetime__lt=last_3_month_date)
        else:
            return SupplierCollection.objects.select_related().filter(datetime__gte=startDate,
                                                                      datetime__lte=endDate + timedelta(days=1),
                                                                      paymentMode__exact='Cheque',
                                                                      isDeleted__exact=False,
                                                                      collectedBy=int(staff),
                                                                      collectedBy__companyID_id=user.companyID_id).exclude(
                datetime__lt=last_3_month_date)

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(Location__icontains=search) | Q(amount__icontains=search) | Q(remark__icontains=search) | Q(datetime__icontains=search) | Q(
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
                escape(item.Location),  # escape HTML for security reasons
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),
                button

            ])
            i = i + 1
        return json_data


class SupplierCollectionInvoiceList(BaseDatatableView):
    order_columns = ['id', 'buyerID.name', 'amount','invoiceNumber', 'collectedBy.name', 'remark','Location', 'datetime','action']

    def get_initial_queryset(self):

        sDate = self.request.GET.get('startDate')
        eDate = self.request.GET.get('endDate')
        staff = self.request.GET.get('staff')
        startDate = datetime.strptime(sDate, '%d/%m/%Y')
        endDate = datetime.strptime(eDate, '%d/%m/%Y')

        user = StaffUser.objects.select_related().get(userID_id=self.request.user.pk)
        if staff == 'all':
            return SupplierInvoiceCollection.objects.select_related().filter(datetime__gte=startDate,
                                                                             datetime__lte=endDate + timedelta(days=1),
                                                                             collectedBy__companyID_id=user.companyID_id,
                                                                             isDeleted__exact=False).exclude(
                datetime__lt=last_3_month_date)
        else:
            return SupplierInvoiceCollection.objects.select_related().filter(datetime__gte=startDate,
                                                                             datetime__lte=endDate + timedelta(days=1),
                                                                             isDeleted__exact=False,
                                                                             collectedBy=int(staff),
                                                                             collectedBy__companyID_id=user.companyID_id).exclude(
                datetime__lt=last_3_month_date)

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(invoiceNumber__icontains=search) | Q(Location__icontains=search) | Q(amount__icontains=search) | Q(remark__icontains=search) | Q(datetime__icontains=search) | Q(
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
                           data-target="#defaultModalInvoice" onclick="approveCollectionInvoice({})">PENDING</button>'''.format(item.pk)
            else:
                button = '''<button type="button" class="btn btn-success waves-effect">APPROVED</button>'''

            json_data.append([
                escape(i),
                escape(item.buyerID.name),
                escape(item.amount),  # escape HTML for security reasons
                escape(item.invoiceNumber),  # escape HTML for security reasons
                escape(item.collectedBy.name),  # escape HTML for security reasons
                escape(item.remark),  # escape HTML for security reasons
                escape(item.Location),  # escape HTML for security reasons
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),
                button

            ])
            i = i + 1
        return json_data


class SupplierCollectionInvoiceListAdmin(BaseDatatableView):
    order_columns = ['id', 'buyerID.name', 'amount','invoiceNumber','approvedBy', 'collectedBy.name', 'remark','Location', 'datetime','action']

    def get_initial_queryset(self):

        sDate = self.request.GET.get('startDate')
        eDate = self.request.GET.get('endDate')
        staff = self.request.GET.get('staff')
        startDate = datetime.strptime(sDate, '%d/%m/%Y')
        endDate = datetime.strptime(eDate, '%d/%m/%Y')

        if staff == 'all':
            return SupplierInvoiceCollection.objects.select_related().filter(datetime__gte=startDate,
                                                                             datetime__lte=endDate + timedelta(days=1),
                                                                             isDeleted__exact=False).exclude(
                datetime__lt=last_3_month_date)
        else:
            return SupplierInvoiceCollection.objects.select_related().filter(datetime__gte=startDate,
                                                                             datetime__lte=endDate + timedelta(days=1),
                                                                             isDeleted__exact=False,
                                                                             collectedBy=int(staff)).exclude(
                datetime__lt=last_3_month_date)

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(invoiceNumber__icontains=search) | Q(Location__icontains=search) | Q(amount__icontains=search) | Q(remark__icontains=search) | Q(datetime__icontains=search) | Q(
                    collectedBy__name__icontains=search)| Q(
                    buyerID__name__icontains=search)).order_by(
                '-id')

        return qs

    def prepare_results(self, qs):
        json_data = []
        i = 1
        for item in qs:

            action = '''<span><a onclick="getSupplierDetail('{}','{}','{}','{}','{}','{}')" class="hideModerator" ><button style="background-color: #3F51B5;color: white;" type="button"
                                                  class="btn  waves-effect " data-toggle="modal"
                                                  data-target="#CollectionModalIn">
                                              <i class="material-icons">border_color</i></button> </a>



                                          <button onclick="deleteCollectionIn('{}')" style="background-color: #e91e63;color: white;" type="button" class="btn  waves-effect " data-toggle="modal" data-target="#defaultModalIn">


                                                                           <i class="material-icons">delete</i></button></span>'''.format(
                item.pk, item.buyerID.name, item.buyerID.pk, item.amount, item.invoiceNumber, item.remark, item.pk)

            if item.isApproved == False:
                button = '''
                <button type="button" class="btn btn-primary waves-effect" data-toggle="modal"
                           data-target="#defaultModalInvoice" onclick="approveCollectionInvoice({})">PENDING</button>'''.format(item.pk)
            else:
                button = '''<button type="button" class="btn btn-success waves-effect">APPROVED</button>'''

            json_data.append([
                escape(i),
                escape(item.buyerID.name),
                escape(item.amount),  # escape HTML for security reasons
                escape(item.invoiceNumber),  # escape HTML for security reasons
                escape(item.approvedBy),  # escape HTML for security reasons
                escape(item.collectedBy.name),  # escape HTML for security reasons
                escape(item.remark),  # escape HTML for security reasons
                escape(item.Location),  # escape HTML for security reasons
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),
                button,
                action

            ])
            i = i + 1
        return json_data



@check_group('Both')
def home(request):
    try:
        b = json.loads(Balance().decode('utf-8'))
        bal = b['balance']['sms']
    except:
        bal = 0
    request.session['nav'] = '1'
    staff = StaffUser.objects.select_related().filter(isDeleted__exact=False).count()
    buyer = Buyer.objects.select_related().filter(isDeleted__exact=False).count()
    credit = MoneyCollection.objects.select_related().filter(datetime__icontains=datetime.today().date()).aggregate(
        Sum('amount'))
    due = Buyer.objects.select_related().aggregate(Sum('closingBalance'))
    date_list = []
    credit_list = []
    for i in range(11):
        c = MoneyCollection.objects.select_related().filter(
            datetime__icontains=datetime.today().date() - timedelta(i)).aggregate(Sum('amount'))
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
        'sms':bal,
    }

    return render(request, 'mamtaApp/index.html',context)


# --------------------------staffs -----------------------------------------------------------------
@check_group('Both')
def staff(request):
    request.session['nav'] = '2'
    users = StaffUser.objects.select_related().filter(isDeleted__exact=False).order_by('name')

    context = {
        'users': users
    }
    return render(request, 'mamtaApp/staffs.html', context)


@check_group('Both')
def add_staff(request):
    staffType = StaffType.objects.select_related().all()
    company = Company.objects.select_related().filter(isDeleted__exact=False)
    context = {
        'types': staffType,
        'company': company
    }
    return render(request, 'mamtaApp/addStaff.html', context)


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
    staffType = StaffType.objects.select_related().all()
    company = Company.objects.select_related().filter(isDeleted__exact=False)

    context = {
        'instance': instance,
        'types': staffType,
        'company': company
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
            username = request.POST.get('username')
            password = request.POST.get('password')
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

            staff.username = username
            staff.password = password
            new_user = User()
            new_user.username = username
            new_user.set_password(password)

            new_user.save()

            staff.userID_id = new_user.pk
            if staffType == '1':
                try:
                    g = Group.objects.select_related().get(name='Staff')
                    g.user_set.add(new_user.pk)
                    g.save()
                    h = Group.objects.select_related().get(name='Collection')
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
                    g = Group.objects.select_related().get(name='Staff')
                    g.user_set.add(new_user.pk)
                    g.save()
                    h = Group.objects.select_related().get(name='Sales')
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
                    h = Group.objects.select_related().get(name='Accountant')
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
                    h = Group.objects.select_related().get(name='Supply')
                    h.user_set.add(new_user.pk)
                    h.save()

                except:
                    h = Group()
                    h.name = "Supply"
                    h.save()
                    h.user_set.add(new_user.pk)
                    h.save()
            elif staffType =='5':
                try:
                    h = Group.objects.select_related().get(name='Cashier')
                    h.user_set.add(new_user.pk)
                    h.save()

                except:
                    h = Group()
                    h.name = "Cashier"
                    h.save()
                    h.user_set.add(new_user.pk)
                    h.save()
            elif staffType =='6':
                try:
                    h = Group.objects.select_related().get(name='Order Team')
                    h.user_set.add(new_user.pk)
                    h.save()

                except:
                    h = Group()
                    h.name = "Order Team"
                    h.save()
                    h.user_set.add(new_user.pk)
                    h.save()
            else:
                try:
                    g = Group.objects.select_related().get(name='Staff')
                    g.user_set.add(new_user.pk)
                    g.save()
                    h = Group.objects.select_related().get(name='Normal')
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

            staff = StaffUser.objects.select_related().get(pk=int(userID))
            staff.name = name
            staff.phoneNumber = phoneNumber
            staff.address = address
            staff.isActive = isActive
            staff.staffTypeID_id = int(staffType)
            staff.canTakePayment = canTakePayment
            staff.companyID_id = int(companyID)
            staff.password = password
            user = User.objects.select_related().get(id=staff.userID_id)
            if isActive == 'True':
                user.is_active = True
            else:
                user.is_active = False
            if staffType == '1':
                new_user = User.objects.select_related().get(pk=staff.userID_id)
                new_user.groups.clear()
                new_user.save()
                g = Group.objects.select_related().get(name='Staff')
                g.user_set.add(new_user.pk)
                g.save()
                h = Group.objects.select_related().get(name='Collection')
                h.user_set.add(new_user.pk)
                h.save()
            elif staffType == '2':
                new_user = User.objects.select_related().get(pk=staff.userID_id)
                new_user.groups.clear()
                new_user.save()
                g = Group.objects.select_related().get(name='Staff')
                g.user_set.add(new_user.pk)
                g.save()
                h = Group.objects.select_related().get(name='Sales')
                h.user_set.add(new_user.pk)
                h.save()
            elif staffType == '3':
                new_user = User.objects.select_related().get(pk=staff.userID_id)
                new_user.groups.clear()
                new_user.save()
                h = Group.objects.select_related().get(name='Accountant')
                h.user_set.add(new_user.pk)
                h.save()
            elif staffType == '4':
                new_user = User.objects.select_related().get(pk=staff.userID_id)
                new_user.groups.clear()
                new_user.save()
                h = Group.objects.select_related().get(name='Supply')
                h.user_set.add(new_user.pk)
                h.save()
            elif staffType == '5':
                new_user = User.objects.select_related().get(pk=staff.userID_id)
                new_user.groups.clear()
                new_user.save()
                h = Group.objects.select_related().get(name='Cashier')
                h.user_set.add(new_user.pk)
                h.save()
            elif staffType == '6':
                new_user = User.objects.select_related().get(pk=staff.userID_id)
                new_user.groups.clear()
                new_user.save()
                h = Group.objects.select_related().get(name='Order Team')
                h.user_set.add(new_user.pk)
                h.save()
            else :
                new_user = User.objects.select_related().get(pk=staff.userID_id)
                new_user.groups.clear()
                new_user.save()
                g = Group.objects.select_related().get(name='Staff')
                g.user_set.add(new_user.pk)
                g.save()
                h = Group.objects.select_related().get(name='Normal')
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
            staff = StaffUser.objects.select_related().get(pk=int(userID))
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

            staff = StaffUser.objects.select_related().get(pk=int(userID))
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
            staff = StaffUser.objects.select_related().get(pk=int(userID))
            staff.isDeleted = True
            staff.isActive = False
            user = User.objects.select_related().get(id=staff.userID_id)
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
    users = Buyer.objects.select_related().filter(isDeleted__exact=False).order_by('name')

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

            buyer = Buyer.objects.select_related().get(pk=int(buyerID))
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
            buyer = Buyer.objects.select_related().get(pk=int(buyerID))
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
            buyer = Buyer.objects.select_related().get(pk=int(buyerID))
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
            money = MoneyToCollect.objects.select_related().get(int(moneyID))
            previousMoney = money.amount
            money.amount = float(amount)
            money.save()
            buyer = Buyer.objects.select_related().get(pk=int(buyerID))
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
            money = MoneyToCollect.objects.select_related().get(pk=int(moneyID))
            money.isDeleted = True
            money.save()
            buyer = Buyer.objects.select_related().get(pk=int(money.buyerID_id))
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
    users = StaffUser.objects.select_related().filter(isDeleted__exact=False).order_by('name')
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
    users = Buyer.objects.select_related().filter(isDeleted__exact=False).order_by('name')
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
            login_or_logout(request, 'Login')
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
            if 'Cashier' in request.user.groups.values_list('name', flat=True):
                return redirect('/cashierHome/')
            if 'Order Team' in request.user.groups.values_list('name', flat=True):
                return redirect('/order_home/')

        else:
            messages.success(request, "Wrong Credential! Please try again.")

            return render(request, "mamtaApp/login.html", {})
    return render(request, 'mamtaApp/login.html')


def logout_user(request):
    request.session['nav'] = '7'
    login_or_logout(request, 'Logout')
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
            data = Admin.objects.select_related().get(userID_id=request.user.pk)
            data.password = password
            data.save()
            user = User.objects.select_related().get(pk=request.user.pk)
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
    users = Buyer.objects.select_related().filter(isDeleted__exact=False).order_by('name')
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
                comp = Company.objects.select_related().get(name__iexact=Cname)
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
        # comp = Company.objects.select_related().all().exclude(pk = int(ECID))
            try:
                comp = Company.objects.select_related().exclude(pk=int(ECID)).get(name__iexact=ECname)
                messages.success(request, 'Company name already exist. Please try again with again with different name.')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            except:

                obj = Company.objects.select_related().get(pk=int(ECID))
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

    user = StaffUser.objects.select_related().get(userID_id=request.user.pk)
    date = datetime.today().now().strftime('%d/%m/%Y')

    context = {
        'user':user,
        'date': date,
    }

    return render(request, 'mamtaApp/supply/supplyIndex.html', context)


@check_group('Cashier')
def cashier_home(request):
    request.session['nav'] = '9'

    user = StaffUser.objects.select_related().get(userID_id=request.user.pk)
    users = StaffUser.objects.select_related().filter(isDeleted__exact=False, companyID_id=user.companyID_id).order_by(
        'name')
    date = datetime.today().now().strftime('%d/%m/%Y')
    context = {
        'users': users,
        'date': date,
        'user': user
    }

    return render(request, 'mamtaApp/cashier/cashierIndex.html', context)

@csrf_exempt
def take_collection_supplier_api(request):
    if request.method == 'POST':

        CustomerCol = request.POST.get('CustomerCol')
        AmountCol = request.POST.get('AmountCol')
        PayMethodCol = request.POST.get('PayMethodCol')
        RemarkCol = request.POST.get('RemarkCol')
        lat = request.POST.get('lat')
        lng = request.POST.get('lng')
        loc = request.POST.get('loc')

        try:
            collection = SupplierCollection()
            collection.buyerID_id = int(CustomerCol)
            collection.amount = float(AmountCol)
            user = StaffUser.objects.select_related().get(userID_id=request.user.pk)
            collection.collectedBy_id = user.pk
            collection.paymentMode = PayMethodCol
            collection.remark = RemarkCol
            collection.companyID_id = user.companyID_id
            collection.lat = lat
            collection.lng = lng
            collection.Location = loc

            collection.save()

            return JsonResponse({'message': 'success'})

        except:
            return JsonResponse({'message': 'fail'})


@csrf_exempt
def take_collection_invoice_supplier_api(request):
    if request.method == 'POST':

        CustomerCol = request.POST.get('CustomerCol')
        AmountCol = request.POST.get('AmountCol')
        inv = request.POST.get('Invoice')
        RemarkCol = request.POST.get('RemarkCol')
        lat = request.POST.get('lat')
        lng = request.POST.get('lng')
        loc = request.POST.get('loc')

        try:
            collection = SupplierInvoiceCollection()
            collection.buyerID_id = int(CustomerCol)
            collection.amount = float(AmountCol)
            user = StaffUser.objects.select_related().get(userID_id=request.user.pk)
            collection.collectedBy_id = user.pk
            collection.invoiceNumber = inv
            collection.remark = RemarkCol
            collection.companyID_id = user.companyID_id
            collection.lat = lat
            collection.lng = lng
            collection.Location = loc
            collection.save()

            return JsonResponse({'message': 'success'})

        except:
            return JsonResponse({'message': 'fail'})



@csrf_exempt
def edit_collection_supplier_api(request):
    if request.method == 'POST':

        supID = request.POST.get('supID')
        CustomerCol = request.POST.get('CustomerCol')
        AmountCol = request.POST.get('AmountCol')
        PayMethodCol = request.POST.get('PayMethodCol')
        RemarkCol = request.POST.get('RemarkCol')

        try:
            collection = SupplierCollection.objects.select_related().get(pk=int(supID))
            collection.buyerID_id = int(CustomerCol)
            collection.amount = float(AmountCol)
            collection.paymentMode = PayMethodCol
            collection.remark = RemarkCol
            collection.save()

            return JsonResponse({'message': 'success'})

        except:
            return JsonResponse({'message': 'fail'})

@check_group('Both')
def supplier_collection_report(request):
    request.session['nav'] = '55'
    users = StaffUser.objects.select_related().filter(isDeleted__exact=False).order_by('name')
    date = datetime.today().now().strftime('%d/%m/%Y')
    context = {
        'users': users,
        'date': date
    }
    return render(request, 'mamtaApp/supply/SupplierCollectionReport.html', context)


@check_group('Both')
def print_report(request):
    request.session['nav'] = '56'
    users = StaffUser.objects.select_related().filter(isDeleted__exact=False).order_by('name')
    date = datetime.today().now().strftime('%d/%m/%Y')
    context = {
        'users': users,
        'date': date
    }
    return render(request, 'mamtaApp/PrintLogReport.html', context)


@csrf_exempt
def approve_collection_supplier_api(request):
    if request.method == 'POST':

        collectionID = request.POST.get('collectionID')


        try:
            collection = SupplierCollection.objects.select_related().get(pk=int(collectionID))
            collection.isApproved = True
            user = StaffUser.objects.select_related().get(userID_id=request.user.pk)
            collection.approvedBy = user.name
            collection.save()
            buy = Buyer.objects.select_related().get(pk=int(collection.buyerID.pk))
            buy.closingBalance = buy.closingBalance - float(collection.amount)
            buy.save()
            return JsonResponse({'message': 'success'})

        except:
            return JsonResponse({'message': 'fail'})



@csrf_exempt
def approve_collection_supplier_invoice_api(request):
    if request.method == 'POST':

        collectionID = request.POST.get('collectionID')


        try:
            collection = SupplierInvoiceCollection.objects.select_related().get(pk=int(collectionID))
            collection.isApproved = True
            user = StaffUser.objects.select_related().get(userID_id=request.user.pk)
            collection.approvedBy = user.name
            collection.save()
            buy = Buyer.objects.select_related().get(pk=int(collection.buyerID.pk))
            buy.closingBalance = buy.closingBalance - float(collection.amount)
            buy.save()
            return JsonResponse({'message': 'success'})

        except:
            return JsonResponse({'message': 'fail'})




@csrf_exempt
def delete_collection_supplier_api(request):
    if request.method == 'POST':

        collectionID = request.POST.get('collectionID')


        try:
            collection = SupplierCollection.objects.select_related().get(pk=int(collectionID))
            collection.isDeleted = True
            collection.save()
            buy = Buyer.objects.select_related().get(pk=int(collection.buyerID.pk))
            buy.closingBalance = buy.closingBalance - float(collection.amount)
            buy.save()
            return JsonResponse({'message': 'success'})

        except:
            return JsonResponse({'message': 'fail'})

@csrf_exempt
def delete_collection_supplier_invoice_api(request):
    if request.method == 'POST':

        collectionID = request.POST.get('collectionID')


        try:
            collection = SupplierInvoiceCollection.objects.select_related().get(pk=int(collectionID))
            collection.isDeleted = True
            collection.save()
            buy = Buyer.objects.select_related().get(pk=int(collection.buyerID.pk))
            buy.closingBalance = buy.closingBalance - float(collection.amount)
            buy.save()
            return JsonResponse({'message': 'success'})

        except:
            return JsonResponse({'message': 'fail'})


def user_name_exist(request, *args, **kwargs):
    username = request.GET.get('q')
    try:

        user = User.objects.select_related().get(username__iexact=username)
        return JsonResponse({'message': 'Username already taken. Please try some other name.','canUse':'No'})
    except:
        return JsonResponse({'message': 'Username available.','canUse':'Yes'})

@check_group('Both')
def login_and_logout_report(request):
    request.session['nav'] = '10'

    return render(request, 'mamtaApp/loginAndLogoutReport.html')


# -------------------Order Team--------------------------------------
@check_group('Order Team')
def order_home(request):
    user = StaffUser.objects.select_related().get(userID_id=request.user.pk)
    date = datetime.today().now().strftime('%d/%m/%Y')

    context = {
        'user':user,
        'date': date,
    }

    return render(request, 'mamtaApp/order/orderIndex.html', context)

@csrf_exempt
def take_order_api(request):
    if request.method == 'POST':

        orderFrom = request.POST.get('orderFrom')
        detail = request.POST.get('detail')

        lat = request.POST.get('lat')
        lng = request.POST.get('lng')
        loc = request.POST.get('loc')
        remark = request.POST.get('remark')
        partyName = request.POST.get('partyName')

        try:
            obj = TakeOrder()
            obj.orderTakenFrom = orderFrom
            try:
                images = request.FILES['img']
                obj.orderPic = images
            except:
                pass
            user = StaffUser.objects.select_related().get(userID_id=request.user.pk)
            obj.orderTakenBy_id = user.pk
            obj.details = detail
            obj.companyID_id = user.companyID_id
            obj.lat = lat
            obj.lng = lng
            obj.location = loc
            obj.remark = remark
            obj.partyName = partyName

            obj.save()

            return JsonResponse({'message': 'success'})

        except:
            return JsonResponse({'message': 'fail'})


class OrderListByUserPerDayJson(BaseDatatableView):
    order_columns = ['id', 'partyName', 'orderTakenFrom', 'details', 'remark', 'datetime']

    def get_initial_queryset(self):
        sDate = self.request.GET.get('startDate')
        startDate = datetime.strptime(sDate, '%d/%m/%Y')
        return TakeOrder.objects.select_related().filter(datetime__icontains=startDate.date(),
                                                                  orderTakenBy__userID_id=self.request.user.pk,
                                                                  isDeleted__exact=False).exclude(
            datetime__lt=last_3_month_date)


    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(partyName__icontains=search) | Q(orderTakenFrom__icontains=search) | Q(details__icontains=search) | Q(
                    datetime__icontains=search) |
                Q(remark__icontains=search))

        return qs

    def prepare_results(self, qs):
        json_data = []
        i = 1
        for item in qs:
            button = '''<a href="/invoice/share_order_to_whatsapp_pdf/?ID={}" type="button" class="btn btn-primary waves-effect"
                             >Share</a>'''.format(
                item.pk)

            json_data.append([
                escape(i),
                escape(item.partyName),
                escape(item.orderTakenFrom),
                escape(item.details),  # escape HTML for security reasons
                escape(item.remark),  # escape HTML for security reasons
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),
                button

            ])
            i = i + 1
        return json_data

class OrderListAdminJson(BaseDatatableView):
    order_columns = ['id', 'partyName', 'orderTakenFrom', 'details','location', 'orderTakenBy', 'datetime','remark']

    def get_initial_queryset(self):

        sDate = self.request.GET.get('startDate')
        eDate = self.request.GET.get('endDate')
        staff = self.request.GET.get('staff')
        startDate = datetime.strptime(sDate, '%d/%m/%Y')
        endDate = datetime.strptime(eDate, '%d/%m/%Y')
        if staff == 'all':
            return TakeOrder.objects.select_related().filter(datetime__gte=startDate,
                                                                      datetime__lte=endDate + timedelta(days=1),
                                                                      isDeleted__exact=False).exclude(
                datetime__lt=last_3_month_date)
        else:
            return TakeOrder.objects.select_related().filter(datetime__gte=startDate,
                                                                      datetime__lte=endDate + timedelta(days=1), isDeleted__exact=False,
                                                                      orderTakenBy=int(staff)).exclude(
                datetime__lt=last_3_month_date)
    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(partyName__icontains=search) | Q(orderTakenFrom__icontains=search) | Q(details__icontains=search) | Q(
                    datetime__icontains=search) |
                Q(location__icontains=search)| Q(orderTakenBy__name__icontains=search)|
                Q(remark__icontains=search))

        return qs

    def prepare_results(self, qs):
        json_data = []
        i = 1
        for item in qs:
            button = '''<a href="/invoice/share_order_to_whatsapp_pdf/?ID={}" type="button" class="btn btn-primary waves-effect"
                             >Share</a>'''.format(
                item.pk)

            json_data.append([
                escape(i),
                escape(item.partyName),
                escape(item.orderTakenFrom),
                escape(item.details),  # escape HTML for security reasons
                escape(item.location),  # escape HTML for security reasons
                escape(item.orderTakenBy),  # escape HTML for security reasons
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),
                escape(item.remark),
                button

            ])
            i = i + 1
        return json_data



# ---------------Order List-------------

def order_list_admin(request):
    request.session['nav'] = 'o_l'
    users = StaffUser.objects.select_related().filter(isDeleted__exact=False).order_by('name')
    date = datetime.today().now().strftime('%d/%m/%Y')
    context = {
        'users': users,
        'date': date
    }
    return render(request, 'mamtaApp/order/OrderReport.html', context)

