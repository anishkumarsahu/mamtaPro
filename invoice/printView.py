from datetime import datetime

from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from invoice.models import *
# from loijingApp.views import check_group


# @check_group('EMP')
def generate_net_report(request):
    # startDate = request.GET.get('StartDate')
    # endDate = request.GET.get('EndDate')
    # date1 = datetime.strptime(startDate, '%d/%m/%Y')
    # date2 = datetime.strptime(endDate, '%d/%m/%Y')
    expense = Sales.objects.all().order_by('expenseDate')



    context = {
        'startDate':'just',




    }

    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = "report.pdf"
    html = render_to_string("invoice/invoicePDF.html",context)

    HTML(string=html).write_pdf(response)
    return response

#
#
# @check_group('EMP')
# def generate_installments_report(request):
#     startDate = request.GET.get('StartDate')
#     endDate = request.GET.get('EndDate')
#     date1 = datetime.strptime(startDate, '%d/%m/%Y')
#     date2 = datetime.strptime(endDate, '%d/%m/%Y')
#
#     install = LoanInstallment.objects.filter(installmentDate__gte=date1, installmentDate__lte=date2, isCollected__exact=True).order_by('installmentDate')
#
#     totalInstall = 0.0
#     totalFine = 0.0
#
#     for i in install:
#         totalInstall = totalInstall + float(i.amountCollected)
#         totalFine = totalFine + float(i.fineCollected)
#
#     context = {
#         'startDate':startDate,
#         'endDate':endDate,
#
#         'install':install,
#         'totalInstall':totalInstall,
#         'totalFine':totalFine,
#         'total':totalInstall+totalFine,
#
#
#     }
#
#     response = HttpResponse(content_type="application/pdf")
#     response['Content-Disposition'] = "installments.pdf"
#     html = render_to_string("loijingApp/installmentsReport.html",context)
#
#     HTML(string=html).write_pdf(response)
#     return response
#
#
#
#
# @check_group('EMP')
# def generate_expenses_report(request):
#     startDate = request.GET.get('StartDate')
#     endDate = request.GET.get('EndDate')
#     date1 = datetime.strptime(startDate, '%d/%m/%Y')
#     date2 = datetime.strptime(endDate, '%d/%m/%Y')
#     expense = Expense.objects.filter(expenseDate__gte=date1,expenseDate__lte=date2).order_by('expenseDate')
#
#     totalExpense = 0.0
#     for e in expense:
#         totalExpense = totalExpense + e.amount
#
#
#     context = {
#         'startDate':startDate,
#         'endDate':endDate,
#         'expense':expense,
#         'totalExpense':totalExpense,
#     }
#
#     response = HttpResponse(content_type="application/pdf")
#     response['Content-Disposition'] = "expenses.pdf"
#     html = render_to_string("loijingApp/expensesReport.html",context)
#
#     HTML(string=html).write_pdf(response)
#     return response

