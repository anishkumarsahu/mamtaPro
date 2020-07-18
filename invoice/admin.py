from django.contrib import admin

# Register your models here.
from .models import *


class InvoiceSeriesAdmin(admin.ModelAdmin):
    list_display = ['series', 'companyID', 'startsWith', 'isDeleted', 'datetime', ]


admin.site.register(InvoiceSeries, InvoiceSeriesAdmin)


class InvoiceSerialAdmin(admin.ModelAdmin):
    list_display = ['number', 'numberMain', 'datetime', ]


admin.site.register(InvoiceSerial, InvoiceSerialAdmin)


class SalesAdmin(admin.ModelAdmin):
    search_fields = ['billNumber', 'actualBillNumber', 'salesType', 'amount', 'customerName', 'datetime', ]

    list_display = ['InvoiceSeriesID', 'billNumber', 'actualBillNumber', 'salesType', 'createdBy', 'amount',
                    'customerName', 'datetime', ]


admin.site.register(Sales, SalesAdmin)


class CollectionAdmin(admin.ModelAdmin):
    search_fields = ['amount', 'customerName', 'datetime', ]
    list_display = ['createdBy', 'amount','companyID', 'customerName', 'datetime', ]


admin.site.register(CollectionOnSale, CollectionAdmin)


class ReturnCollectionAdmin(admin.ModelAdmin):
    search_fields = ['actualBillNumber', 'numberMain', 'amount', 'datetime', ]
    list_display = ['actualBillNumber', 'numberMain','amount','companyID','createdBy','isDeleted', 'datetime', ]


admin.site.register(ReturnCollection, ReturnCollectionAdmin)



class CommissionAdmin(admin.ModelAdmin):
    search_fields = ['actualBillNumber', 'numberMain', 'amount', 'datetime', ]
    list_display = ['actualBillNumber', 'numberMain','amount','companyID','createdBy','isDeleted', 'datetime', ]


admin.site.register(Commission, CommissionAdmin)


