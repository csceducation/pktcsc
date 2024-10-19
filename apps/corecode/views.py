from django.contrib import messages
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
    TimeForm
    
)
from .models import (
    AcademicSession,
    AcademicTerm,
    SiteConfig,
    StudentClass,
    Subject,
    Book,Exam,Time,Bill
)
from apps.revenue.models import GST

#---dashboard--
from django.utils import timezone
from apps.students.models import Student
from apps.finance.models import Invoice
from apps.enquiry.models import Enquiry
from apps.batch.models import BatchModel
from django.db.models import Sum,Count 
import datetime

def get_month_start_end(date=None):
    """Gets the start and end date of the month for the given date. 
    If no date is given, it defaults to today.
    """
    if date is None:
        date = datetime.date.today()

    # Get the first day of the month
    start_date = datetime.date(date.year, date.month, 1)

    # Get the last day of the month
    next_month = date.replace(day=28) + datetime.timedelta(days=4)  # Go to next month
    end_date = next_month - datetime.timedelta(days=next_month.day)

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
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        today = timezone.now().strftime('%Y-%m-%d')
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
            
            context = {
                'dashboard':True,
                'total_invoices':total_admissions,
                'total_invoice_amount': total_invoice_amount,
                'total_collected_amount': total_collected_amount,
                'average_per_admission': round(avg_invoice_amount,2),
                'cr_percent':cr_percent,
                'course_admissions': course_admissions,
                'students':students,
                'enquiry_data':enquiry_data,
                'batch_data':batch_data
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
    fields = ["time"]
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
    fields = ["name","exam_mode","exam_duration"]
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
    context_object_name = 'bill'

    def get_object(self):
        return Bill.objects.first()
    
    def get_context_data(self, **kwargs):
        # Get the existing context
        context = super().get_context_data(**kwargs)
        
        # Add another object, e.g., Customer, to the context
        context['gst'] = GST.objects.first()  # Example of returning another object
        return context

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