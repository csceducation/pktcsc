from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import BatchModel
from .forms import BatchModelForm,AddStudentForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django import forms
from apps.course.models import *
from apps.students.models import Classmodel
from django.utils import timezone
from apps.students.models import Student
from apps.corecode.models import Time
from apps.attendancev2.manager import AttendanceManagerV2
from csc_app.settings import db
from apps.corecode.utils import debug_info


def BatchListView(request):
    # Get the authenticated user
    user = request.user

    # Check if the user is an admin
    if user.is_superuser:
        # If user is admin, return all batches
        batches = BatchModel.objects.all()
    else:
        # For regular staff users, filter batches where staff matches the user
        batches = BatchModel.objects.filter(batch_staff=user.staff_profile)
    # Filter batches that are out of end date and still active
    current_date = timezone.now().date()
    expired_batches = batches.filter(batch_end_date__lt=current_date, batch_status="Active")
    template_name = "batch/batchlist.html"
    context = {"batches": batches,'expired_batches':expired_batches}
    
    return render(request, template_name, context)
class BatchDetailView(DetailView):
    model = BatchModel
    template_name = "batch/batchdetails.html"
    context_object_name = 'batch'
    def get_context_data(self, **kwargs):
        context = super(BatchDetailView, self).get_context_data(**kwargs)
        manager = AttendanceManagerV2(db)
        # context['finished'] = [item for sublist in finished for item in sublist]
        finished,data = manager.get_finished_topics_batch(self.object.id)
        # debug_info(data)
        context['covered'] = finished
        context['attendance_details'] = data
        finished_flat = [item for sublist in finished for item in sublist]
        contents = list(self.object.batch_course.get_day_contents().values())
        context['not_covered'] = [topic for topic in contents if topic not in finished_flat]  # Not covered topics
        # debug_info(context)
        return context
class AddStudentView(View):
    template_name = 'batch/add_student.html'
    def get(self, request, *args, **kwargs):
        batch = get_object_or_404(BatchModel, pk=kwargs['pk'])
        # student_detail = Student.objects.filter(current_status = "active")
        student_detail = Student.objects.filter(course__coursesubjectmodel__sub_name=batch.batch_course,current_status="active")
        add_student_form = AddStudentForm(instance=batch)
        context = {'batch': batch, 'add_student_form': add_student_form,'stu':student_detail}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        batch = get_object_or_404(BatchModel, pk=kwargs['pk'])
        add_student_form = AddStudentForm(request.POST, instance=batch)

        if add_student_form.is_valid():
            students = add_student_form.cleaned_data['batch_students']
            add_student_form.save()

            # Create Classmodel instance for each selected student
            for student in students:
                finished_subject = batch.batch_course.name
                start_date = batch.batch_start_date
                end_date = batch.batch_end_date
                class_time = Time.objects.get(id=batch.batch_timing.id)
                faculty = batch.batch_staff
                remark = "Student added to batch"  # You might want to customize this

                class_model_instance = Classmodel.objects.create(
                    student=student,
                    finised_subject=finished_subject,
                    start_date=start_date,
                    end_date=end_date,
                    class_time=class_time,
                    faculty=faculty,
                    remark=remark,
                )

        return redirect('batch_detail', pk=batch.id)
class BatchModelUpdateFormV2(forms.ModelForm):
    class Meta:
        model = BatchModel
        fields = "__all__"
        exclude = ['batch_students']
        widgets = {
            'batch_start_date': forms.DateInput(attrs={'type': 'date'}),
            'batch_end_date': forms.DateInput(attrs={'type': 'date'}),
            'batch_students': forms.SelectMultiple(attrs={'size': 10}),
        }
class BatchModelUpdateForm(forms.ModelForm):
    class Meta:
        model = BatchModel
        fields = "__all__"
        exclude = ['batch_students']
        widgets = {
            'batch_start_date': forms.DateInput(attrs={'type': 'date'}),
            'batch_end_date': forms.DateInput(attrs={'type': 'date'}),
            'batch_students': forms.SelectMultiple(attrs={'size': 10}),
        }
        
    def clean(self):
        cleaned_data = super().clean()
        batch_staff = cleaned_data.get('batch_staff')
        batches = BatchModel.objects.filter(batch_staff=batch_staff, batch_status="Active")
        if batches.exists():
            for batch in batches:
                if batch.batch_timing == cleaned_data.get('batch_timing'):# need not to check for date as we are checking against the active batches only
                    
                    raise forms.ValidationError("There is an error in your form")
        
        return cleaned_data
    
class BatchCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = BatchModel
    form_class = BatchModelUpdateForm
    template_name = "batch/batchform.html"
    success_message = "Record successfully Created."
    def get_auto_id(self):
        # Customize this method to generate the auto-incremented ID with date and time
        current_datetime = timezone.now()
        formatted_datetime = current_datetime.strftime("%M%S")
        
        # Combine the formatted date and time to create the ID
        return f"{formatted_datetime}"
    def get(self, request, *args, **kwargs):
        form = BatchModelUpdateForm()
        form.fields['batch_id'].initial = self.get_auto_id()  # Replace generate_auto_id() with your logic

        subjects = Subject.objects.all()
        end_dates = {}
        for subject in subjects:
            end_dates[subject.id] = subject.calculate_duration()
        extra = {
            "subject_end_date":end_dates
        }
        
        return render(request, 'batch/batchform.html', {'form': form,**extra})
    def post(self, request, *args, **kwargs):

            form = BatchModelUpdateForm(request.POST)
            
            if form.is_valid():
                return self.form_valid(form)
            else: 
                return self.form_invalid(form)
            return render(request, self.template_name, {'form': form})

    def form_valid(self, form):
            
            response = super().form_valid(form)
            return response
    def form_invalid(self, form):
        # Custom error handling
        self.object = None
        form.add_error('batch_timing', 'Staff is already assigned to an active batch on the same time.')
        # You can also add specific errors to a specific field
        # form.add_error('fieldname', 'Custom error message')
        return super().form_invalid(form)
    
class BatchUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = BatchModel
    form_class = BatchModelUpdateFormV2
    template_name = "batch/batchform.html"
    success_message = "Record successfully updated."
    def form_valid(self, form):
        # Update the BatchModel instance
        response = super().form_valid(form)



        # # Update the end_date in associated Classmodel instances
        # new_end_date = form.cleaned_data['batch_end_date']
        # for student in self.object.batch_students.all():
        #     classmodel_instance = Classmodel.objects.get(student=student)
        #     classmodel_instance.end_date = new_end_date
        #     classmodel_instance.save()
        
        return response



    
    def get_success_url(self):
        return reverse_lazy('batch_detail', kwargs={'pk': self.object.pk})

class BatchDeleteView(LoginRequiredMixin, DeleteView):
    model = BatchModel
    success_url = reverse_lazy("batch_list")

def delete_batchstudent_log(request, pk, id):
    enquiry_log = get_object_or_404(BatchModel, pk=pk)
    subject_to_remove = enquiry_log.batch_students.filter(id=id).first()

    # Delete associated Classmodel instances for each selected student
    class_model_instances = Classmodel.objects.filter(student=subject_to_remove)
    class_model_instances.delete()

    if subject_to_remove:
        enquiry_log.batch_students.remove(subject_to_remove)

    referring_url = request.META.get('HTTP_REFERER', '/')
    return redirect(referring_url)


