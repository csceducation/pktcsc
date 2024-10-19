import datetime

from django.db.models import F, Sum
from django.shortcuts import render

from ..finance import models as finmod
from ..students import models as stumod
from apps.finance.models import Due

def get_deadline_due():
    dues = Due.objects.filter(due_date=datetime.date.today())
    return dues

def total_student():
    total_stud = stumod.Student.objects.count()
    totals = total_stud
    return totals

def total_income():
    total_am = finmod.Invoice.objects.all()
    total_ammount = sum(account.total_amount_payable() for account in total_am)
    return total_ammount

def total_paid():
    total_pa = finmod.Receipt.objects.all()
    total_pait = total_pa.aggregate(total=Sum('amount_paid'))['total']
    return total_pait

def total_balance():
    total_bal = finmod.Invoice.objects.all()
    total_balanc = sum(account.balance() for account in total_bal)
    return total_balanc


#------------------------------------------------------------------------------

def today_income(request):
    global total_col
    date = datetime.date.today()
    rec = finmod.Receipt.objects.filter(date_paid = date)
    total_col = rec.aggregate(total=Sum('amount_paid'))['total']
    return render(request ,"today.html",context={
        "recipt":rec,
        "date":date,
        "today_col":total_col,
    })
def month_income(request):
    month = request.GET.get('month')
    month1 = datetime.datetime.now().month
    rec = finmod.Receipt.objects.filter(date_paid__month = month or month1)
    total_col = rec.aggregate(total=Sum('amount_paid'))['total']
    return render(request ,"month.html",context={
        "recipt":rec,
        "today_col":total_col
    })
def all_income(request):
    rec = finmod.Receipt.objects.all()
    total_col = rec.aggregate(total=Sum('amount_paid'))['total']
    return render(request ,"revenue.html",context={
        "recipt":rec,
        
        "today_col":total_col
    })

def bill_statement(req):
    if req.method == 'POST':
        start_date = req.POST.get('start_date')
        end_date = req.POST.get('end_date')
        
        # Check if start_date and end_date are provided
        if start_date and end_date:
            # Parse the start_date and end_date from string to datetime.date
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
            
            
            
            # Filter receipts within the date range
            filtered_bills = finmod.Receipt.objects.filter(date_paid__range=[start_date, end_date])
            total_col = filtered_bills.aggregate(total=Sum('amount_paid'))['total']
            total_gst = filtered_bills.aggregate(total=Sum('gst_amount'))['total']
            total_amm = filtered_bills.aggregate(total=Sum('org_amount'))['total']
           
        else:
            filtered_bills = []
            
    else:
        filtered_bills = []
       
    return render(req, 'today.html', {'bills': filtered_bills,'total_col':total_col,'total_gst':total_gst,'total_amm':total_amm,'startd':start_date,'endd':end_date})
