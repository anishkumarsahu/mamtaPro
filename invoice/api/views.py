from django.contrib.auth import authenticate
from django.http import JsonResponse
from rest_framework_jwt.serializers import JSONWebTokenSerializer, jwt_encode_handler, jwt_payload_handler
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.response import Response

from .serializers import *
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework_jwt.settings import api_settings

jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
from django.contrib.auth.models import Group
from invoice.models import *
from datetime import datetime, timedelta


class InvoiceSeriesView(APIView):
    '''
    {"message":"success","data":{
                    'Series':obj.series,
                    'SeriesID':obj.pk
                }}
    '''

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            invoiceSerial = InvoiceSeries.objects.select_related().all().order_by('series')
            in_list = []
            for obj in invoiceSerial:
                in_dic = {
                    'Series': obj.series,
                    'SeriesID': obj.pk
                }

                in_list.append(in_dic)

            return Response({'message': 'success', 'data': in_list})
        except:
            return Response({'message': 'fail'})


class InvoiceSerialsView(APIView):
    '''
    {'data':{
            'Used':[{
                        'Serial':numbers.serials,
                        'SerialID':numbers.pk
                    }],
            'UnUsed':[{
                        'Serial':numbers.serials,
                        'SerialID':numbers.pk
                    }],
            'Upcoming': [{
                        'Serial':numbers.serials,
                        'SerialID':numbers.pk
                    }],
        

        }}
    '''

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        invoiceByUser = InvoiceSeries.objects.select_related().get(assignedTo__userID_id=request.user.pk)

        salesID = Sales.objects.select_related().filter(invoiceSerialID__invoiceSeriesID_id=invoiceByUser.pk,
                                                        datetime__gte=datetime.today().date() - timedelta(
                                                            days=1)).order_by(
            '-invoiceSerialID')

        last_used_invoice_number = salesID.first()

        # used
        used_invoice_id_list = []
        un_used_invoice_id_list = []
        for numbers in InvoiceSerial.objects.select_related().filter(
                series__lt=last_used_invoice_number.invoiceSerialID.serials):
            for sale in salesID:
                if numbers.pk == sale.invoiceSerialID_id:

                    used_invoice_id_dic = {
                        'Serial': numbers.serials,
                        'SerialID': numbers.pk
                    }

                    used_invoice_id_list.append(used_invoice_id_dic)
                else:
                    un_used_invoice_id_dic = {
                        'Serial': numbers.serials,
                        'SerialID': numbers.pk
                    }

                    un_used_invoice_id_list.append(un_used_invoice_id_dic)
        upcoming_serials_invoice_id_list = []
        for obj in InvoiceSerial.objects.select_related().filter(
                series__gt=last_used_invoice_number.invoiceSerialID.serials):
            upcoming_serials_invoice_id_dic = {
                'Serial': obj.serials,
                'SerialID': obj.pk
            }

            upcoming_serials_invoice_id_list.append(upcoming_serials_invoice_id_dic)

        data = {
            'Used': used_invoice_id_list,
            'UnUsed': un_used_invoice_id_list,
            'Upcoming': upcoming_serials_invoice_id_list,

        }

        return Response({'data': data})


class CreateSalesPostView(APIView):
    serializer_class = CreateInvoiceSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateInvoiceSerializer(data=request.data)
        if serializer.is_valid():
            InvoiceSerialID = request.data.get('InvoiceSerialID')
            BillNumber = request.data.get('BillNumber')
            SalesType = request.data.get('SalesType')
            Amount = request.data.get('Amount')
            CustomerName = request.data.get('CustomerName')

            sale = Sales()
            sale.invoiceSerialID_id = int(InvoiceSerialID)
            sale.billNumber = BillNumber
            sale.salesType = SalesType
            sale.amount = float(Amount)
            sale.customerName = CustomerName
            if SalesType == 'Cash':
                sale.isCash = True
            if SalesType == 'Cheque':
                sale.isCash = False

            user = StaffUser.objects.select_related().get(userID_id=request.user.pk)
            sale.createdBy_id = user.pk
            sale.save()
            return Response({'message': 'success'})
        else:
            return Response({'message': 'fail'})
