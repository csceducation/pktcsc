from django.urls import path

from .views import (
    DownloadCSVViewdownloadcsv,
    EnquiryCreateView,
    EnquiryDeleteView,
    EnquiryDetailView,
    EnquiryListView,
    EnquiryUpdateView,
    LogCreateView,
    delete_enquiry_log,
    StudentEnquiryDeleteView,
    StudentEnquiryUpdateView,
    StudentEnquiryListView,
    StudentEnquiryCreateView,
    enquiry_index,
    
)

urlpatterns = [
    path("index",enquiry_index,name="enquiry-index"),
    path("create/<int:enquiry_id>/", StudentEnquiryCreateView.as_view(), name="student-enquiry-create"),
    path("list",EnquiryListView.slist, name="enquiry-list"),
    path("pending/list",StudentEnquiryListView.slist, name="pending-enquiry-list"),
    path("<int:pk>/histroy",LogCreateView.as_view(),name="logview"),
    path("<int:pk>/",EnquiryDetailView.as_view(), name="enquiry-detail"),
    path("create/",EnquiryCreateView.as_view(), name="enquiry-create"),
    path("<int:pk>/update/",EnquiryUpdateView.as_view(), name="enquiry-update"),
    path("<int:pk>/pending/update/",StudentEnquiryUpdateView.as_view(), name="pending-enquiry-update"),
    path("delete/<int:pk>/",EnquiryDeleteView.as_view(), name="enquiry-delete"),
    path("pending/delete/<int:pk>/",StudentEnquiryDeleteView.as_view(), name="student-enquiry-delete"),
     path("endelete/<int:pk>/", delete_enquiry_log, name="enhis-delete"),
    path("download-csv/", DownloadCSVViewdownloadcsv.as_view(), name="download-csv"),
]
