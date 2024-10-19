import csv
from django.core.exceptions import ValidationError
from django.contrib.auth.mixins import AccessMixin
from datetime import datetime
from django import forms
from django.http import HttpResponse
from PIL import Image
import qrcode
import os
from csc_app import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import widgets
from django.http import HttpResponse,Http404
from django.shortcuts import redirect, render,get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, View
from django.views.generic.edit import FormMixin, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import (
    CreateView,
    DeleteView,
    FormMixin,
    UpdateView,
)
import qrcode
import datetime
from PIL import Image, ImageDraw, ImageFont
import os
from ..finance.models import Invoice,InvoiceItem
from django.views.generic import DetailView
from apps.finance.models import Invoice,Due
from ..enquiry.models import *
from .models import Student, StudentBulkUpload,Bookmodel,Classmodel,Exammodel,Certificatemodel
from django.utils.decorators import method_decorator
from apps.corecode.views import student_entry_resricted,staff_student_entry_restricted,different_user_restricted
from django.contrib.auth.decorators import login_required
from apps.batch.models import BatchModel
from apps.attendancev2.dashboard import DashboardManager
from apps.attendancev2.manager import AttendanceManager
from django.core.serializers import serialize
from csc_app.settings import db
from apps.corecode.models import User

def generate_student_id_card(request,student_id):
        # Create a blank image
    image = Image.new('RGB', (1000, 900), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    student = Student.objects.get(id=student_id)
    

# Get the path of the system font

    font_path = os.path.join(settings.BASE_DIR, 'static/dist/css/arial.ttf')
    # Use the system font for ImageFont
    font = ImageFont.truetype(font_path, size=45)


    d_date = datetime.datetime.now()
    reg_format_date = d_date.strftime("  %d-%m-%Y\t\t\t\t\t ID CARD Generator\t\t\t\t\t  %I:%M:%S %p")

    # Company Name
    text_color = 'rgb(255, 255, 0)'  # yellow color
    background_color = 'rgb(255, 0, 0)'  # red color
    draw.rectangle([(0, 0), (1000, 150)], fill='red')
    (x, y) = (300, 50)
    logo_path = os.path.join(settings.BASE_DIR, "static/dist/img/logoid.jpg")
    logo = Image.open(logo_path)
    logo = logo.resize((150, 120))  # Resize the logo as needed
    image.paste(logo, (100, 25))  # Paste the logo at the desired location
    company = "Pudukkottai   CSC"
    color = 'rgb(0, 0, 0)' # black color
    draw.text((x, y), company, fill=text_color, font=font)

    # ID Number
    (x, y) = (50, 200)
    idno = student.enrol_no
    message = str('Roll Number: ' + str(idno))
    draw.text((x, y), message, fill=color, font=font)

    # Name
    (x, y) = (50, 300)
    name = student.student_name
    fname = str('Name: ' + str(name))
    draw.text((x, y), fname, fill=color, font=font)

    (x, y) = (50, 400)
    name = student.course
    fname = str('Course: ' + str(name))
    draw.text((x, y), fname, fill=color, font=font)

    # Gender
    (x, y) = (50, 500)
    gender = student.gender
    fgender = str('Gender: ' + str(gender))
    draw.text((x, y), fgender, fill=color, font=font)

    # DOB
    (x, y) = (50, 600)
    dob = student.date_of_birth
    fdob = str('Date of Birth: ' + str(dob))
    draw.text((x, y), fdob, fill=color, font=font)

    # Blood Group

    # Mobile Number
    (x, y) = (50, 700)
    mobile_number = student.mobile_number
    fmobile_number = str('Mobile Number: ' + str(mobile_number))
    draw.text((x, y), fmobile_number, fill=color, font=font)


    # Save the edited image
    image_path = os.path.join(settings.BASE_DIR, "media/idcards", f"student_id_card_{student_id}.png")
    image.save(image_path)

    # Generate QR code
    public_student_profile_url = reverse('public_student_profile', args=[student.id])
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(request.get_host() + public_student_profile_url)
    qr.make(fit=True)
    qr_image = qr.make_image(fill_color="black", back_color="white")

    qr_path = os.path.join('media/qrcodes', f'qr_code{student_id}.png')
    qr_image.save(qr_path)

    # Paste QR code onto the ID card
    if student.passport.path:
        student_photo = Image.open(student.passport.path)
    id_card = Image.open(image_path)
    qr_code = Image.open(qr_path)
    student_photo = student_photo.resize((320, 200))
    qr_code = qr_code.resize((320, 400))
    id_card.paste(student_photo,(650,200))
    id_card.paste(qr_code, (650, id_card.height // 2))
    id_card.save(image_path)

    # Serve the image as a downloadable file
    with open(image_path, 'rb') as file:
        response = HttpResponse(file.read(), content_type='image/png')
        response['Content-Disposition'] = 'attachment; filename=student_id_card.png'
    return response
def handler404(request, exception):
    return render(request, '404.html', status=404)

@method_decorator(student_entry_resricted(),name='dispatch')
class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    
    def slist(request):
        template_name = "students/student_list.html"
        return render(request, template_name , context={"students":Student.objects.all()})

def select_enquiry(request):
    enquiries = Enquiry.objects.filter(enquiry_status = "Following")
    if request.method == 'POST':
        selected_enquiry_id = request.POST.get('enquiry')
        # Redirect to the next page with the selected Enquiry ID
        return redirect('student-create', enquiry_id=selected_enquiry_id)

    return render(request, 'students/ad_con.html', {'enquiries': enquiries})


@method_decorator(student_entry_resricted(),name='dispatch')
class StudentDetailView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = "students/student_detail.html"

    def get_context_data(self, **kwargs):
        context = super(StudentDetailView, self).get_context_data(**kwargs)
        context['invoice'] = Invoice.objects.filter(student__id = self.object.id).first()
        context["payments"] = Invoice.objects.filter(student=self.object)
        context["booklog"] = Bookmodel.objects.filter(student=self.object)
        context["classlog"] = Classmodel.objects.filter(student=self.object)
        context["examlog"] = Exammodel.objects.filter(student=self.object)
        context["certilog"] = Certificatemodel.objects.filter(student=self.object)
        context['dues'] = Due.objects.all()
        return context

@method_decorator(student_entry_resricted(),name='dispatch')
class StudentCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Student
    fields = "__all__"
    success_message = "New student successfully added."
    def automatic_ro(self):
            id = Student.objects.count()
            year = str(datetime.datetime.now().year)[-2:]  # Last two digits of the current year
            month = str(datetime.datetime.now().month).zfill(2)  # Month with leading zero if needed
            object_id = str(id).zfill(4)  # Object ID with leading zeros if needed
            return f'{year}{month}{object_id}'
    def get(self, request, *args, **kwargs):
        # Stage 1: Select Enquiry
        if 'enquiry_id' not in kwargs:
            enquiries = Enquiry.objects.all()
            
            return render(request, 'students/ad_con.html', {'enquiries': enquiries})

        # Stage 2: Add Student Information
        enquiry_id = kwargs['enquiry_id']
        enquiry = Enquiry.objects.get(auto_increment=enquiry_id)
       
        
        

        # Create a dynamic ModelForm for the Student model
        class StudentForm(forms.ModelForm):
            
            class Meta:
                model = Student
                fields = '__all__'
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    # Make the 'enquiry_id' field readonly
                    
           
                                


        form = StudentForm()
        for field_name, field in form.fields.items():
                        if field.required:
                            form.fields[field_name].label = f"{field.label} *"
        form.initial['if_enq'] = enquiry_id
        form.fields['if_enq'].widget = forms.HiddenInput()
        form.fields['if_enq'].label = ""
        enquiry_id = enquiry_id  # self.kwargs.get('if_enq')
        del form.fields["user"]
        #form.fields['username'].widget.attrs['readonly'] = True
        #form.fields['password'].widget.attrs['readonly'] = True
        # if self.request.user.is_staff and not self.request.user.is_superuser:
        #     del form.fields["username"]
        #     del form.fields["password"]
        del form.fields["username"]
        del form.fields["password"]
        try:
            # If enquiry_id is provided, fetch the Enquiry instance
            if enquiry_id:
                enquiry_instance = Enquiry.objects.get(pk=enquiry_id)
                
                # Pre-fill the form fields based on the Enquiry instance
                form.initial['student_name'] = enquiry_instance.name
                form.initial['enrol_no'] = self.automatic_ro()
                form.initial['username'] = self.automatic_ro()
                form.initial['password'] = enquiry_instance.formatted_date_of_birth()
                form.initial['date_of_birth'] = enquiry_instance.date_of_birth
                form.initial['address'] = enquiry_instance.address
                form.initial['address1'] = enquiry_instance.address1
                form.initial['address2'] = enquiry_instance.address2
                form.initial['rel_name'] = enquiry_instance.f_name
                form.initial['m_name'] = enquiry_instance.m_name
                form.initial['date_of_birth'] = enquiry_instance.date_of_birth
                form.initial['age'] = enquiry_instance.age
                form.initial['gender'] = enquiry_instance.gender
                form.initial['occupation'] = enquiry_instance.student_role
                form.initial['mobile_number'] = enquiry_instance.mobile_number
                form.initial['email'] = enquiry_instance.email
                form.initial['taluka'] = enquiry_instance.taluka
                form.initial['district'] = enquiry_instance.district
                form.initial['pincode'] = enquiry_instance.pincode
                form.initial['course'] = enquiry_instance.course_to_join
                form.initial['class_time'] = [t.id for t in enquiry_instance.time_to_study.all()]
                

        except Enquiry.DoesNotExist:
            raise Http404("Enquiry does not exist")

       
        return render(request, 'students/student_form.html', {'form': form, 'enquiry_id': enquiry_id, 'enquiry': enquiry})

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        del form.fields['user']
        
        # Retrieve the enquiry_id from the URL parameters
        # Add date pickers and customize widgets
        form.fields["date_of_birth"].widget = widgets.DateInput(attrs={"type": "date"})
        form.fields["date_of_admission"].widget = widgets.DateInput(attrs={"type": "date"})
        form.fields["address"].widget = widgets.Textarea(attrs={"rows": 2})

        return form
    
    def post(self, request, *args, **kwargs):
            # Stage 2: Add Student Information
            enquiry_id = kwargs['enquiry_id']
            enquiry = Enquiry.objects.get(auto_increment=enquiry_id)
            self.usefrfollow =enquiry_id

            # Create a dynamic ModelForm for the Student model
            class StudentForm(forms.ModelForm):
                class Meta:
                    model = Student
                    fields = '__all__'
                    
                def clean_username(self):
                    username = self.cleaned_data.get('username')
                    if User.objects.filter(username=username).exists():
                        raise ValidationError("Username already exists.")
                    return username

            form = StudentForm(request.POST,request.FILES)
            del form.fields['user']
            if form.is_valid():
                if 'passport' in request.FILES:
                    form.cleaned_data['passport'] = request.FILES['passport']
                return self.form_valid(form)
            


            return render(request, 'students/student_form.html', {'form': form, 'enquiry_id': enquiry_id, 'enquiry': enquiry})

    def form_valid(self, form):
        
            username = form.cleaned_data.get('username')
            if User.objects.filter(username=username).exists():
                form.add_error('username', "Username already exists.")
                return self.form_invalid(form)
            # Additional logic after the form is valid
            response = super().form_valid(form)
            total_fee = form.cleaned_data.get('total_fee', 0)
            invoice = Invoice.objects.create(
            student=self.object, 
            status = "Active",)
            invoice_create = InvoiceItem.objects.create(
            invoice = invoice,
            description = "Total Fee",
            amount = total_fee
            )
            objectcha = Enquiry.objects.filter(auto_increment=self.usefrfollow)
            for object1 in objectcha:
                object1.enquiry_status = "Admitted"
                object1.save()
            return response
        
    def form_invalid(self, form):
        # Remove the 'username' field from the form if needed
        del form.fields['user']
        
        # Render the form with errors
        return self.render_to_response(self.get_context_data(form=form))

    
def Studentdashboard(request):
    return render(request,"students/student_dashboard.html")


@method_decorator(student_entry_resricted(),name='dispatch')
class StudentUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Student
    fields = "__all__"
    success_message = "Record successfully updated."

    def get_form(self):
        """add date picker in forms"""
        form = super(StudentUpdateView, self).get_form()
        del form.fields["user"]
        del form.fields["username"]
        del form.fields["password"]
        # form.fields['username'].widget.attrs['readonly'] = True
        # form.fields['password'].widget.attrs['readonly'] = True
        # if self.request.user.is_staff and not self.request.user.is_superuser:
            # del form.fields["username"]
            # del form.fields["password"]
        form.fields["date_of_birth"].widget = widgets.DateInput(attrs={"type": "date"})
        form.fields["date_of_admission"].widget = widgets.DateInput(
            attrs={"type": "date"}
        )
        form.fields["address"].widget = widgets.Textarea(attrs={"rows": 2})
        del form.fields['total_fee']
        return form

@method_decorator(staff_student_entry_restricted(),name='dispatch')
class StudentDeleteView(LoginRequiredMixin, DeleteView):
    model = Student
    success_url = reverse_lazy("student-list")


class StudentBulkUploadView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = StudentBulkUpload
    template_name = "students/students_upload.html"
    fields = ["csv_file"]
    success_url = "/student/list"
    success_message = "Successfully uploaded students"


class DownloadCSVViewdownloadcsv(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="student_template.csv"'

        writer = csv.writer(response)
        writer.writerow(
            [
                "registration_number",
                "surname",
                "firstname",
                "other_names",
                "gender",
                "parent_number",
                "address",
                "current_class",
            ]
        )

        return response

class CreateBooklLog(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Bookmodel
    fields = '__all__'
    template_name = "books/add_logs.html"
    def get(self, request, *args, **kwargs):
        class BookForm(forms.ModelForm):
                class Meta:
                    model = Bookmodel
                    fields = '__all__'
        form = BookForm()
        if "pk" in kwargs:
            form.initial['student'] = kwargs['pk']
            form.fields['student'].widget = forms.HiddenInput()
            form.fields['student'].label = ""
            form.fields["received_date"].widget = widgets.DateInput(attrs={"type": "date"})
            
        return render(request, 'books/add_logs.html', {'form': form})
    def post(self, request, *args, **kwargs):

            # Create a dynamic ModelForm for the Student model
            class BookForm(forms.ModelForm):
                class Meta:
                    model = Bookmodel
                    fields = '__all__'

            form = BookForm(request.POST)
            
            if form.is_valid():
                return self.form_valid(form)
            
            return render(request, self.template_name, {'form': form})

    def form_valid(self, form):
            # Additional logic after the form is valid
            response = super().form_valid(form)
            return response
class CreateClasslLog(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Classmodel
    fields = '__all__'
    template_name = "classes/add_class.html"
    def get(self, request, *args, **kwargs):
        class ClassForm(forms.ModelForm):
                class Meta:
                    model = Classmodel
                    fields = '__all__'
        form = ClassForm()
        if "pk" in kwargs:
            form.initial['student'] = kwargs['pk']
            form.fields['student'].widget = forms.HiddenInput()
            form.fields['student'].label = ""
            form.fields["start_date"].widget = widgets.DateInput(attrs={"type": "date"})
            form.fields["end_date"].widget = widgets.DateInput(attrs={"type": "date"})
            
        return render(request, 'classes/add_class.html', {'form': form})
    def post(self, request, *args, **kwargs):

           
            class ClassForm(forms.ModelForm):
                class Meta:
                    model = Classmodel
                    fields = '__all__'

            form = ClassForm(request.POST)
            
            if form.is_valid():
                return self.form_valid(form)
            
            return render(request, self.template_name, {'form': form})

    def form_valid(self, form):
            # Additional logic after the form is valid
            response = super().form_valid(form)
            return response
class CreateClasslLog(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Classmodel
    fields = '__all__'
    template_name = "classes/add_class.html"
    def get(self, request, *args, **kwargs):
        class ClassForm(forms.ModelForm):
                class Meta:
                    model = Classmodel
                    fields = '__all__'
        form = ClassForm()
        if "pk" in kwargs:
            form.initial['student'] = kwargs['pk']
            form.fields['student'].widget = forms.HiddenInput()
            form.fields['student'].label = ""
            form.fields["start_date"].widget = widgets.DateInput(attrs={"type": "date"})
            form.fields["end_date"].widget = widgets.DateInput(attrs={"type": "date"})
            
        return render(request, 'classes/add_class.html', {'form': form})
    def post(self, request, *args, **kwargs):

           
            class ClassForm(forms.ModelForm):
                class Meta:
                    model = Classmodel
                    fields = '__all__'

            form = ClassForm(request.POST)
            
            if form.is_valid():
                return self.form_valid(form)
            
            return render(request, self.template_name, {'form': form})

    def form_valid(self, form):
            # Additional logic after the form is valid
            response = super().form_valid(form)
            return response
class CreateExamLog(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Exammodel
    fields = '__all__'
    template_name = "classes/exam.html"
    def get(self, request, *args, **kwargs):
        class ExamForm(forms.ModelForm):
                class Meta:
                    model = Exammodel
                    fields = '__all__'
        form = ExamForm()
        if "pk" in kwargs:
            form.initial['student'] = kwargs['pk']
            form.fields['student'].widget = forms.HiddenInput()
            form.fields['student'].label = ""
            form.fields["exam_date"].widget = widgets.DateInput(attrs={"type": "date"})
            
        return render(request, 'classes/exam.html', {'form': form})
    def post(self, request, *args, **kwargs):

           
            class ExamForm(forms.ModelForm):
                class Meta:
                    model = Exammodel
                    fields = '__all__'

            form = ExamForm(request.POST)
            
            if form.is_valid():
                return self.form_valid(form)
            
            return render(request, self.template_name, {'form': form})

    def form_valid(self, form):
            # Additional logic after the form is valid
            response = super().form_valid(form)
            return response
class CreateCertificateLog(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Certificatemodel
    fields = '__all__'
    template_name = "classes/certificate.html"
    def get(self, request, *args, **kwargs):
        class CertificateForm(forms.ModelForm):
                class Meta:
                    model = Certificatemodel
                    fields = '__all__'
        form = CertificateForm()
        if "pk" in kwargs:
            form.initial['student'] = kwargs['pk']
            form.fields['student'].widget = forms.HiddenInput()
            form.fields['student'].label = ""
            form.fields["date_of_complete"].widget = widgets.DateInput(attrs={"type": "date"})
            form.fields["certificate_date"].widget = widgets.DateInput(attrs={"type": "date"})
            form.fields["certificate_issued_date"].widget = widgets.DateInput(attrs={"type": "date"})
            
        return render(request, 'classes/certificate.html', {'form': form})
    def post(self, request, *args, **kwargs):

           
            class CertificateForm(forms.ModelForm):
                class Meta:
                    model = Certificatemodel
                    fields = '__all__'

            form = CertificateForm(request.POST)
            
            if form.is_valid():
                return self.form_valid(form)
            
            return render(request, self.template_name, {'form': form})

    def form_valid(self, form):
            # Additional logic after the form is valid
            response = super().form_valid(form)
            return response
def delete_book_log(request, pk):
    enquiry_log = get_object_or_404(Bookmodel, pk=pk)
    enquiry_log.delete()
    referring_url = request.META.get('HTTP_REFERER', '/')
    return redirect(referring_url) 
def delete_class_log(request, pk):
    enquiry_log = get_object_or_404(Classmodel, pk=pk)
    enquiry_log.delete()
    referring_url = request.META.get('HTTP_REFERER', '/')
    return redirect(referring_url) 
def delete_exam_log(request, pk):
    enquiry_log = get_object_or_404(Exammodel, pk=pk)
    enquiry_log.delete()
    referring_url = request.META.get('HTTP_REFERER', '/')
    return redirect(referring_url) 
def delete_certificate_log(request, pk):
    enquiry_log = get_object_or_404(Certificatemodel, pk=pk)
    enquiry_log.delete()
    referring_url = request.META.get('HTTP_REFERER', '/')
    return redirect(referring_url) 
class PublicAccessMixin(AccessMixin):
    def handle_no_permission(self):
        return super().handle_no_permission()

@method_decorator(login_required(),name='dispatch')
class PublicView(PublicAccessMixin,DetailView):
    model = Student
    template_name = "public/indexs.html"
    login_url = None
    def get_context_data(self, **kwargs):
        context = super(PublicView, self).get_context_data(**kwargs)
        context["payments"] = Invoice.objects.filter(student=self.object)
        context["booklog"] = Bookmodel.objects.filter(student=self.object)
        context["classlog"] = Classmodel.objects.filter(student=self.object)
        context["examlog"] = Exammodel.objects.filter(student=self.object)
        context["certilog"] = Certificatemodel.objects.filter(student=self.object)
        context["dues"] = Due.objects.filter(invoice__student=self.object)
        return context
    
    
def attendance_test(request,**kwargs):
    student_id = kwargs.get('pk')
    student = Student.objects.get(id=student_id)
    batches = BatchModel.objects.filter(batch_students__id=student.id)
    manager = DashboardManager(db)
    lab_manager = AttendanceManager(db)
    lab_data = lab_manager.get_public_student_lab_data(student.enrol_no)
    data = {}
    for batch in batches:
        x = manager.get_public_attendance(student.enrol_no,batch.id)
        x.append(batch.batch_staff.username)
        data[str(batch.batch_course)+"("+str(batch.batch_id)+")"] = x
    #print(data)
    
    return render(request, 'public/student_attendance.html', {'data':data,'object':student,"lab_data":lab_data})