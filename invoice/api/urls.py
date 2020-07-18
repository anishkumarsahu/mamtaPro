from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^InvoiceSeries/$', InvoiceSeriesView.as_view(), name='InvoiceSeriesView'),
    url(r'^InvoiceSerials/$', InvoiceSerialsView.as_view(), name='InvoiceSerialsView'),
    url(r'^CreateSales/$', CreateSalesPostView.as_view(), name='CreateSalesPostView'),


]