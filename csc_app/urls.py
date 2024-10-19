"""newapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from apps.enquiry.views import StudentEnquiryFormCreateView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path,re_path
from django.views.static import serve
from apps.students import views
from apps.corecode.views import logout_view,login_url
handler404 = 'apps.students.views.handler404'
urlpatterns = [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    path('login/<str:username>/<str:password>/', login_url, name='login_url'),
    path('admin/', admin.site.urls , name='admin'),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("apps.corecode.urls")),
    path("student/", include("apps.students.urls")),
    path("staff/", include("apps.staffs.urls")),
    path("finance/", include("apps.finance.urls")),
    path("result/", include("apps.result.urls")),
    path("enquiry/",include("apps.enquiry.urls")),
    path('public/student/<int:pk>/', views.PublicView.as_view(), name='public_student_profile'),
    path('public/student/<int:pk>/attendance', views.attendance_test, name='public_student_profile_attendance'),
    path("revenue/", include("apps.revenue.urls")),
    path("course/", include("apps.course.urls")),
    path("batches/",include("apps.batch.urls")),
    path("attendance/",include("apps.attendancev2.urls")),
    path('logout/',logout_view, name='logout'),
    path('enquiryform',StudentEnquiryFormCreateView.as_view(),name='enquiryform')
] 


