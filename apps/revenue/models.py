from django.db import models
from django.db.models import Sum
import math
from ..finance import models as mod


class revenue(models.Model):
    Total_student = models.IntegerField(default=None)
    Total_paid = models.DecimalField(max_digits=10 , decimal_places=2)
    Total_Income = models.DecimalField(max_digits=10 , decimal_places=2)
    Total_Balance = models.DecimalField(max_digits=10 , decimal_places=2)

    def total_student(self):
        total_count = mod.Invoice.objects.count()
        self.Total_student = total_count
        return total_count
    def total_income(self):
        income = mod.Invoice.objects.all()
        total_incomes = mod.Invoice.objects.aggregate(total=Sum('total_amount_payable'))
        total_income_value = total_incomes['total']
        self.Total_Income = total_income_value
        return total_income_value
    def total_paid(self):
        paid = mod.Invoice.objects.all()
        total_paids = mod.Invoice.objects.aggregate(total=Sum('total_amount_paid'))
        total_paid_value = total_paids['total']
        self.Total_paid = total_paid_value
        return total_paid_value
    def total_balance(self):
        balance = mod.Invoice.objects.all()
        total_balance = mod.Invoice.objects.aggregate(total=sum('balance'))
        total_balance_value = total_balance['total']
        self.Total_Balance  = total_balance_value
        return total_balance_value




class GST(models.Model):
    percent = models.FloatField()
    gst_number = models.CharField(max_length=15, blank=True, null=True)
    
    def calculate_gst(self,price):
        gst = round((price * self.percent) / (100+self.percent),2)
        amount = round(price - gst,2)
        return (amount,gst)