from django.urls import path
from .views import *
urlpatterns = [
    path("labs",labs,name="lab_list"),
    path("add_lab",create_labs,name="add_labs"),
    path("lab_detail/<int:lab_id>/",lab_details,name="lab_details"),
    path("delete_lab/<int:lab_id>/",delete_lab,name="delete_lab"),
    path("add_system/<int:lab_id>/",add_systems,name = "add_system"),
    path("delete_system/<int:lab_id>/<str:system_name>/",delete_system,name = "delete_system"),
    path("add_lab_attendance/<int:lab_id>/",add_lab_attendance,name="add_lab_attendance"),
    path("delete_lab_attendance/<int:student_id>/<int:lab_id>/<str:date>/<str:system_no>/",delete_lab_attendance_data,name="data_delete"),
    path("add_theory_attendance/<int:batch_id>/",add_theory_attendance,name="theory_attendance"),
    path('staffs/day/', staff_attendance, name='staff_attendance'),
    path('students/day', student_attendance, name='student_attendance'),
    path('day_dashboard',day_dashboard,name="day_dashboard"),
    path("delete_staff_attendance/<str:date>/<int:staff_id>/",delete_staff_attendance,name="delete_staff_attendance"),
    path("delete_student_attendance/<str:date>/<int:student_id>/",delete_student_attendance,name="delete_student_attendance"),
    path('select/feature',router,name="router"),
    path('lab_dashboard/<int:lab_id>/',lab_dashboard,name="lab_dashboard"),
    path('theory_dashboard/',theory_dashboard,name="theory_dashboard"),
    path("profile_redirector/<int:enrol_no>/",profile_redirector,name="profile_redirector")
]