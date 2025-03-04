from django.urls import path

from . import views

urlpatterns = [
    path('daystatement', views.daystatement, name="day-statement"),
    path('collectiveview', views.Collectivestatement, name="collective-view"),
    path('today', views.today_income, name="today"),
    path("statments", views.bill_statement, name="bill_statement"),
    path("account-insert", views.AccountsCreateView.as_view(), name="account-insert-create"),
    path("account-delete/<int:pk>/", views.AccountsDeleteView.as_view(), name="account-insert-delete"),
    path("dailyactivity",views.Dayactivity, name="daily-activity"),
]