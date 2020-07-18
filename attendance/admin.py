from django.contrib import admin

# Register your models here.

from .models import *

class LoginSystemAdmin(admin.ModelAdmin):
    list_display = ['systemName', 'location', 'username', 'password']


admin.site.register(LoginSystem, LoginSystemAdmin)


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'phoneNumber', 'password', 'password', 'inTime', 'outTime', 'isActive']


admin.site.register(Employee, EmployeeAdmin)


class EmployeeAttendanceAdmin(admin.ModelAdmin):
    list_display = ['employeeID', 'attendanceDate', 'loginTime', 'loginRemark', 'logoutTime', 'logoutRemark']


admin.site.register(EmployeeAttendance, EmployeeAttendanceAdmin)