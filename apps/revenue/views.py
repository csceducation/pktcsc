import datetime 
from django.db.models import F, Sum,Q
from django.shortcuts import render
from django.views.generic.edit import UpdateView, DeleteView
from ..finance import models as finmod
from ..students import models as stumod
from apps.finance.models import Due
from .models import Accounts,DailyAccountData
from .forms import AccountsForm
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView, DeleteView,CreateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from ..corecode.models import AccountHeading
from ..enquiry.models import Enquiry
from ..finance.models import Due
from ..batch.models import BatchModel




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
""" 
def month_income(request):
    month = request.GET.get('month')
    month1 = datetime.datetime.now().month
    rec = finmod.Receipt.objects.filter(date_paid__month = month or month1)
    total_col = deep2
    return render(request ,"month.html",context={
        "recipt":rec,
        "today_col":total_col
    })
def all_income(request):
    rec = finmod.Receipt.objects.all()
    total_col = deep2
    return render(request ,"revenue.html",context={
        "recipt":rec,
        
        "today_col":total_col
    }) """

def bill_statement(req):

    if req.method == 'POST':
        
        start_date = req.POST.get('start_date')
        end_date = req.POST.get('end_date')
        
        # Initialize variables
        total_col = total_gst = total_amm = 0
        
        # Check if start_date and end_date are provided
        if start_date and end_date:
            # Parse the start_date and end_date from string to datetime.date
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
            
            
            # Filter receipts within the date range
            filtered_bills = finmod.Receipt.objects.filter(date_paid__range=[start_date, end_date]).order_by('date_paid', 'Bill_No')
            total_col = round(filtered_bills.aggregate(total=Sum('amount_paid'))['total'] , 2)
            total_gst = round(filtered_bills.aggregate(total=Sum('gst_amount'))['total'],2)
            total_amm = round(filtered_bills.aggregate(total=Sum('org_amount'))['total'],2)

           
        else:
            filtered_bills = []
            
    else:
        filtered_bills = []
        total_col = total_gst = total_amm = 0
    print("hi")
    return render(req, 'today.html', {'bills': filtered_bills,'total_col':total_col,'total_gst':total_gst,'total_amm':total_amm,'startd':start_date,'endd':end_date,'outstanding_amount':outstanding_amount,'collected_amount':collected_amount,'collectable_amount':collectable_amount})


class AccountsCreateView(CreateView):
    """
    View to create a new account using the AccountsForm.
    """
    form_class = AccountsForm
    template_name = 'accounts_form.html'
    success_url = '/revenue/daystatement'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)



class AccountsDeleteView(DeleteView):
    """
    View to delete an existing account.
    """
    model = Accounts
    template_name = 'corecode/core_confirm_delete.html'
    success_url = reverse_lazy('day-statement')
    pk_url_kwarg = 'pk'  # Ensure the URLconf includes 'pk'

    def get_object(self, queryset=None):
        """
        Override get_object to fetch the account by id from the URL.
        """
        obj = super().get_object(queryset)
        return obj


def daystatement(request):
    try:
        op_ba = DailyAccountData.objects.first()
    except DailyAccountData.DoesNotExist:
        op_ba = None
    if request.method == 'POST':
        date = request.POST.get('date')
    else:
        date = str(datetime.date.today())
    
    date_obj = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    opening_balance = calculate_opening_balance(date_obj - datetime.timedelta(days=1))
    day_income = calculate_day_income(date)
    day_expense = calculate_day_expense(date)
    closing_balance = calculate_closing_balance(opening_balance, day_income, day_expense)
    accounts = Accounts.objects.filter(Date=date)

    return render(request, "day_view.html", context={
        'date': date,
        'opening_balance': opening_balance,
        'day_income': day_income,
        'day_expense': day_expense,
        'closing_balance': closing_balance,
        'accounts': accounts,
    })


def calculate_opening_balance(date):
    op_ba = DailyAccountData.objects.first()
    start_date = op_ba.date
    rec = finmod.Receipt.objects.filter(date_paid__range=[start_date, date]) 
    rec = rec if rec else 0
    income_via_other = Accounts.objects.filter(Date__range=[start_date, date], Type='Credit')
    
    if income_via_other:
        income_via_other = income_via_other.aggregate(total=Sum('Amount'))['total']
    else:
        income_via_other = 0
    deep = Accounts.objects.filter(Date__range=[start_date, date], Type='Debit')
    if deep:
        opening_balance =( op_ba.opening_balance + income_via_other + rec.aggregate(total=Sum('amount_paid'))['total']) - deep.aggregate(total=Sum('Amount'))['total']
    else:
        opening_balance = op_ba.opening_balance + income_via_other +( rec.aggregate(total=Sum('amount_paid'))['total'] if rec else 0)
    return opening_balance


def calculate_day_income(date):
    rec = finmod.Receipt.objects.filter(date_paid=date)
    income_via_other = Accounts.objects.filter(Date=date, Type='Credit').aggregate(total=Sum('Amount'))['total']
    if income_via_other:
        day_income = rec.aggregate(total=Sum('amount_paid'))['total'] + income_via_other
    else:
        day_income = rec.aggregate(total=Sum('amount_paid'))['total']
    return day_income


def calculate_day_expense(date):
    day_expense = Accounts.objects.filter(Date=date, Type='Debit').aggregate(total=Sum('Amount'))['total']
    return day_expense


def calculate_closing_balance(opening_balance, day_income, day_expense):
    if day_income and day_expense:
        closing_balance = opening_balance + day_income - day_expense
    else:
        closing_balance = 0
    return closing_balance


def Collectivestatement(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
    else:
        start_date = str(datetime.date.today().replace(day=1))
        current_date = datetime.date.today()
        next_month = current_date.replace(day=28) + datetime.timedelta(days=4)
        end_date = next_month - datetime.timedelta(days=next_month.day)
    acc = Accounts.objects.filter(Date__range=[start_date, end_date])
    total_expense = acc.filter(Type='Debit').aggregate(total=Sum('Amount'))['total']
    rec = finmod.Receipt.objects.filter(date_paid__range=[start_date, end_date])
    income_via_other = Accounts.objects.filter(Date__range=[start_date, end_date], Type='Credit').aggregate(total=Sum('Amount'))['total'] or 0
    deep2 = rec.aggregate(total=Sum('amount_paid'))['total']
    if income_via_other:
        income = deep2 + income_via_other
    else:
        income = deep2 or 0
    expense = Accounts.objects.filter(Date__range=[start_date, end_date], Type='Debit').aggregate(total=Sum('Amount'))['total'] if Accounts.objects.filter(Date__range=[start_date, end_date], Type='Debit').aggregate(total=Sum('Amount'))['total'] else 0
    
    opening_balance = calculate_opening_balance(datetime.datetime.strptime(start_date, "%Y-%m-%d").date() - datetime.timedelta(days=1))
    
    Headings = Accounts.objects.values('Heading').distinct()
    heading_expenses = {}
    for heading in Headings:
        heading_name = AccountHeading.objects.get(pk=heading['Heading']).name
        total_expense = Accounts.objects.filter(Date__range=[start_date, end_date], Type='Debit', Heading=heading['Heading']).aggregate(total=Sum('Amount'))['total']
        heading_expenses[heading_name] = total_expense

    closing_balance = opening_balance + income - expense
    return render(request, 'collective_view.html', {'start_date': start_date, 'end_date': end_date, 'opening_balance': opening_balance, 'income': income, 'expense': expense, 'closing_balance': closing_balance, 'heading_expenses': heading_expenses})


def Dayactivity(request):
    if request.method == 'POST':
        date = request.POST.get('date')
    else:
        date = str(datetime.date.today())

    #Expected Addmission
    batches = BatchModel.objects.all()
    expected_admission = Enquiry.objects.filter(expected_date__lte=date, enquiry_status='Following')
    today_due_bills = Due.objects.filter(due_date__lte=date)
    expired_batches = batches.filter(batch_end_date__lte=date, batch_status="Active")

    
    return render(request, 'dayactivity.html', {
        'date': date,
        'expected_admission': expected_admission,
        'today_due_bills': today_due_bills,
        'ending_batches': expired_batches,
    })
     

    