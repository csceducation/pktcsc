from django.urls import path

from .views import (
    StaffCreateView,
    StaffDeleteView,
    StaffDetailView,
    StaffListView,
    StaffInActiveListView,
    StaffUpdateView,
    get_staff_subjects
)

urlpatterns = [
    path("list/", StaffListView.slist, name="staff-list"),
    path("inactive", StaffInActiveListView.slist, name="staff-inactive-list"),
    path("<int:pk>/", StaffDetailView.as_view(), name="staff-detail"),
    path("create/", StaffCreateView.as_view(), name="staff-create"),
    path("<int:pk>/update/", StaffUpdateView.as_view(), name="staff-update"),
    path("<int:pk>/delete/", StaffDeleteView.as_view(), name="staff-delete"),
    path('get_staffs/<int:subject_id>/', get_staff_subjects, name='get_staffs'),
]
