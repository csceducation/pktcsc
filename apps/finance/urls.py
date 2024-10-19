from django.urls import path

from .views import (
    InvoiceCreateView,
    InvoiceDeleteView,
    InvoiceDetailView,
    InvoiceListView,
    InvoiceUpdateView,
    ReceiptCreateView,
    ReceiptUpdateView,
    bulk_invoice,
    save_bill_details,
    get_student_dues,
    dues_list,
    delete_due,
    extend_due,
    update_due,
    dashboard_view
)

urlpatterns = [
    path("bill/",save_bill_details,name="bill"),
    path('due/<int:due_id>/update/', update_due, name='update_due'),
    path("list/", InvoiceListView.as_view(), name="invoice-list"),
    path("create/", InvoiceCreateView.as_view(), name="invoice-create"),
    path("<int:pk>/detail/", InvoiceDetailView.as_view(), name="invoice-detail"),
    path("<int:pk>/update/", InvoiceUpdateView.as_view(), name="invoice-update"),
    path("<int:pk>/delete/", InvoiceDeleteView.as_view(), name="invoice-delete"),
    path("receipt/create", ReceiptCreateView.as_view(), name="receipt-create"),
    path(
        "receipt/<int:pk>/update/", ReceiptUpdateView.as_view(), name="receipt-update"
    ),
    path("bulk-invoice/", bulk_invoice, name="bulk-invoice"),
    path('student-dues/<int:student_id>/', get_student_dues, name='student-dues'),
    path('dues',dues_list,name="due_dashboard"),
    path('delete_dues/<int:pk>/',delete_due,name="delete_due"),
    path('extend_dues/<int:pk>',extend_due,name="extend_due"),
    path('dashboard',dashboard_view,name = "finance_dashboard")
]
