from django.urls import path
from .views import *
urlpatterns = [
    path("labs",labs,name="lab_list"),
    path("add_lab",create_labs,name="add_labs"),
    path("lab_detail/<int:lab_id>/",lab_details,name="lab_details"),
    path("delete_lab/<int:lab_id>/",delete_lab,name="delete_lab"),
    path("add_system/<int:lab_id>/",add_systems,name = "add_system"),
    path("delete_system/<int:lab_id>/<str:system_name>/",delete_system,name = "delete_system"),
    #------------------old urls-------------------
    # path("add_lab_attendance/<int:lab_id>/",add_lab_attendance,name="add_lab_attendance"),
    # path("delete_lab_attendance/<int:student_id>/<int:lab_id>/<str:date>/<str:system_no>/",delete_lab_attendance_data,name="data_delete"),
    # path("add_theory_attendance/<int:batch_id>/",add_theory_attendance,name="theory_attendance"),
    #--------new urls for angular testing---------
    path('theory_attendance/<int:batch_id>',show_form,name="theory_attendance_form"),
    path("api/batch_details/<int:batch_id>/",pre_batch_details,name="pre_batch_details"),# new one for testing angular
    path("api/save_theory/<int:batch_id>/",save_theory_attendance,name="save_theory_attendance"),# new one for testing angular
    path("api/batch_attendances/<int:batch_id>/",get_theory_attendance,name="get_theory_attendance"),# new one for testing angular
    path('theory_dashboard/',show_theory_dashboard,name="theory_dashboard"),
    #-----------new lab url ---------------------
    path('lab_attendance_form/',show_lab_form,name="lab_attendance_form"),
    path('api/systems/<int:lab_id>/',get_systems,name="systems"),
    path('api/lab_attendance/<int:lab_id>/<str:date>',get_lab_attendance,name="get_lab_attendance"),
    path('api/lab_sys_data/<int:lab_id>/<str:date>/<str:sys_no>/<str:start>/<str:end>',get_lab_sys_data,name="get_lab_sys_data"),
    path('api/save_lab_attendance/<int:lab_id>/<str:date>/',add_lab_data,name="save_lab_attendance"),
    path('api/delete_lab_attendance/<int:lab_id>/<str:date>/',delete_lab_data,name="delete_lab_attendance"),
    path('api/dashboard/get_staff_data/<int:staff_id>/<str:from_date>/<str:to_date>/',staff_dashboard_data,name="staff_dashboard_data"),
    #--------previous---------------------------
    path('staffs/day/', staff_attendance, name='staff_attendance'),
    path('students/day', student_attendance, name='student_attendance'),
    path('day_dashboard',day_dashboard,name="day_dashboard"),
    path("delete_staff_attendance/<str:date>/<int:staff_id>/",delete_staff_attendance,name="delete_staff_attendance"),
    path("delete_student_attendance/<str:date>/<int:student_id>/",delete_student_attendance,name="delete_student_attendance"),
    path('select/feature',router,name="router"),
    path('lab_dashboard/<int:lab_id>/',lab_dashboard,name="lab_dashboard"),
    path("profile_redirector/<int:enrol_no>/",profile_redirector,name="profile_redirector")
]