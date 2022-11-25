
from django.conf.urls import url
from .views import *



urlpatterns = [
    # buyer
    url(r'^InvoicePrintListJson/$', InvoicePrintListJson.as_view(), name='InvoicePrintListJson'),
    url(r'^LoginListJson/$', LoginListJson.as_view(), name='LoginListJson'),
    url(r'^LogoutListJson/$', LogoutListJson.as_view(), name='LogoutListJson'),
    url(r'^buyerList/$', BuyerListJson.as_view(), name='BuyerListJson'),
    url(r'^ManageCreditListJson/$', ManageCreditListJson.as_view(), name='ManageCreditListJson'),
    url(r'^CreditListJson/$', CreditListJson.as_view(), name='CreditListJson'),
    url(r'^DebitListJson/$', DebitListJson.as_view(), name='DebitListJson'),
    url(r'^CollectionListCashJson/$', CollectionListCashJson.as_view(), name='CollectionListCashJson'),
    url(r'^CollectionListChequeJson/$', CollectionListChequeJson.as_view(), name='CollectionListChequeJson'),
    url(r'^ManageCompanyListJson/$', ManageCompanyListJson.as_view(), name='ManageCompanyListJson'),
    url(r'^StaffListJson/$', StaffListJson.as_view(), name='StaffListJson'),
    url(r'^SupplierCollectionListJson/$', SupplierCollectionListJson.as_view(), name='SupplierCollectionListJson'),
    url(r'^SupplierInvoiceCollectionListJson/$', SupplierInvoiceCollectionListJson.as_view(), name='SupplierInvoiceCollectionListJson'),
    url(r'^SupplierCollectionListCashJson/$', SupplierCollectionListCashJson.as_view(), name='SupplierCollectionListCashJson'),
    url(r'^SupplierCollectionAdminListCashJson/$', SupplierCollectionAdminListCashJson.as_view(), name='SupplierCollectionAdminListCashJson'),
    url(r'^SupplierCollectionListChequeJson/$', SupplierCollectionListChequeJson.as_view(), name='SupplierCollectionListChequeJson'),
    url(r'^SupplierCollectionAdminListChequeJson/$', SupplierCollectionAdminListChequeJson.as_view(), name='SupplierCollectionAdminListChequeJson'),
    url(r'^SupplierCollectionInvoiceList/$', SupplierCollectionInvoiceList.as_view(),
        name='SupplierCollectionInvoiceList'),

    url(r'^SupplierCollectionInvoiceListAdmin/$', SupplierCollectionInvoiceListAdmin.as_view(),
        name='SupplierCollectionInvoiceListAdmin'),

    url(r'^$', home, name='home'),
    # staff
    url(r'^staff/$', staff, name='staff'),
    url(r'^staff/add/$', add_staff, name='add_staff'),
    url(r'^staff/detail/(?P<id>\d+)/$', detail_staff, name='detail_staff'),
    url(r'^staff/edit/(?P<id>\d+)/$', edit_staff, name='edit_staff'),

    # staff api
    url(r'^staff/add/api/$', add_staff_user_api, name='add_staff_user_api'),
    url(r'^staff/edit/api/$', edit_staff_user_api, name='edit_staff_user_api'),
    url(r'^staff/photo_edit/api/$', edit_staff_photo_api, name='edit_staff_photo_api'),
    url(r'^staff/idproof_edit/api/$', edit_staff_idproof_api, name='edit_staff_idproof_api'),
    url(r'^staff/delete/api/$', delete_staff_user_api, name='delete_staff_user_api'),

    # buyers
    url(r'^buyers/$', buyers, name='buyers'),
    url(r'^buyers/add/$', add_buyer, name='add_buyer'),
    url(r'^buyers/detail/(?P<id>\d+)/$', detail_buyer, name='detail_buyer'),
    url(r'^buyers/edit/(?P<id>\d+)/$', edit_buyer, name='edit_buyer'),

    # buyers api
    url(r'^buyers/add/api/$', add_buyer_api, name='add_buyer_api'),
    url(r'^buyers/edit/api/$', edit_buyer_api, name='edit_buyer_api'),
    url(r'^buyers/delete/api/$', delete_buyer_api, name='delete_buyer_api'),

    # credits
    url(r'^buyers/credit/add/api/$', add_money_to_be_collected_api, name='add_money_to_be_collected_api'),

    # report
    url(r'^report/$', report, name='report'),
    # report
    url(r'^manage_credits/$', manage_credits, name='manage_credits'),

    # login
    url(r'^login/$', loginApp, name='loginApp'),

    # logout
    url(r'^Logout/$', logout_user, name='logout'),

    # profile
    url(r'^profile/$', profile, name='profile'),
    url(r'^change_password/$', change_password_api, name='change_password_api'),


    url(r'^manage_company/$', manage_company, name='manage_company'),
    url(r'^add_company_api/$', add_company_api, name='add_company_api'),
    url(r'^edit_company_api/$', edit_company_api, name='edit_company_api'),


    #supply
    url(r'^supplyHome/$', supply_home, name='supply_home'),
    url(r'^supplier_collection_report/$', supplier_collection_report, name='supplier_collection_report'),
    url(r'^take_collection_supplier_api/$', take_collection_supplier_api, name='take_collection_supplier_api'),
    url(r'^take_collection_invoice_supplier_api/$', take_collection_invoice_supplier_api, name='take_collection_invoice_supplier_api'),
    url(r'^edit_collection_supplier_api/$', edit_collection_supplier_api, name='edit_collection_supplier_api'),
    url(r'^approve_collection_supplier_api/$', approve_collection_supplier_api, name='approve_collection_supplier_api'),
    url(r'^approve_collection_supplier_invoice_api/$', approve_collection_supplier_invoice_api, name='approve_collection_supplier_invoice_api'),
    url(r'^delete_collection_supplier_api/$', delete_collection_supplier_api, name='delete_collection_supplier_api'),
    url(r'^delete_collection_supplier_invoice_api/$', delete_collection_supplier_invoice_api, name='delete_collection_supplier_invoice_api'),

    # username exist?
    url(r'^user_name_exist/$', user_name_exist, name='user_name_exist'),

    # login logout report
    url(r'^login_and_logout_report/$', login_and_logout_report, name='login_and_logout_report'),

    #cashier
    url(r'^cashierHome/$', cashier_home, name='cashier_home'),

    #print Report
    url(r'^print_report/$', print_report, name='print_report'),

    # Order Team
    url(r'^order_home/$', order_home, name='order_home'),
    url(r'^api/take_order_api/$', take_order_api, name='take_order_api'),
    url(r'^api/OrderListByUserPerDayJson/$', OrderListByUserPerDayJson.as_view(), name='OrderListByUserPerDayJson'),

]
