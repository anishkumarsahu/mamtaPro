from django.conf.urls import url
from rest_framework_jwt.views import ObtainJSONWebToken
from .views import *

urlpatterns = [

    url(r'^StaffLogin/$', ObtainJSONWebToken.as_view(serializer_class=StaffLogin)),
    url(r'^GetStaffDetail/$', StaffDetailView.as_view(), name='StaffDetailView'),

    url(r'^BuyerList/$', BuyerListView.as_view(), name='BuyerListView'),
    url(r'^CollectMoneyPost/$', CollectMoneyPostView.as_view(), name='CollectMoneyPostView'),
    url(r'^CollectMoneyList/$', CollectMoneyListView.as_view(), name='CollectMoneyListView'),
    url(r'^ChangePasswordForStaff/$', ChangePasswordPostView.as_view(), name='ChangePasswordPostView'),
    url(r'^CanTakePayment/$', CanTakePaymentView.as_view(), name='CanTakePaymentView'),

]