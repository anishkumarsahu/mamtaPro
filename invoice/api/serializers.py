from rest_framework import serializers


class CreateInvoiceSerializer(serializers.Serializer):
    InvoiceSerialID = serializers.CharField(max_length=100)
    BillNumber= serializers.CharField(max_length=100)
    SalesType = serializers.CharField(max_length=200)
    Amount = serializers.CharField(max_length=200)
    CustomerName = serializers.CharField(max_length=200)

    class Meta:
        fields = ['InvoiceSerialID', 'BillNumber', 'SalesType'
                  'Amount','CustomerName']

