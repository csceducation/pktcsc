from django.urls import path

from . import views

urlpatterns = [
    path('today',views.today_income,name="today"),
    path("month", views.month_income , name="month"),
    path("revenue",views.all_income,name="all"),
    path("statments",views.bill_statement,name="bill_statement")
]