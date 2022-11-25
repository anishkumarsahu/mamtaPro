from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Company(models.Model):
    name = models.CharField(blank=True, null=True, max_length=250)
    phoneNumber = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    isDeleted = models.BooleanField(default=False)
    datetime = models.DateTimeField(auto_now_add=True, auto_now=False)
    lastUpdatedOn = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return self.name


class StaffType(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    isDeleted = models.BooleanField(default=False)
    datetime = models.DateTimeField(auto_now_add=True, auto_now=False)
    lastUpdatedOn = models.DateTimeField(auto_now_add=False, auto_now=True)


class Admin(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    username = models.CharField(max_length=100, blank=True, null=True)
    password = models.CharField(max_length=100, blank=True, null=True)
    userID = models.ForeignKey(User, blank=True, null=True)
    isDeleted = models.BooleanField(default=False)
    datetime = models.DateTimeField(auto_now_add=True, auto_now=False)
    lastUpdatedOn = models.DateTimeField(auto_now_add=False, auto_now=True)


class StaffUser(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    phoneNumber = models.CharField(max_length=100, blank=True, null=True)
    photo = models.ImageField(upload_to='Images', blank=True, null=True)
    idProof = models.ImageField(upload_to='IdProof', blank=True, null=True)
    isActive = models.BooleanField(default=True)
    username = models.CharField(max_length=100, blank=True, null=True)
    password = models.CharField(max_length=100, blank=True, null=True)
    userID = models.ForeignKey(User, blank=True, null=True)
    staffTypeID = models.ForeignKey(StaffType, blank=True, null=True)
    isDeleted = models.BooleanField(default=False)
    canTakePayment = models.BooleanField(default=True)
    datetime = models.DateTimeField(auto_now_add=True, auto_now=False)
    lastUpdatedOn = models.DateTimeField(auto_now_add=False, auto_now=True)
    companyID = models.ForeignKey(Company, blank=True, null=True)

    def __str__(self):
        return self.name


class Buyer(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    phoneNumber = models.CharField(max_length=100, blank=True, null=True)
    closingBalance = models.FloatField(default=0.0)
    isDeleted = models.BooleanField(default=False)
    datetime = models.DateTimeField(auto_now_add=True, auto_now=False)
    lastUpdatedOn = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return self.name


class MoneyToCollect(models.Model):
    buyerID = models.ForeignKey(Buyer, blank=True, null=True)
    amount = models.FloatField(default=0.0)
    remark = models.CharField(max_length=200, blank=True, null=True)
    isDeleted = models.BooleanField(default=False)
    datetime = models.DateTimeField(auto_now_add=True, auto_now=False)
    lastUpdatedOn = models.DateTimeField(auto_now_add=False, auto_now=True)


class MoneyCollection(models.Model):
    buyerID = models.ForeignKey(Buyer, blank=True, null=True)
    collectedBy = models.ForeignKey(StaffUser, blank=True, null=True)
    amount = models.FloatField(default=0.0)
    remark = models.CharField(max_length=500, blank=True, null=True)
    message = models.CharField(max_length=500, blank=True, null=True)
    paymentMode = models.CharField(max_length=100, default='Cash')
    chequeImage = models.ImageField(upload_to='Cheques', blank=True, null=True)
    latitude = models.CharField(max_length=200, default='0.0')
    longitude = models.CharField(max_length=200, default='0.0')
    isDeleted = models.BooleanField(default=False)
    isAddedInSales = models.BooleanField(default=False)
    companyID = models.ForeignKey(Company, blank=True, null=True)
    datetime = models.DateTimeField(auto_now_add=True, auto_now=False)
    lastUpdatedOn = models.DateTimeField(auto_now_add=False, auto_now=True)


class CashMoneyCollection(models.Model):
    buyerID = models.ForeignKey(Buyer, blank=True, null=True)
    collectedBy = models.ForeignKey(StaffUser, blank=True, null=True)
    amount = models.FloatField(default=0.0)
    remark = models.CharField(max_length=500, blank=True, null=True)
    message = models.CharField(max_length=500, blank=True, null=True)
    paymentMode = models.CharField(max_length=100, default='Cash')
    chequeImage = models.ImageField(upload_to='Cheques', blank=True, null=True)
    latitude = models.CharField(max_length=200, default='0.0')
    longitude = models.CharField(max_length=200, default='0.0')
    isDeleted = models.BooleanField(default=False)
    isAddedInSales = models.BooleanField(default=False)
    companyID = models.ForeignKey(Company, blank=True, null=True)
    datetime = models.DateTimeField(auto_now_add=True, auto_now=False)
    lastUpdatedOn = models.DateTimeField(auto_now_add=False, auto_now=True)


class SupplierCollection(models.Model):
    buyerID = models.ForeignKey(Buyer, blank=True, null=True)
    collectedBy = models.ForeignKey(StaffUser, blank=True, null=True)
    amount = models.FloatField(default=0.0)
    remark = models.CharField(max_length=500, blank=True, null=True)
    message = models.CharField(max_length=500, blank=True, null=True)
    paymentMode = models.CharField(max_length=100, default='Cash')
    isDeleted = models.BooleanField(default=False)
    companyID = models.ForeignKey(Company, blank=True, null=True)
    datetime = models.DateTimeField(auto_now_add=True, auto_now=False)
    lastUpdatedOn = models.DateTimeField(auto_now_add=False, auto_now=True)
    isApproved = models.BooleanField(default=False)
    approvedBy = models.CharField(max_length=100, blank=True, null=True, default='N/A')
    Location = models.CharField(max_length=200, blank=True, null=True, default='N/A')
    lat = models.CharField(max_length=200, blank=True, null=True, default='0.0')
    lng = models.CharField(max_length=200, blank=True, null=True, default='0.0')

class LoginAndLogoutStatus(models.Model):
    userID = models.ForeignKey(User, blank=True, null=True)
    statusType = models.CharField(max_length=100, blank=True, null=True)
    isDeleted = models.BooleanField(default=False)
    companyID = models.ForeignKey(Company, blank=True, null=True)
    datetime = models.DateTimeField(auto_now_add=True, auto_now=False)
    lastUpdatedOn = models.DateTimeField(auto_now_add=False, auto_now=True)


class SupplierInvoiceCollection(models.Model):
    buyerID = models.ForeignKey(Buyer, blank=True, null=True)
    collectedBy = models.ForeignKey(StaffUser, blank=True, null=True)
    amount = models.FloatField(default=0.0)
    remark = models.CharField(max_length=500, blank=True, null=True)
    message = models.CharField(max_length=500, blank=True, null=True)
    invoiceNumber = models.CharField(max_length=100, blank=True, null=True)
    isDeleted = models.BooleanField(default=False)
    companyID = models.ForeignKey(Company, blank=True, null=True)
    datetime = models.DateTimeField(auto_now_add=True, auto_now=False)
    lastUpdatedOn = models.DateTimeField(auto_now_add=False, auto_now=True)
    isApproved = models.BooleanField(default=False)
    approvedBy = models.CharField(max_length=100, blank=True, null=True, default='N/A')
    Location = models.CharField(max_length=200, blank=True, null=True, default='N/A')
    lat = models.CharField(max_length=200, blank=True, null=True, default='0.0')
    lng = models.CharField(max_length=200, blank=True, null=True, default='0.0')


class StaffAdvanceToBuyer(models.Model):
    buyerID = models.ForeignKey(Buyer, blank=True, null=True)
    collectedBy = models.ForeignKey(StaffUser, blank=True, null=True)
    amount = models.FloatField(default=0.0)
    remark = models.CharField(max_length=500, blank=True, null=True)
    isDeleted = models.BooleanField(default=False)
    companyID = models.ForeignKey(Company, blank=True, null=True)
    datetime = models.DateTimeField(auto_now_add=True, auto_now=False)
    lastUpdatedOn = models.DateTimeField(auto_now_add=False, auto_now=True)



class TakeOrder(models.Model):
    orderTakenFrom = models.CharField(max_length=200, blank=True, null=True)
    orderPic = models.ImageField(upload_to='OrderPics', blank=True, null=True)
    details = models.TextField(blank=True, null=True)
    latitude = models.CharField(max_length=200, default='0.0')
    longitude = models.CharField(max_length=200, default='0.0')
    location = models.TextField(blank=True, null=True)
    orderTakenBy = models.ForeignKey(StaffUser, blank=True, null=True)
    isDeleted = models.BooleanField(default=False)
    companyID = models.ForeignKey(Company, blank=True, null=True)
    datetime = models.DateTimeField(auto_now_add=True, auto_now=False)
    lastUpdatedOn = models.DateTimeField(auto_now_add=False, auto_now=True)