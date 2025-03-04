from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import HttpResponseRedirect, redirect, render
from django.urls import reverse_lazy
from django.contrib.auth import logout
from django.views.generic import ListView, TemplateView, View
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic import DetailView
from functools import wraps
from ..revenue.models import DailyAccountData
from django.utils.decorators import method_decorator
from ..revenue import views
from .forms import (
    AcademicSessionForm,
    AcademicTermForm,
    CurrentSessionForm,
    SiteConfigForm,
    StudentClassForm,
    SubjectForm,
    BookForm,
    ExamForm,
    TimeForm,
    AccountHeadingForm,
    SchemesForm,
    InventoryForm
    
)
from .models import (
    AcademicSession,
    AcademicTerm,
    SiteConfig,
    StudentClass,
    Subject,
    Book,Exam,Time,Bill,AccountHeading,Schemes,Inventory
)
from apps.revenue.models import GST

#---dashboard--
from django.utils import timezone
from apps.students.models import Student
from apps.finance.models import Invoice
from apps.enquiry.models import Enquiry
from apps.batch.models import BatchModel
from django.db.models import Sum,Count,Case, When, IntegerField, F
# import datetime
from django.contrib.contenttypes.models import ContentType
import json
from django.core.serializers.json import DjangoJSONEncoder
from django import forms
from collections import defaultdict
from datetime import datetime, timedelta,date
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, TruncYear


def get_month_start_end(date_obj=None):
    """Gets the start and end date of the month for the given date. 
    If no date is given, it defaults to today.
    """
    if date_obj is None:
        date_obj = date.today()

    # Get the first day of the month
    start_date = date(date_obj.year, date_obj.month, 1)

    # Get the last day of the month
    next_month = date_obj.replace(day=28) + timedelta(days=4)  # Go to next month
    end_date = next_month - timedelta(days=next_month.day)

    return start_date, end_date



"""
decorators and page access functions
"""
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
import base64

def login_url(request, username, password:str):
    password = base64.b64decode(password).decode('utf-8')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        if user.is_superuser:
            return redirect("/")
        elif user.is_staff and not user.is_superuser:
            user=user.staff_profile
            return redirect(user.get_absolute_url())
        elif not user.is_staff :
            user=user.student_profile
            return redirect('public_student_profile',pk=user.id)
        else:
            return redirect("accounts/login")
    else:
        return HttpResponse("Invalid username or password")

def entry_restricted(request,*args,**kwargs):
    return render(request=request,template_name='corecode/entry_restricted.html',)



def staff_student_restricted(user):
    if user.is_superuser:
        return True
    else:
        return False

def student_restricted(user):
    if user.is_superuser or user.is_staff:
        return True
    else:
        return False
    



def student_entry_resricted():
    def decorator(view):
        @wraps(view)
        def _wrapped_view(request, *args, **kwargs):
            if not student_restricted(request.user):
                return redirect('login')
            return view(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def staff_student_entry_restricted():
    def decorator(view):
        @wraps(view)
        def _wrapped_view(request, *args, **kwargs):
            if not staff_student_restricted(request.user):
                return redirect('login')
            return view(request, *args, **kwargs)
        return _wrapped_view
    return decorator

"""
Views
"""

@method_decorator(student_entry_resricted(),name='dispatch')
class IndexView(LoginRequiredMixin, TemplateView):
    def index(request):
        # v2 = request.GET.get("v2")
        # if v2:
            # return redirect('detailed_dashboard')
        options_selected = request.GET.get('opti')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        scheme_id = request.GET.get('scheme')
        today = timezone.now().strftime('%Y-%m-%d')
        analize_vice = 'Period'
        if options_selected == 'scheme':
            analize_vice = 'scheme'
            students = Student.objects.filter(scheme=Schemes.objects.get(id=scheme_id))
            invoices = Invoice.objects.filter(student__in=students)
            start_date = Schemes.objects.get(pk=scheme_id).start_date
            end_date = Schemes.objects.get(pk=scheme_id).end_date
            enquiries = Enquiry.objects.filter(enquiry_date__range=[start_date,end_date])
            
            if enquiries:
                enquiry_data = {
                    'total': enquiries.count(),
                    'admitted': enquiries.filter(enquiry_status='Admitted').count(),
                    'following': enquiries.filter(enquiry_status='Following').count(),
                    'dropped': enquiries.filter(enquiry_status='Rejected').count()
                }
            else:
                enquiry_data = {}
                
            batches = BatchModel.objects.filter(batch_status = "Active")
            batch_count = batches.count()
            #print(batch_count)
            completed = 0
            for batch in batches:
                if batch.get_attendance_data(today):
                    completed += 1
            batch_data = {
                'total':batch_count,
                'completed':completed,
                'not_completed':(batch_count-completed)
            }
            

            total_invoice_amount = sum(invoice.total_amount_payable() for invoice in invoices)
            
            total_collected_amount = invoices.aggregate(Sum('receipt__amount_paid'))['receipt__amount_paid__sum'] or 0
            
            total_admissions = students.count()
            
            avg_invoice_amount = total_invoice_amount / total_admissions if total_admissions > 0 else 0
            if  total_invoice_amount != 0:
                cr_percent = round((total_collected_amount/total_invoice_amount) * 100,2)
            else:
                cr_percent = 0
            print("hi")
            course_admissions = students.values('course__course_name').annotate(admission_count=Count('course')).order_by('-admission_count')
            scheme_list = Schemes.objects.filter(scheme_status='Active')
            context = {
                'via':analize_vice,
                'start_date':start_date,
                'end_date':end_date,
                'dashboard':True,
                'total_invoices':total_admissions,
                'total_invoice_amount': total_invoice_amount,
                'total_collected_amount': total_collected_amount,
                'average_per_admission': round(avg_invoice_amount,2),
                'cr_percent':cr_percent,
                'course_admissions': course_admissions,
                'students':students,
                'enquiry_data':enquiry_data,
                'batch_data':batch_data,
                'schemes':scheme_list
            }


            return render(request, 'index.html', context)
        
        else:
            
            if not start_date or not end_date:
                start_date,end_date = get_month_start_end()
            if start_date and end_date: 
                students = Student.objects.filter(date_of_admission__range=[start_date, end_date])
                invoices = Invoice.objects.filter(student__in=students)
                enquiries = Enquiry.objects.filter(enquiry_date__range=[start_date,end_date])
                if enquiries:
                    enquiry_data = {
                        'total': enquiries.count(),
                        'admitted': enquiries.filter(enquiry_status='Admitted').count(),
                        'following': enquiries.filter(enquiry_status='Following').count(),
                        'dropped': enquiries.filter(enquiry_status='Rejected').count()
                    }
                else:
                    enquiry_data = {}
                    
                batches = BatchModel.objects.filter(batch_status = "Active")
                batch_count = batches.count()
                #print(batch_count)
                completed = 0
                for batch in batches:
                    if batch.get_attendance_data(today):
                        completed += 1
                batch_data = {
                    'total':batch_count,
                    'completed':completed,
                    'not_completed':(batch_count-completed)
                }
                

                total_invoice_amount = sum(invoice.total_amount_payable() for invoice in invoices)
                
                total_collected_amount = invoices.aggregate(Sum('receipt__amount_paid'))['receipt__amount_paid__sum'] or 0
                
                total_admissions = students.count()
                
                avg_invoice_amount = total_invoice_amount / total_admissions if total_admissions > 0 else 0
                if  total_invoice_amount != 0:
                    cr_percent = round((total_collected_amount/total_invoice_amount) * 100,2)
                else:
                    cr_percent = 0

                course_admissions = students.values('course__course_name').annotate(admission_count=Count('course')).order_by('-admission_count')
                scheme_list = Schemes.objects.filter(scheme_status='Active')
                context = {
                    'via':analize_vice,
                    'start_date':start_date,
                    'end_date':end_date,
                    'dashboard':True,
                    'total_invoices':total_admissions,
                    'total_invoice_amount': total_invoice_amount,
                    'total_collected_amount': total_collected_amount,
                    'average_per_admission': round(avg_invoice_amount,2),
                    'cr_percent':cr_percent,
                    'course_admissions': course_admissions,
                    'students':students,
                    'enquiry_data':enquiry_data,
                    'batch_data':batch_data,
                    'schemes':scheme_list
                }


                return render(request, 'index.html', context)
        #return render(request,'finance/finance_index.html')
        return render(request,"index.html",context={
            "total_student":views.total_student,
            "total_income":views.total_income,
            "total_paid":views.total_paid(),
            "total_balance":views.total_balance,
            "pending_dues":views.get_deadline_due(),
        })


class SiteConfigView(LoginRequiredMixin, View):
    """Site Config View"""

    form_class = SiteConfigForm
    template_name = "corecode/siteconfig.html"

    def get(self, request, *args, **kwargs):
        formset = self.form_class(queryset=SiteConfig.objects.all())
        context = {"formset": formset}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        formset = self.form_class(request.POST)
        if formset.is_valid():
            formset.save()
            messages.success(request, "Configurations successfully updated")
        context = {"formset": formset, "title": "Configuration"}
        return render(request, self.template_name, context)


class SessionListView(LoginRequiredMixin, SuccessMessageMixin, ListView):
    model = AcademicSession
    template_name = "corecode/session_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = AcademicSessionForm()
        return context


class SessionCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = AcademicSession
    form_class = AcademicSessionForm
    template_name = "corecode/mgt_form.html"
    success_url = reverse_lazy("sessions")
    success_message = "New session successfully added"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Add new session"
        return context


class SessionUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = AcademicSession
    form_class = AcademicSessionForm
    success_url = reverse_lazy("sessions")
    success_message = "Session successfully updated."
    template_name = "corecode/mgt_form.html"

    def form_valid(self, form):
        obj = self.object
        if obj.current == False:
            terms = (
                AcademicSession.objects.filter(current=True)
                .exclude(name=obj.name)
                .exists()
            )
            if not terms:
                messages.warning(self.request, "You must set a session to current.")
                return redirect("session-list")
        return super().form_valid(form)


class SessionDeleteView(LoginRequiredMixin, DeleteView):
    model = AcademicSession
    success_url = reverse_lazy("sessions")
    template_name = "corecode/core_confirm_delete.html"
    success_message = "The session {} has been deleted with all its attached content"

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.current == True:
            messages.warning(request, "Cannot delete session as it is set to current")
            return redirect("sessions")
        messages.success(self.request, self.success_message.format(obj.name))
        return super(SessionDeleteView, self).delete(request, *args, **kwargs)


class TermListView(LoginRequiredMixin, SuccessMessageMixin, ListView):
    model = AcademicTerm
    template_name = "corecode/term_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = AcademicTermForm()
        return context


class TermCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = AcademicTerm
    form_class = AcademicTermForm
    template_name = "corecode/mgt_form.html"
    success_url = reverse_lazy("terms")
    success_message = "New term successfully added"


class TermUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = AcademicTerm
    form_class = AcademicTermForm
    success_url = reverse_lazy("terms")
    success_message = "Term successfully updated."
    template_name = "corecode/mgt_form.html"

    def form_valid(self, form):
        obj = self.object
        if obj.current == False:
            terms = (
                AcademicTerm.objects.filter(current=True)
                .exclude(name=obj.name)
                .exists()
            )
            if not terms:
                messages.warning(self.request, "You must set a term to current.")
                return redirect("term")
        return super().form_valid(form)


class TermDeleteView(LoginRequiredMixin, DeleteView):
    model = AcademicTerm
    success_url = reverse_lazy("terms")
    template_name = "corecode/core_confirm_delete.html"
    success_message = "The term {} has been deleted with all its attached content"

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.current == True:
            messages.warning(request, "Cannot delete term as it is set to current")
            return redirect("terms")
        messages.success(self.request, self.success_message.format(obj.name))
        return super(TermDeleteView, self).delete(request, *args, **kwargs)


class ClassListView(LoginRequiredMixin, SuccessMessageMixin, ListView):
    model = StudentClass
    template_name = "corecode/class_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = StudentClassForm()
        return context


class ClassCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = StudentClass
    form_class = StudentClassForm
    template_name = "corecode/mgt_form.html"
    success_url = reverse_lazy("classes")
    success_message = "New class successfully added"


class ClassUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = StudentClass
    fields = ["name"]
    success_url = reverse_lazy("classes")
    success_message = "class successfully updated."
    template_name = "corecode/mgt_form.html"


class ClassDeleteView(LoginRequiredMixin, DeleteView):
    model = StudentClass
    success_url = reverse_lazy("classes")
    template_name = "corecode/core_confirm_delete.html"
    success_message = "The class {} has been deleted with all its attached content"

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        print(obj.name)
        messages.success(self.request, self.success_message.format(obj.name))
        return super(ClassDeleteView, self).delete(request, *args, **kwargs)


class SubjectListView(LoginRequiredMixin, SuccessMessageMixin, ListView):
    model = Subject
    template_name = "corecode/subject_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = SubjectForm()
        return context


class SubjectCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Subject
    form_class = SubjectForm
    template_name = "corecode/mgt_form.html"
    success_url = reverse_lazy("subjects")
    success_message = "New subject successfully added"
    
    


class SubjectUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Subject
    fields = ["name","duration","contents"]
    success_url = reverse_lazy("subjects")
    success_message = "Subject successfully updated."
    template_name = "corecode/mgt_form.html"


class SubjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Subject
    success_url = reverse_lazy("subjects")
    template_name = "corecode/core_confirm_delete.html"
    success_message = "The subject {} has been deleted with all its attached content"

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message.format(obj.name))
        return super(SubjectDeleteView, self).delete(request, *args, **kwargs)

class BookListView(LoginRequiredMixin, SuccessMessageMixin, ListView):
    model = Book
    template_name = "corecode/book-list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = BookForm()
        # print(context['object_list'])
        context['stock'] = Inventory().books_stock()
        return context


class BookCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Book
    form_class = BookForm
    template_name = "corecode/mgt_form.html"
    success_url = reverse_lazy("book")
    success_message = "New Book successfully added"


class BookUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Book
    fields = ["name"]
    success_url = reverse_lazy("book")
    success_message = "Book successfully updated."
    template_name = "corecode/mgt_form.html"


class BookDeleteView(LoginRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy("book")
    template_name = "corecode/core_confirm_delete.html"
    success_message = "The Book {} has been deleted with all its attached content"

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message.format(obj.name))
        return super(BookDeleteView, self).delete(request, *args, **kwargs)
class TimeListView(LoginRequiredMixin, SuccessMessageMixin, ListView):
    model = Time
    template_name = "corecode/time_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = TimeForm()
        return context


class TimeCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Time
    form_class = TimeForm
    template_name = "corecode/mgt_form.html"
    success_url = reverse_lazy("time")
    success_message = "New time successfully added"


class TimeUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Time
    form_class = TimeForm
    success_url = reverse_lazy("time")
    success_message = "time successfully updated."
    template_name = "corecode/mgt_form.html"


class TimeDeleteView(LoginRequiredMixin, DeleteView):
    model = Time
    success_url = reverse_lazy("time")
    template_name = "corecode/core_confirm_delete.html"
    success_message = "The time {} has been deleted with all its attached content"

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message.format(obj.name))
        return super(BookDeleteView, self).delete(request, *args, **kwargs)
    
class ExamListView(LoginRequiredMixin, SuccessMessageMixin, ListView):
    model = Exam
    template_name = "corecode/exam_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = ExamForm()
        return context


class ExamCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Exam
    form_class = ExamForm
    template_name = "corecode/mgt_form.html"
    success_url = reverse_lazy("exam")
    success_message = "New Exam successfully added"


class ExamUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Exam
    fields = "__all__"
    success_url = reverse_lazy("exam")
    success_message = "Exam successfully updated."
    template_name = "corecode/mgt_form.html"


class ExamDeleteView(LoginRequiredMixin, DeleteView):
    model = Exam
    success_url = reverse_lazy("exam")
    template_name = "corecode/core_confirm_delete.html"
    success_message = "The Exam {} has been deleted with all its attached content"

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message.format(obj.name))
        return super(ExamDeleteView, self).delete(request, *args, **kwargs)
    
class AccountHeadingListView(LoginRequiredMixin, SuccessMessageMixin, ListView):
    model = AccountHeading
    template_name = "corecode/accountheading.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = AccountHeadingForm()
        return context


class AccountHeadingCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = AccountHeading
    form_class = AccountHeadingForm
    template_name = "corecode/mgt_form.html"
    success_url = reverse_lazy("account-headings")
    success_message = "New account heading successfully added"


class AccountHeadingUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = AccountHeading
    fields = ["name"]
    success_url = reverse_lazy("account-headings")
    success_message = "Account heading successfully updated."
    template_name = "corecode/mgt_form.html"


class AccountHeadingDeleteView(LoginRequiredMixin, DeleteView):
    model = AccountHeading
    success_url = reverse_lazy("account-headings")
    template_name = "corecode/core_confirm_delete.html"
    success_message = "The account heading {} has been deleted with all its attached content"

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message.format(obj.name))
        return super(AccountHeadingDeleteView, self).delete(request, *args, **kwargs)
    


class CurrentSessionAndTermView(LoginRequiredMixin, View):
    """Current SEssion and Term"""

    form_class = CurrentSessionForm
    template_name = "corecode/current_session.html"

    def get(self, request, *args, **kwargs):
        form = self.form_class(
            initial={
                "current_session": AcademicSession.objects.get(current=True),
                "current_term": AcademicTerm.objects.get(current=True),
            }
        )
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = self.form_Class(request.POST)
        if form.is_valid():
            session = form.cleaned_data["current_session"]
            term = form.cleaned_data["current_term"]
            AcademicSession.objects.filter(name=session).update(current=True)
            AcademicSession.objects.exclude(name=session).update(current=False)
            AcademicTerm.objects.filter(name=term).update(current=True)

        return render(request, self.template_name, {"form": form})


class BillDetailView(DetailView):
    model = Bill
    template_name = 'bill_detail.html'
    context_object_name = 'billx'

    def get_object(self):
        return Bill.objects.first()
    
    def get_context_data(self, **kwargs):
        # Get the existing context
        context = super().get_context_data(**kwargs)
        
        # Add another object, e.g., Customer, to the context
        context['gst'] = GST.objects.first()  # Example of returning another object
        context['bill'] = DailyAccountData.objects.first()
        return context
def create_opening_balance(request):
    if request.method == 'POST':
        amount = request.POST.get('op')
        date = request.POST.get('op_date')
        if not amount:
            messages.warning(request, 'Please provide both date and amount')
            return redirect('opening-balance')
        account_data = DailyAccountData.objects.first()
        account_data.date = date
        account_data.opening_balance = amount
        account_data.save()
        messages.success(request, 'Opening balance successfully updated')
        return redirect('bill-detail')
    return render(request, 'bill_detail.html')
class BillUpdateView(UpdateView):
    model = Bill
    template_name = 'bill_form.html'
    fields = ['prefix', 'last_bill']
    success_url = reverse_lazy('bill-detail')

    def get_object(self):
        return Bill.objects.first()

def save_gst_percent(request,*args,**kwargs):
    obj = GST.objects.first()
    obj.percent = request.GET.get('percent',18)
    obj.save()
    return redirect('bill-detail')

def save_gst_number(request,*args,**kwargs):
    obj = GST.objects.first()
    num = request.GET.get('gst_num',None)
    if num:
        obj.gst_number = num 
    obj.save()
    return redirect('bill-detail')


class InventoryCreateView(CreateView,SuccessMessageMixin):
    model = Inventory
    form_class = InventoryForm 
    template_name = "corecode/mgt_form.html"
    success_url = reverse_lazy("inventory-list")
    success_message = "Inventory updated successfully"
    

class InventoryListView(ListView):
    model = Inventory
    template_name = "corecode/inventory.html"

    def get_queryset(self):
        return Inventory.objects.values("order_id", "order_date", "items",'id')  # Fetch only required fields

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = InventoryForm()
        context['books'] = list(Book.objects.all().values())
        context["form"] = form

        return context


class InventoryUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Inventory
    fields = '__all__'
    success_url = reverse_lazy("inventory-list")
    success_message = "Stock successfully updated."
    template_name = "corecode/inventory-update.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['books'] = list(Book.objects.all().values())
        date_widget = forms.DateInput(attrs={'type': 'date'}) 
        context['form'].fields['order_date'].widget = date_widget
        return context

class InventoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Inventory
    success_url = reverse_lazy("inventory-list")
    template_name = "corecode/core_confirm_delete.html"
    success_message = "The stock {} has been deleted with all its attached content"

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message.format(obj.name))
        return super(Inventory, self).delete(request, *args, **kwargs)


"""
logout function to logout  a user using logout function from auth app
"""

def logout_view(request):
    logout(request)
    # Redirect to a different page after logout
    return redirect('login')  # Redirect to your login page

"""
decorators and page access functions
"""
def entry_restricted(request,*args,**kwargs):
    return render(request=request,template_name='corecode/entry_restricted.html',)



def staff_student_restricted(user):
    if user.is_superuser:
        return True
    else:
        return False

def student_restricted(user):
    if user.is_superuser or user.is_staff:
        return True
    else:
        return False
    



def student_entry_resricted():
    def decorator(view):
        @wraps(view)
        def _wrapped_view(request, *args, **kwargs):
            if not student_restricted(request.user):
                return redirect('login')
            return view(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def staff_student_entry_restricted():
    def decorator(view):
        @wraps(view)
        def _wrapped_view(request, *args, **kwargs):
            if not staff_student_restricted(request.user):
                return redirect('login')
            return view(request, *args, **kwargs)
        return _wrapped_view
    return decorator


"""
views for redirections of users to the appropriate page after login

here we changed the default login success url to our view belo and redirect them to next page

1.admin got redirected home page
2.staffs get redirected to their profile
3.studet get redirected to thier profile

a function that takes user argument and redirects them using their ID and also restricts them from viewing other profile using the same ID

"""


def redirector(request,*args,**kwargs):
    if request.user.is_superuser:
        return redirect("/")
    elif request.user.is_staff and not request.user.is_superuser:
        user=request.user.staff_profile
        return redirect(user.get_absolute_url())
    elif not request.user.is_staff :
        user=request.user.student_profile
        return redirect('public_student_profile',pk=user.id)
    else:
        return redirect("accounts/login")


def user_restricted(user,pk):# we have to say if it is thier profile or not so if i give false then it will redirect them to login page
    if user.is_superuser:
        return True
    elif user.is_staff:
        return user.staff_profile.id == pk
    elif not user.is_staff:
        return user.student_profile.id == pk



def different_user_restricted():
    def decorator(view):
        @wraps(view)
        def _wrapped_view(request, *args, **kwargs):
            pk = kwargs.get("pk")
            if not user_restricted(request.user,pk):
                return redirect('login')
            return view(request, *args, **kwargs)
        return _wrapped_view
    return decorator

class SchemeListView(LoginRequiredMixin, SuccessMessageMixin, ListView):
    model = Schemes
    template_name = "corecode/scheme-list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = SchemesForm()
        return context


class SchemeCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Schemes
    form_class = SchemesForm
    template_name = "corecode/mgt_form.html"
    success_url = reverse_lazy("scheme")
    success_message = "New Scheme successfully added"


class SchemeUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Schemes
    form_class = SchemesForm
    success_url = reverse_lazy("scheme")
    success_message = "Scheme successfully updated."
    template_name = "corecode/mgt_form.html"


class SchemeDeleteView(LoginRequiredMixin, DeleteView):
    model = Schemes
    success_url = reverse_lazy("scheme")
    template_name = "corecode/core_confirm_delete.html"
    success_message = "The Scheme {} has been deleted with all its attached content"

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message.format(obj.name))
        return super(SchemeDeleteView, self).delete(request, *args, **kwargs)


#---------- Error Pages ------------ #

def custom_404(request, exception):
    return render(request, '404.html', status=404)

def custom_500(request,exception):
    # Capture error details
    # error_details = traceback.format_exc()
    # print(request.user)
    return render(request, '500.html', status=500)
    
    
from django.conf.urls import handler404, handler500

handler404 = custom_404
handler500 = custom_500


#------------- dashboard ------------

def format_date(func):
    @wraps(func)
    def wrapper(date_input, *args, **kwargs):
        today = datetime.today()
        
        if date_input.lower() == "ytd":
            start_date = datetime(today.year, 1, 1)
            end_date = today
        elif date_input.lower().startswith("year:"):
            year = int(date_input.split(":")[1])
            start_date = datetime(year, 1, 1)
            end_date = datetime(year, 12, 31)
        elif date_input.lower().startswith("month:"):
            year, month = map(int, date_input.split(":")[1].split("-"))
            start_date = datetime(year, month, 1)
            next_month = month % 12 + 1
            next_month_year = year if next_month > 1 else year + 1
            end_date = datetime(next_month_year, next_month, 1) - timedelta(days=1)
        elif date_input.lower().startswith("week:"):
            year, week = map(int, date_input.split(":")[1].split("-"))
            start_date = datetime.strptime(f"{year}-W{week}-1", "%Y-W%W-%w")
            end_date = start_date + timedelta(days=6)
        elif date_input.lower().startswith("range:"):
            start_str, end_str = date_input.split(":")[1].split("to")
            start_date = datetime.strptime(start_str.strip(), "%Y-%m-%d")
            end_date = datetime.strptime(end_str.strip(), "%Y-%m-%d")
        else:
            raise ValueError("Invalid date format")
        
        return func(start_date, end_date, *args, **kwargs)
    
    return wrapper

@format_date
def dashboard_scheme_data(start_date, end_date):
    data = (
        Student.objects.filter(date_of_admission__range=(start_date, end_date))
        .values("scheme__name")
        .annotate(total_students=Count("id"))
        .order_by("-total_students")
    )
    return list(data)

@format_date
def dashboard_staff_data(start_date, end_date):
    data = (
        Student.objects.filter(date_of_admission__range=(start_date, end_date))
        .values(counsellor = F('if_enq__counsellor__name'))
        .annotate(total_students=Count('id'))
        .order_by("-total_students")
    )
    return list(data)

@format_date
def dashboard_course_data(start_date, end_date):
    data = (
        Student.objects.filter(date_of_admission__range=(start_date, end_date))
        .values("course__course_s_name")  
        .annotate(total_students=Count("id"))  
        .order_by("-total_students") 
    )
    return list(data)

@format_date
def dashboard_enquiry_data(start_date, end_date):
    # Step 1: Fetch enquiries grouped by course and staff
    enquiries = (
        Enquiry.objects.filter(enquiry_date__range=(start_date, end_date))
        .values("course_to_join__course_s_name", "counsellor__name")
        .annotate(total_enquiries=Count("enquiry_no"))
    )

    # Step 2: Fetch admissions grouped by course and staff
    admissions = (
        Student.objects.filter(date_of_admission__range=(start_date, end_date))
        .values("course__course_s_name", "if_enq__counsellor__name")
        .annotate(total_admissions=Count("id"))
    )

    # Step 3: Convert admissions data to a dictionary for quick lookups
    admissions_dict = {
        (entry["course__course_s_name"], entry["if_enq__counsellor__name"]): entry["total_admissions"]
        for entry in admissions
    }

    # Step 4: Prepare conversion data
    course_data = {}
    staff_data = {}
    data = []
    for enquiry in enquiries:
        course = enquiry["course_to_join__course_s_name"] or "not specified"  
        data.append({"enquiry":enquiry,"course":course})
        staff = enquiry["counsellor__name"]
        total_enquiries = enquiry["total_enquiries"]

        # Get admissions count for the same course and staff
        admissions = admissions_dict.get((course, staff), 0)
        conversion_rate = (admissions / total_enquiries) * 100 if total_enquiries > 0 else 0

        # Store course-wise data
        if course not in course_data:
            course_data[course] = {"total_enquiries": 0, "total_admissions": 0}
        course_data[course]["total_enquiries"] += total_enquiries
        course_data[course]["total_admissions"] += admissions

        # Store staff-wise data
        if staff not in staff_data:
            staff_data[staff] = {"total_enquiries": 0, "total_admissions": 0}
        staff_data[staff]["total_enquiries"] += total_enquiries
        staff_data[staff]["total_admissions"] += admissions

    # Compute conversion rates
    def calculate_conversion(data):
        return [
            {
                "name": key,
                "total_enquiries": value["total_enquiries"],
                "total_admissions": value["total_admissions"],
                "conversion_rate": round((value["total_admissions"] / value["total_enquiries"]) * 100, 2) if value["total_enquiries"] > 0 else 0
            }
            for key, value in data.items()
        ]

    return {
        "course_conversion": calculate_conversion(course_data),
        "staff_conversion": calculate_conversion(staff_data),
        "debug":data
    }

@format_date
def dashboard_admission_trends(start_date,end_date):
    admissions = Student.objects.filter(date_of_admission__range=(start_date, end_date))

    # Day-wise admissions
    day_wise = (
        admissions.annotate(day=TruncDay("date_of_admission"))
        .values("day")
        .annotate(total=Count("id"))
        .order_by("day")
    )

    # Week-wise admissions
    week_wise = (
        admissions.annotate(week=TruncWeek("date_of_admission"))
        .values("week")
        .annotate(total=Count("id"))
        .order_by("week")
    )

    # Month-wise admissions
    month_wise = (
        admissions.annotate(month=TruncMonth("date_of_admission"))
        .values("month")
        .annotate(total=Count("id"))
        .order_by("month")
    )

    # Year-to-Date (YTD) admissions
    current_year = datetime.now().year
    ytd_start_date = f"{current_year}-01-01"
    ytd_admissions = Student.objects.filter(date_of_admission__range=(ytd_start_date, end_date)).count()

    def format_results(data, key):
        return [{"date": entry[key].strftime("%Y-%m-%d"), "total": entry["total"]} for entry in data]

    return {
        "day_wise": format_results(day_wise, "day"),
        "week_wise": format_results(week_wise, "week"),
        "month_wise": format_results(month_wise, "month"),
        "ytd_admissions": ytd_admissions,
    }
    
    
def dashboard(request):
    date = request.GET.get("date",None)
    if not date:
        date = "ytd"
        
    data = {}
    data['trends'] = dashboard_admission_trends(date)
    data['staff'] = dashboard_staff_data(date)
    data['course'] = dashboard_course_data(date)
    data['scheme'] = dashboard_scheme_data(date)
    data['enquiry'] = dashboard_enquiry_data(date)
    if request.GET.get('api') == '1':
        return JsonResponse(data,safe=False,status=200)
    
    return render(request,'dashboard.html',{'data':data})