from django.urls import path

from .views import (
    DownloadCSVViewdownloadcsv,
    StudentBulkUploadView,
    StudentCreateView,
    Studentdashboard,
    StudentDeleteView,
    StudentDetailView,
    StudentListView,
    StudentUpdateView,
    select_enquiry,
    CreateBooklLog,
    delete_book_log,
    delete_class_log,
    CreateClasslLog,
    CreateExamLog,
    delete_exam_log,
    delete_certificate_log,
    CreateCertificateLog,
    PublicView,
    generate_student_id_card,
    
)

urlpatterns = [
    path('generate_student_id_card/<int:student_id>/', generate_student_id_card, name='generate_student_id_card'),
    path("",Studentdashboard,name="dashboard"),
    path('select_enquiry/', select_enquiry, name='select_enquiry'),
    path("list", StudentListView.slist, name="student-list"),
    path("<int:pk>/", StudentDetailView.as_view(), name="student-detail"),
    path("create/<int:enquiry_id>/", StudentCreateView.as_view(), name="student-create"),
    path("<int:pk>/update/", StudentUpdateView.as_view(), name="student-update"),
    path("delete/<int:pk>/", StudentDeleteView.as_view(), name="student-delete"),
    path("upload/", StudentBulkUploadView.as_view(), name="student-upload"),
    path("download-csv/", DownloadCSVViewdownloadcsv.as_view(), name="download-csv"),
    path("<int:pk>/booklog/",CreateBooklLog.as_view(),name="booklog"),
    path("bookdel/<int:pk>/", delete_book_log, name="book-delete"),
    path("<int:pk>/classlog/",CreateClasslLog.as_view(),name="classlog"),
    path("classdel/<int:pk>/", delete_class_log, name="class-delete"),
    path("<int:pk>/examlog/",CreateExamLog.as_view(),name="examlog"),
    path("examdel/<int:pk>/", delete_exam_log, name="exam-delete"),
    path("<int:pk>/certificatelog/",CreateCertificateLog.as_view(),name="certificatelog"),
    path("certificatedel/<int:pk>/", delete_certificate_log, name="certificate-delete"),
    
]
