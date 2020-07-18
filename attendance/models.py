from django.db import models
from django.contrib.auth.models import User
from stdimage import StdImageField


# Create your models here.

class LoginSystem(models.Model):
    systemName = models.CharField(max_length=200, blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    username = models.CharField(max_length=100, blank=True, null=True)
    password = models.CharField(max_length=100, blank=True, null=True)
    userID = models.ForeignKey(User, blank=True, null=True)
    isDeleted = models.BooleanField(default=False)
    datetime = models.DateTimeField(auto_now_add=True, auto_now=False)
    lastUpdatedOn = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return self.systemName


class Employee(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    phoneNumber = models.CharField(max_length=100, blank=True, null=True)
    photo = StdImageField(upload_to='Employee', blank=True, null=True,
                          variations={'thumbnail': {'width': 70, 'height': 70}})
    inTime = models.TimeField(null=True)
    outTime = models.TimeField(null=True)
    isActive = models.BooleanField(default=True)
    password = models.CharField(max_length=100, blank=True, null=True)
    isDeleted = models.BooleanField(default=False)
    datetime = models.DateTimeField(auto_now_add=True, auto_now=False)
    lastUpdatedOn = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return self.name


class EmployeeAttendance(models.Model):
    employeeID = models.ForeignKey(Employee, blank=True, null=True)
    attendanceDate = models.DateField(null=True)
    loginTime = models.TimeField(null=True)
    loginRemark = models.CharField(max_length=500, blank=True, null=True)
    loginPhoto = StdImageField(upload_to='EmployeeAttendanceLogin', blank=True, null=True,
                               variations={'thumbnail': {'width': 70, 'height': 70}})

    logoutTime = models.TimeField(null=True)
    logoutRemark = models.CharField(max_length=500, blank=True, null=True)
    logoutPhoto = StdImageField(upload_to='EmployeeAttendanceLogout', blank=True, null=True,
                                variations={'thumbnail': {'width': 70, 'height': 70}})

    isDeleted = models.BooleanField(default=False)
    datetime = models.DateTimeField(auto_now_add=True, auto_now=False)
    lastUpdatedOn = models.DateTimeField(auto_now_add=False, auto_now=True)

    loginSystemID = models.ForeignKey(User, blank=True, null=True, related_name='login')
    logoutSystemID = models.ForeignKey(User, blank=True, null=True, related_name='logout')

    def __str__(self):
        return self.employeeID.name
