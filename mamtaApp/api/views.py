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
from mamtaApp.models import *
from datetime import datetime, timedelta

import urllib.request
import urllib.parse
import json
api_key = 'zqc9vE5iO0U-jhurpShYlOIPyuJp1UZH6ZlFux7Kir'

sender = 'ADDACN'
last_3_month_date = datetime.today().date() - timedelta(days=90)


def sendSMS(numbers,message1):
    message = '''{}'''.format(message1)

    params = {'apikey': api_key, 'numbers': '91'+numbers, 'message': message, 'sender': sender}
    f = urllib.request.urlopen('https://api.textlocal.in/send/?'
                               + urllib.parse.urlencode(params))
    return (f.read(), f.code)



class StaffLogin(JSONWebTokenSerializer):
    """
    {
    "username":'anish',
    "password":'sahu12345'
    }
    """
    username_field = 'username'

    def validate(self, attrs):

        credentials = {
            'username': attrs.get("username"),
            'password': attrs.get("password")
        }

        if all(credentials.values()):
            user = authenticate(**credentials)
            if user:
                query_set = Group.objects.select_related().filter(user=user.id)[0]
                if not user.is_active:
                    msg = 'User account is disabled.'
                    raise serializers.ValidationError(msg)

                payload = jwt_payload_handler(user)

                return {
                    'userType': query_set.name,
                    'token': jwt_encode_handler(payload),
                }
            else:
                return {'message': 'fail'}

        else:
            return {'message': 'fail'}


class StaffDetailView(APIView):
    '''
    {"message":"success","data":{"Name":"Sam Kumar","Address":"Mantripukhri , Bengali Colony","PhoneNumber":"7005824802","Photo":"/media/Images/Screenshot_from_2019-01-25_10-59-21.png","IdProof":"/media/Images/Screenshot_from_2019-01-25_10-59-21.png"}}
    '''

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            staff = StaffUser.objects.select_related().get(userID_id=request.user.pk)
            if staff.photo is None:
                photo = 'NaN'
            else:
                photo = staff.photo.url
            if staff.idProof is None:
                idProof = 'NaN'
            else:
                idProof = staff.idProof.url
            data = {
                'Name': staff.name,
                'Address': staff.address,
                'PhoneNumber': staff.phoneNumber,
                'Photo': photo,
                'IdProof':idProof

            }

            return Response({'message':'success','data':data})
        except:
            return Response({'message': 'fail'})

class BuyerListView(APIView):
    '''
    [
    {
                'BuyerID':obj.pk,
                'BuyerName': obj.name,
                'Address': obj.address,
                'PhoneNumber': obj.phoneNumber,
                'ClosingBalance': obj.closingBalance,

            }]
    '''

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        buyer = Buyer.objects.select_related().filter(isDeleted__exact=False).order_by('name')
        buyer_list = []
        for obj in buyer:
            buyer_dic = {
                'BuyerID':obj.pk,
                'BuyerName': obj.name,
                'Address': obj.address,
                'PhoneNumber': obj.phoneNumber,
                'ClosingBalance': obj.closingBalance,

            }

            buyer_list.append(buyer_dic)
        return Response({'buyers':buyer_list})


class CollectMoneyPostView(APIView):
    serializer_class = CollectMoneySerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CollectMoneySerializer(data=request.data)
        if serializer.is_valid():
            BuyerID = request.data.get('BuyerID')
            AmountCollected = request.data.get('AmountCollected')
            Remark = request.data.get('Remark')
            PaymentType = request.data.get('PaymentType')
            Longitude = request.data.get('Longitude')
            Latitude = request.data.get('Latitude')
            try:
                ChequeImage = request.FILES['ChequeImage']
            except:
                ChequeImage = None
            collect = MoneyCollection()
            collect.buyerID_id = int(BuyerID)
            collect.amount = float(AmountCollected)
            collect.remark = Remark
            collect.latitude = Latitude
            collect.longitude = Longitude
            collect.paymentMode = PaymentType
            if PaymentType == 'Cash':
                collect.chequeImage = None
            if PaymentType == 'Cheque':
                collect.chequeImage = ChequeImage

            user = StaffUser.objects.select_related().get(userID_id=request.user.pk)
            collect.collectedBy_id = user.pk
            collect.save()

            buyer = Buyer.objects.select_related().get(pk=int(BuyerID))
            buyer.closingBalance = buyer.closingBalance - float(AmountCollected)
            buyer.save()
            r = sendSMS(buyer.phoneNumber, AmountCollected)



            return Response({'message': 'success'})
        else:
            return Response({'message': 'fail'})


class CollectMoneyListView(APIView):
    '''
    [
    {
                'BuyerName':obj.buyerID.name,
                'AmountCollected':obj.amount,
                'Remark':obj.remark,
                'PaymentType':obj.paymentMode,
                'ChequeImage':obj.chequeImage,
                'DateTime':obj.datetime.strftime('%I:%M %p')

            }]
    '''

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        collection = MoneyCollection.objects.select_related().filter(datetime__icontains=datetime.today().date(),
                                                                     collectedBy__userID=request.user.pk).exclude(
            datetime__lt=last_3_month_date).order_by(
            '-id')
        collection_list = []
        for obj in collection:
            try:
                chequeImage = obj.chequeImage.url
            except:
                chequeImage = 'N/A'
            collection_dic = {
                'BuyerName':obj.buyerID.name,
                'AmountCollected':obj.amount,
                'Remark':obj.remark,
                'PaymentType':obj.paymentMode,
                'ChequeImage':chequeImage,
                'DateTime':obj.datetime.strftime('%I:%M %p')

            }

            collection_list.append(collection_dic)
        return Response({'data':collection_list})


class ChangePasswordPostView(APIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            NewPassword = request.data.get('NewPassword')
            OldPassword = request.data.get('OldPassword')
            data = StaffUser.objects.select_related().get(userID_id=request.user.pk)
            if data.password == OldPassword:



                data.password = NewPassword
                data.save()
                user = User.objects.select_related().get(pk=request.user.pk)
                user.set_password(NewPassword)
                user.save()

                return Response({'message': 'success'})
            else:
                return Response({'message': 'fail'})
        else:
            return Response({'message': 'fail'})


class CanTakePaymentView(APIView):
    '''
   {'data':{
            'CanTakePayment':staff.canTakePayment,
        }}
    '''

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        staff = StaffUser.objects.select_related().get(userID_id=request.user.pk)

        staff_dic = {
            'CanTakePayment':staff.canTakePayment,


        }

        return Response({'data':staff_dic})
