from django.conf.urls import url
from .views import *

urlpatterns = [
    # buyer

    url(r'^InvoiceSeriesListJson/$', InvoiceSeriesListJson.as_view(), name='InvoiceSeriesListJson'),
    url(r'^InvoiceCreatedByCashListJson/$', InvoiceCreatedByCashListJson.as_view(),
        name='InvoiceCreatedByCashListJson'),
    url(r'^InvoiceCreatedByCardListJson/$', InvoiceCreatedByCardListJson.as_view(),
        name='InvoiceCreatedByCardListJson'),
    url(r'^InvoiceCreatedByMixListJson/$', InvoiceCreatedByMixListJson.as_view(), name='InvoiceCreatedByMixListJson'),
    url(r'^InvoiceCreatedByCreditListJson/$', InvoiceCreatedByCreditListJson.as_view(),
        name='InvoiceCreatedByCreditListJson'),
    url(r'^CollectionListJson/$', CollectionListJson.as_view(), name='CollectionListJson'),
    url(r'^CashCollectionListJson/$', CashCollectionListJson.as_view(), name='CashCollectionListJson'),
    url(r'^StaffAdvanceListJson/$', StaffAdvanceListJson.as_view(), name='StaffAdvanceListJson'),
    url(r'^ReturnCollectionListJson/$', ReturnCollectionListJson.as_view(), name='ReturnCollectionListJson'),
    url(r'^CorrectCollectionListJson/$', CorrectCollectionListJson.as_view(), name='CorrectCollectionListJson'),
    url(r'^CommissionListJson/$', CommissionListJson.as_view(), name='CommissionListJson'),
    url(r'^ExpenseListJson/$', ExpenseListJson.as_view(), name='ExpenseListJson'),

    url(r'^$', index, name='index'),
    url(r'^get_invoice_series/$', get_invoice_series, name='get_invoice_series'),
    url(r'^create_invoice/$', create_invoice, name='create_invoice'),
    url(r'^edit_invoice/$', edit_invoice, name='edit_invoice'),
    url(r'^edit_invoice_mix/$', edit_invoice_mix, name='edit_invoice_mix'),
    url(r'^edit_collection/$', edit_collection, name='edit_collection'),
    url(r'^edit_collection_cash/$', edit_collection_cash, name='edit_collection_cash'),
    url(r'^delete_sale_api/$', delete_sale_api, name='delete_sale_api'),
    url(r'^delete_sale_api_mix/$', delete_sale_api_mix, name='delete_sale_api_mix'),
    url(r'^delete_collection_api/$', delete_collection_api, name='delete_collection_api'),
    url(r'^delete_cash_collection_api/$', delete_cash_collection_api, name='delete_cash_collection_api'),
    url(r'^generateInvoice/$', generate_serial_invoice_number, name='generate_serial_invoice_number'),

    url(r'^manage_invoice/$', invoice_list, name='manage_invoice'),
    url(r'^add_invoice_serial/$', add_invoice_serial, name='add_invoice_serial'),
    url(r'^edit_invoice_serial/$', edit_invoice_serial, name='edit_invoice_serial'),

    url(r'^invoice_report/$', invoice_report, name='invoice_report'),
    url(r'^generate_net_report/$', generate_net_report, name='generate_net_report'),
    url(r'^generate_net_report_admin/$', generate_net_report_admin, name='generate_net_report_admin'),
    url(r'^generate_net_report_accountant/$', generate_net_report_accountant, name='generate_net_report_accountant'),
    url(r'^generate_monthly_report_admin/$', generate_monthly_report_admin, name='generate_monthly_report_admin'),
    url(r'^generate_monthly_report_staff_advance_admin/$', generate_monthly_report_staff_advance_admin, name='generate_monthly_report_staff_advance_admin'),

    url(r'^search_invoice/$', search_invoice, name='search_invoice'),
    url(r'^skipped_invoice/$', skipped_invoice, name='skipped_invoice'),
    url(r'^take_collection/$', take_collection, name='take_collection'),
    url(r'^take_cash_collection/$', take_cash_collection, name='take_cash_collection'),

    url(r'^get_today_collection_by_company/$', get_today_collection_by_company, name='get_today_collection_by_company'),
    url(r'^get_today_cash_collection_by_company/$', get_today_cash_collection_by_company,
        name='get_today_cash_collection_by_company'),
    url(r'^add_party_from_sales/$', add_party_from_sales, name='add_party_from_sales'),
    url(r'^get_buyer_list/$', get_buyer_list, name='get_buyer_list'),

    url(r'^change_password_for_sales_user/$', change_password_for_sales_user, name='change_password_for_sales_user'),
    url(r'^get_last_three_invoices/$', get_last_three_invoices, name='get_last_three_invoices'),
    url(r'^generate_collection_report_admin/$', generate_collection_report_admin,
        name='generate_collection_report_admin'),
    url(r'^generate_collection_report_supplier/$', generate_collection_report_supplier,
        name='generate_collection_report_supplier'),
    url(r'^generate_collection_report/$', generate_collection_report, name='generate_collection_report'),

    # Accountant
    url(r'^collection_report_accountant/$', collection_report_accountant, name='collection_report_accountant'),

    # Return
    url(r'^return_collection_post/$', return_collection, name='return_collection'),
    url(r'^get_today_return_by_company/$', get_today_return_by_company, name='get_today_return_by_company'),
    url(r'^edit_return/$', edit_return, name='edit_return'),
    url(r'^delete_return_api/$', delete_return_api, name='delete_return_api'),

    # Commission
    url(r'^commission_collection_post/$', commission_collection, name='commission_collection'),
    url(r'^get_today_commission_by_company/$', get_today_commission_by_company, name='get_today_commission_by_company'),
    url(r'^edit_commission/$', edit_commission, name='edit_commission'),
    url(r'^delete_commission_api/$', delete_commission_api, name='delete_commission_api'),

    # Correction
    url(r'^correction_collection_post/$', correct_collection, name='correct_collection'),
    url(r'^get_today_correction_by_company/$', get_today_correction_by_company, name='get_today_correction_by_company'),
    url(r'^edit_correction/$', edit_correction, name='edit_correction'),
    url(r'^delete_correction_api/$', delete_correction_api, name='delete_correction_api'),

    # expense
    url(r'^add_expense/$', add_expense, name='add_expense'),
    url(r'^get_today_expense_by_company/$', get_today_expense_by_company, name='get_today_expense_by_company'),
    url(r'^edit_expense/$', edit_expense, name='edit_expense'),
    url(r'^delete_expense_api/$', delete_expense_api, name='delete_expense_api'),

    url(r'^add_closing_balance_api/$', add_closing_balance_api, name='add_closing_balance_api'),

    # staffAdvance
    url(r'^staff_advance_post/$', staff_advance_post, name='staff_advance_post'),
    url(r'^get_today_staff_advance_by_company/$', get_today_staff_advance_by_company,
        name='get_today_staff_advance_by_company'),
    url(r'^edit_staff_advance/$', edit_staff_advance, name='edit_staff_advance'),
    url(r'^delete_staff_advance_api/$', delete_staff_advance_api, name='delete_staff_advance_api'),

]
