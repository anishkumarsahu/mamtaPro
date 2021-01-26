from django.db import models

# Create your models here.

from mamtaApp.models import *


class InvoiceSeries(models.Model):
    series = models.CharField(max_length=100, blank=True, null=True)
    assignedTo = models.ForeignKey(StaffUser, blank=True, null=True)
    startsWith = models.CharField(default='00001', max_length=100)
    isDeleted = models.BooleanField(default=False)
    datetime = models.DateTimeField(auto_now_add=True, auto_now=False)
    companyID = models.ForeignKey(Company, blank=True, null=True)
    lastUpdatedOn = models.DateTimeField(auto_now_add=False, auto_now=True)
    isCompleted = models.BooleanField(default=False)

    def __str__(self):
        return str(self.series)


class InvoiceSerial(models.Model):
    number = models.CharField(default='00001', max_length=100)
    numberMain = models.IntegerField(default=1)
    isDeleted = models.BooleanField(default=False)
    datetime = models.DateTimeField(auto_now_add=True, auto_now=False)
    lastUpdatedOn = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return str(self.number)


class Sales(models.Model):
    InvoiceSeriesID = models.ForeignKey(InvoiceSeries, blank=True, null=True)
    billNumber = models.CharField(max_length=100, blank=True, null=True)
    actualBillNumber = models.CharField(max_length=100, blank=True, null=True)
    numberMain = models.IntegerField(default=1)
    salesType = models.CharField(max_length=100, blank=True, null=True)
    createdBy = models.ForeignKey(StaffUser, blank=True, null=True)
    amount = models.FloatField(default=0.0)
    mixCardAmount = models.FloatField(default=0.0)
    isCash = models.BooleanField(default=True)
    customerName = models.CharField(max_length=200, blank=True, null=True)
    challanNumber = models.CharField(max_length=200,default='N/A')
    isDeleted = models.BooleanField(default=False)
    datetime = models.DateTimeField(auto_now_add=True, auto_now=False)
    lastUpdatedOn = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return str(self.billNumber)


class CollectionOnSale(models.Model):
    companyID = models.ForeignKey(Company, blank=True, null=True)
    createdBy = models.ForeignKey(StaffUser, blank=True, null=True)
    amount = models.FloatField(default=0.0)
    customerName = models.CharField(max_length=200, blank=True, null=True)
    isDeleted = models.BooleanField(default=False)
    datetime = models.DateTimeField(auto_now_add=True, auto_now=False)
    lastUpdatedOn = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return str(self.customerName)


class ReturnCollection(models.Model):
    actualBillNumber = models.CharField(max_length=100, blank=True, null=True)
    numberMain = models.IntegerField(default=1)
    createdBy = models.ForeignKey(StaffUser, blank=True, null=True)
    amount = models.FloatField(default=0.0)
    companyID = models.ForeignKey(Company, blank=True, null=True)
    isDeleted = models.BooleanField(default=False)
    datetime = models.DateTimeField(auto_now_add=True, auto_now=False)
    lastUpdatedOn = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return str(self.actualBillNumber)


class Commission(models.Model):
    actualBillNumber = models.CharField(max_length=100, blank=True, null=True)
    numberMain = models.IntegerField(default=1)
    createdBy = models.ForeignKey(StaffUser, blank=True, null=True)
    amount = models.FloatField(default=0.0)
    companyID = models.ForeignKey(Company, blank=True, null=True)
    isDeleted = models.BooleanField(default=False)
    datetime = models.DateTimeField(auto_now_add=True, auto_now=False)
    lastUpdatedOn = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return str(self.actualBillNumber)



class CorrectCollection(models.Model):
    actualBillNumber = models.CharField(max_length=100, blank=True, null=True)
    numberMain = models.IntegerField(default=1)
    createdBy = models.ForeignKey(StaffUser, blank=True, null=True)
    amount = models.FloatField(default=0.0)
    companyID = models.ForeignKey(Company, blank=True, null=True)
    isDeleted = models.BooleanField(default=False)
    datetime = models.DateTimeField(auto_now_add=True, auto_now=False)
    lastUpdatedOn = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return str(self.actualBillNumber)