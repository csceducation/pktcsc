from django.urls import path
from .views import BatchListView,AddStudentView, BatchDetailView, BatchCreateView, BatchUpdateView, BatchDeleteView,delete_batchstudent_log

urlpatterns = [
    path('', BatchListView, name='batch_list'),
    path('<int:pk>/', BatchDetailView.as_view(), name='batch_detail'),
    path('create/', BatchCreateView.as_view(), name='batch_create'),
    path('<int:pk>/update/', BatchUpdateView.as_view(), name='batch_update'),
    path('<int:pk>/delete/', BatchDeleteView.as_view(), name='batch_delete'),
    path("batch-stu-delete/<int:pk>/<int:id>/", delete_batchstudent_log, name="batchstudelete"),
    path('<int:pk>/add-student/', AddStudentView.as_view(), name='add_student'),

]
