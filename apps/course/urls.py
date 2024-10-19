from django.urls import path
from .views import CourseCreateView,delete_exam_log,ExamCreateView,CourseListView,CourseDetailView,CourseDeleteView,CourseUpdateView,SubjectCreateView,delete_subject_log,BookCreateView,delete_book_log

urlpatterns = [
    path('create/', CourseCreateView.as_view(), name='create_course'),
    path('', CourseListView.slist, name='list_course'),
    path('course-details/<int:pk>/', CourseDetailView.as_view(), name='details_course'),
    path("delete/<int:pk>/", CourseDeleteView.as_view(), name="course-delete"),
    path("<int:pk>/update/", CourseUpdateView.as_view(), name="course-update"),
    path("<int:pk>/create-subject/",SubjectCreateView.as_view(),name="subjectcreate"),    
    path("course-subject-delete/<int:pk>/<str:subject_name>/", delete_subject_log, name="course-subject-delete"),
    path("<int:pk>/create-book/",BookCreateView.as_view(),name="bookcreate"),    
    path("course-book-delete/<int:pk>/<str:book_name>/", delete_book_log, name="course-book-delete"),
    path("<int:pk>/create-exam/",ExamCreateView.as_view(),name="examcreate"),    
    path("course-exam-delete/<int:pk>/<str:exam_name>/", delete_exam_log, name="course-exam-delete"),



    # Add other URL patterns as needed
]
