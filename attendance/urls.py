from django.conf.urls import url
from .views import *

urlpatterns = [
    # buyer
    url(r'^LoginSystemListJson/$', LoginSystemListJson.as_view(), name='LoginSystemListJson'),
    url(r'^EmployeeListJson/$', EmployeeListJson.as_view(), name='EmployeeListJson'),
    url(r'^EmployeeListForAttendanceJson/$', EmployeeListForAttendanceJson.as_view(), name='EmployeeListForAttendanceJson'),
    url(r'^EmployeeListForAttendanceAdminJson/$', EmployeeListForAttendanceAdminJson.as_view(), name='EmployeeListForAttendanceAdminJson'),
    url(r'^EmployeeListForAttendanceAdminBasicJson/$', EmployeeListForAttendanceAdminBasicJson.as_view(), name='EmployeeListForAttendanceAdminBasicJson'),
    url(r'^OrderEmployeeListForAttendanceAdminBasicJson/$', OrderEmployeeListForAttendanceAdminBasicJson.as_view(), name='OrderEmployeeListForAttendanceAdminBasicJson'),

    url(r'^attendance/$', attendance, name='attendance'),
    url(r'^attendanceReport/$', attendanceReport, name='attendanceReport'),


    url(r'^ManageLoginSystem/$', loginSystem, name='loginSystem'),
    url(r'^add_login_system_api/$', add_login_system_api, name='add_login_system_api'),
    url(r'^edit_login_system_api/$', edit_login_system_api, name='edit_login_system_api'),


    url(r'^manageEmployee/$', manageEmployee, name='manageEmployee'),
    url(r'^addEmployee/$', addEmployee, name='addEmployee'),
    url(r'^employee/edit/(?P<id>\d+)/$', edit_employee, name='edit_employee'),

    url(r'^add_employee_api/$', add_employee_api, name='add_employee_api'),
    url(r'^edit_employee_api/$', edit_employee_api, name='edit_employee_api'),
    url(r'^edit_employee_photo_api/$', edit_employee_photo_api, name='edit_employee_photo_api'),
    url(r'^delete_employee_api/$', delete_employee_api, name='delete_employee_api'),



    url(r'^login_post_api/$', login_post_api, name='login_post_api'),
    url(r'^logout_post_api/$', logout_post_api, name='logout_post_api'),
    url(r'^genereate_attendence_report/$', genereate_attendence_report, name='genereate_attendence_report'),
    url(r'^demoReport/$', demoReport, name='demoReport'),
    url(r'^order_employee_attendance_post_api/$', order_employee_attendance_post_api, name='order_employee_attendance_post_api'),
    url(r'^generate_attendance_for_order_emp_report/$', generate_attendance_for_order_emp_report, name='generate_attendance_for_order_emp_report'),

]
