from mamtaApp.models import StaffUser
from .models import Employee

def generate_emp_from_staff():
    for staff in StaffUser.objects.filter(isDeleted=False, staffTypeID__name='Order Team'):
        try:
            Employee.objects.get(staffIdIfAutogenerated__exact=staff.pk, isDeleted=False,autogenerated=True)
        except:
            try:
                Employee.objects.create(staffIdIfAutogenerated=staff.pk, autogenerated=True,name=staff.name,password=staff.password,
                                    photo=staff.photo.url, address=staff.address, phoneNumber=staff.phoneNumber,inTime="09:00",
                                        outTime="18:00")
            except:
                print("error")
                pass
