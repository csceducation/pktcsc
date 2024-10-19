from django.db import models
from django.urls import reverse
from django.utils import timezone
from apps.staffs.models import Staff
from apps.corecode.models import AcademicSession, AcademicTerm, StudentClass,Bill
from apps.students.models import Student
import json
from datetime import date
from apps.revenue.models import GST

class Invoice(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, default=None)
    status = models.CharField(
        max_length=20,
        choices=[("active", "Active"), ("closed", "Closed")],
        default="active",
    )
    _past_dues = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["student"]

    def __str__(self):
        return f"{self.student}"
    
    def balance(self):
        return self.total_amount_payable() - self.total_amount_paid()
    
    def amount_payable(self):
        return sum(item.amount for item in InvoiceItem.objects.filter(invoice=self))
    
    def total_amount_payable(self):
        return self.amount_payable()
    
    def total_amount_paid(self):
        return sum(receipt.amount_paid for receipt in Receipt.objects.filter(invoice=self))

    def get_absolute_url(self):
        return reverse("invoice-detail", kwargs={"pk": self.pk})

    def add_past_due(self, due):
        past_dues = self._past_dues
        if isinstance(past_dues, str):
            past_dues = json.loads(past_dues)
        
        past_due_dict = {
            'id': due.id,
            'amount': str(due.amount),
            'due_date': str(due.due_date) if isinstance(due.due_date, date) else due.due_date
        }
        past_dues.append(past_due_dict)
        self._past_dues = past_dues
        self.save()

    @property
    def get_past_dues(self):
        return self._past_dues
    
    def update_dues(self):
        total_due_amount = sum(due.amount for due in self.dues.all())
        if self.balance() <= 0:
            for due in self.dues.all():
                due.delete()
        self.save()

    def update_dues_based_on_receipt(self, receipt_amount,due_date=None,next_due_amount=None):
        dues = self.dues.all().order_by('due_date')

        remaining_amount = int(receipt_amount)
        if dues.exists():
            for due in dues:
                if remaining_amount >= due.amount:
                    # If receipt amount is greater than or equal to due amount, delete the due
                    remaining_amount -= due.amount
                    due.delete()
                else:
                    # If receipt amount is less than due amount, update due with remaining amount
                    due.amount -= remaining_amount
                    due.save()
                    remaining_amount = 0  # No remaining amount after this due is updated
                    break
        else:
            # Handle the case where there are no dues
            print("No existing dues to apply the receipt amount.")
            remaining_amount = 0  # Reset remaining amount as there's nothing to apply it to

        # If there is remaining amount after updating dues, create a new due with the remaining amount
        if remaining_amount > 0 or due_date:
            if next_due_amount:
                remaining_amount += next_due_amount
            new_due_date = due_date # Set the due date as current date
            print("next due date printed in the upate_function ",new_due_date)
            Due.objects.create(invoice=self, amount=remaining_amount, due_date=new_due_date)
            self.update_dues()

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    description = models.CharField(max_length=200)
    amount = models.IntegerField()


class Receipt(models.Model):
    
    Bill_No = models.CharField(max_length=245, default=None)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    amount_paid = models.IntegerField()
    date_paid = models.DateField(default=timezone.now)
    comment = models.CharField(max_length=200, blank=True)
    received_by = models.ForeignKey(Staff, verbose_name="Billing Staff", on_delete=models.DO_NOTHING)
    org_amount = models.FloatField(null=True)
    gst_amount = models.FloatField(null=True)
    def __str__(self):
        return f"Receipt on {self.date_paid}"

    
    def save(self, *args, **kwargs):
        bill = Bill.objects.filter().first()
        if self.Bill_No.startswith(bill.prefix):
            bill.last_bill = self.Bill_No[len(bill.prefix):]
            bill.save()

        # Cast amount_paid to integer
        self.amount_paid = int(float(self.amount_paid))
        
        next_due_date = kwargs.pop('next_due_date')
        next_due_amount = kwargs.pop('next_due_amount')
        
        gst_obj = GST.objects.first()
        amt,gst = None,None
        if gst_obj.gst_number:
            paid = float(self.amount_paid)
            amt, gst = gst_obj.calculate_gst(paid)
        
        self.org_amount = amt
        self.gst_amount = gst
        
        super().save(*args, **kwargs)
        self.invoice.update_dues_based_on_receipt(self.amount_paid, next_due_date, next_due_amount)

        
    @property
    def get_last_bill(self,Bill):
        bill = Bill.objects.filter().first()

class Due(models.Model):
    due_choice = [("Paid","Paid"),("Pending","Pending")]
    due_status = models.TextField("Due Status",choices=due_choice,default="Pending",max_length=255)
    invoice = models.ForeignKey(Invoice, related_name='dues', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def extend_due(self, new_due_date):
        self.due_date = new_due_date
        self.extended = True
        self.save()

    def delete(self, *args, **kwargs):
        self.invoice.add_past_due(self)
        super().delete(*args, **kwargs)

    @staticmethod
    def dues_for_student(student):
        return Due.objects.filter(invoice__student=student)
