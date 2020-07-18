from rest_framework import serializers


class CollectMoneySerializer(serializers.Serializer):
    BuyerID = serializers.CharField(max_length=100)
    AmountCollected= serializers.CharField(max_length=100)
    Remark = serializers.CharField(max_length=200)
    PaymentType = serializers.CharField(max_length=200)
    Latitude = serializers.CharField(max_length=200)
    Longitude = serializers.CharField(max_length=200)
    ChequeImage = serializers.ImageField(allow_null=True, use_url=True)

    class Meta:
        fields = ['BuyerID', 'AmountCollected', 'Remark','PaymentType','Latitude','Longitude','ChequeImage' ]



class ChangePasswordSerializer(serializers.Serializer):
    NewPassword = serializers.CharField(max_length=100)
    OldPassword = serializers.CharField(max_length=100)

    class Meta:
        fields = ['NewPassword','OldPassword' ]