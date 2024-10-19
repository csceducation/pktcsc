from django.shortcuts import render, redirect
from django.views import View
from django.shortcuts import get_object_or_404
from .models import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import (
    CreateView,
    DeleteView,
    FormMixin,
    UpdateView,
)
from django import forms
from django.views.generic import DetailView, ListView, View
from .forms import CourseModelForm,CourseSubjectModelForm,CourseBookModelForm
from django.urls import reverse_lazy


class CourseListView(LoginRequiredMixin, ListView):
    model = CourseModel
    template_name = "list.html"
    def slist(request):
        template_name = "list.html"
        return render(request, template_name , context={"course":CourseModel.objects.all()})

class CourseCreateView(View):
    template_name = 'coursecreate.html'

    def get(self, request, *args, **kwargs):
        form = CourseModelForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = CourseModelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_course')
        return render(request, self.template_name, {'form': form})
    
class CourseDetailView(DetailView):
    model = CourseModel
    template_name = "course_details.html"

    def get_context_data(self, **kwargs):
        context = super(CourseDetailView, self).get_context_data(**kwargs)
        context["subject"] = CourseSubjectModel.objects.filter(course=self.object)
        context["book"] = CourseBookModel.objects.filter(course=self.object)
        context["exam"] = CourseExamModel.objects.filter(course=self.object)
        return context
    

class CourseDeleteView(LoginRequiredMixin, DeleteView):
    model = CourseModel
    success_url = reverse_lazy("list_course")

class CourseUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = CourseModel
    template_name = "coursecreate.html"
    fields = "__all__"
    success_message = "Record successfully updated."

    def get_form(self):
        """add date picker in forms"""
        form = super(CourseUpdateView, self).get_form()
        
      
        return form
    
class SubjectCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = CourseSubjectModel
    fields = '__all__'
    template_name = "course/subjectadd.html"
    def get(self, request, *args, **kwargs):
        class ClassForm(forms.ModelForm):
                class Meta:
                    model = CourseSubjectModel
                    fields = '__all__'
                sub_name = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )
        form = ClassForm()
        if "pk" in kwargs:
            form.initial['course'] = kwargs['pk']
            form.fields['course'].widget = forms.HiddenInput()
            form.fields['course'].label = ""
        return render(request, 'course/subjectadd.html', {'form': form})
    def post(self, request, *args, **kwargs):

           
            class ClassForm(forms.ModelForm):
                class Meta:
                    model = CourseSubjectModel
                    fields = '__all__'

            form = ClassForm(request.POST)
            
            if form.is_valid():
                return self.form_valid(form)
            
            return render(request, self.template_name, {'form': form})

    def form_valid(self, form):
            # Additional logic after the form is valid
            response = super().form_valid(form)
            return response
    
def delete_subject_log(request, pk,subject_name):
    enquiry_log = get_object_or_404(CourseSubjectModel, pk=pk)
    subject_to_remove = enquiry_log.sub_name.filter(name=subject_name).first()
    if subject_to_remove:
        enquiry_log.sub_name.remove(subject_to_remove)
    referring_url = request.META.get('HTTP_REFERER', '/')
    return redirect(referring_url)

class BookCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = CourseBookModel
    fields = '__all__'
    template_name = "course/bookcreate.html"
    def get(self, request, *args, **kwargs):
        class ClassForm(forms.ModelForm):
                class Meta:
                    model = CourseBookModel
                    fields = '__all__'
                book_name = forms.ModelMultipleChoiceField(
        queryset=Book.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )
        form = ClassForm()
        if "pk" in kwargs:
            form.initial['course'] = kwargs['pk']
            form.fields['course'].widget = forms.HiddenInput()
            form.fields['course'].label = ""
        return render(request, 'course/bookcreate.html', {'form': form})
    def post(self, request, *args, **kwargs):

           
            class ClassForm(forms.ModelForm):
                class Meta:
                    model = CourseBookModel
                    fields = '__all__'

            form = ClassForm(request.POST)
            
            if form.is_valid():
                return self.form_valid(form)
            
            return render(request, self.template_name, {'form': form})

    def form_valid(self, form):
            # Additional logic after the form is valid
            response = super().form_valid(form)
            return response
class ExamCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = CourseExamModel
    fields = '__all__'
    template_name = "course/examadd.html"
    def get(self, request, *args, **kwargs):
        class ExamForm(forms.ModelForm):
                class Meta:
                    model = CourseExamModel
                    fields = '__all__'
                course_exams = forms.ModelMultipleChoiceField(
        queryset=Exam.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )
        form = ExamForm()
        if "pk" in kwargs:
            form.initial['course'] = kwargs['pk']
            form.fields['course'].widget = forms.HiddenInput()
            form.fields['course'].label = ""
        return render(request, 'course/examadd.html', {'form': form})
    def post(self, request, *args, **kwargs):

           
            class ExamForm(forms.ModelForm):
                class Meta:
                    model = CourseExamModel
                    fields = '__all__'

            form = ExamForm(request.POST)
            
            if form.is_valid():
                return self.form_valid(form)
            
            return render(request, self.template_name, {'form': form})

    def form_valid(self, form):
            # Additional logic after the form is valid
            response = super().form_valid(form)
            return response
    
def delete_book_log(request, pk,book_name):
    enquiry_log = get_object_or_404(CourseBookModel, pk=pk)
    book_to_remove = enquiry_log.book_name.filter(name=book_name).first()
    if book_to_remove:
        enquiry_log.book_name.remove(book_to_remove)
    referring_url = request.META.get('HTTP_REFERER', '/')
    return redirect(referring_url)
def delete_exam_log(request, pk,exam_name):
    enquiry_log = get_object_or_404(CourseExamModel, pk=pk)
    exam_to_remove = enquiry_log.course_exams.filter(name=exam_name).first()
    if exam_to_remove:
        enquiry_log.course_exams.remove(exam_to_remove)
    referring_url = request.META.get('HTTP_REFERER', '/')
    return redirect(referring_url)