import csv
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import widgets
from django.http import HttpResponse ,Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, View
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from .forms import EnquiryForm, LogForm , StudentEnquiryForm
from .models import Enquiry, Enquirylogs , StudentEnquiryModel

def enquiry_index(request):
    return render(request,"index_enquiry.html")

class EnquiryListView(LoginRequiredMixin, ListView):
    model = Enquiry
    
    def slist(request):
        template_name = "enquiry.html"
        return render(request, template_name , context={"Enquiry":Enquiry.objects.all()})



class EnquiryDetailView(LoginRequiredMixin, DetailView):
    model = Enquiry
    template_name = "enquiry_details.html"

    def get_context_data(self, **kwargs):
        context = super(EnquiryDetailView, self).get_context_data(**kwargs)
        context["history"] = Enquirylogs.objects.filter(student=self.object)
        return context


class EnquiryCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Enquiry
    template_name = "enquiry_form.html"
    form_class = EnquiryForm
    success_message = "New Enquiry successfully added."

    def get_form(self, *args, **kwargs):
        form = super(EnquiryCreateView, self).get_form(*args, **kwargs)
        # Customize widget for the date field
        form.fields["enquiry_date"].widget = widgets.DateInput(attrs={"type": "date"})
        form.fields["date_of_birth"].widget = widgets.DateInput(attrs={"type": "date"})
        form.fields["expected_date"].widget = widgets.DateInput(attrs={"type": "date"})
        
        # Customize widget for the address field
        form.fields["qualification"].widget = widgets.Textarea(attrs={"rows": 1,"cols":25})
        form.fields["studying_course"].widget = widgets.Textarea(attrs={"rows": 1,"cols":25})
        form.fields["counsellor_remark"].widget = widgets.Textarea(attrs={"rows": 1,"cols":25})
        return form



class EnquiryUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Enquiry
    success_message = "Record successfully updated."
    form_class = EnquiryForm
    template_name = "enquiry_form.html"

    def get_form(self, *args, **kwargs):
        form = super(EnquiryUpdateView, self).get_form(*args, **kwargs)
        
        # Customize widget for the date field
        form.fields["enquiry_date"].widget = widgets.DateInput(attrs={"type": "date"})
        form.fields["date_of_birth"].widget = widgets.DateInput(attrs={"type": "date"})
        form.fields["expected_date"].widget = widgets.DateInput(attrs={"type": "date"})
        
        # Customize widget for the address field
        form.fields["address"].widget = widgets.Textarea(attrs={"rows": 1,"cols":25})
        form.fields["qualification"].widget = widgets.Textarea(attrs={"rows": 1,"cols":25})
        form.fields["studying_course"].widget = widgets.Textarea(attrs={"rows": 1,"cols":25})
        form.fields["counsellor_remark"].widget = widgets.Textarea(attrs={"rows": 1,"cols":25})
        return form



class EnquiryDeleteView(LoginRequiredMixin, DeleteView):
    model = Enquiry
    success_url = reverse_lazy("enquiry-list")
    template_name="del_confirm.html"


class DownloadCSVViewdownloadcsv(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="enquiry_template.csv"'

        writer = csv.writer(response)
        writer.writerow(
            [
                "enquiry_no",
                "name",
                "gender",
                "mobile_number",
                "address",
                "enquiry_statuss",
            ]
        )

        return response


class LogCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Enquirylogs
    template_name = "history.html"
    form_class = LogForm
    success_message = "Log added."

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        # Get the student ID from the URL parameter
        kwargs['initial'] = {'student': self.kwargs['pk']}

        return kwargs

    def get_success_url(self):
        # Redirect to the absolute URL of the related Enquiry instance
        return reverse_lazy('enquiry-detail', kwargs={'pk': self.object.student.pk})

def delete_enquiry_log(request, pk):
    enquiry_log = get_object_or_404(Enquirylogs, pk=pk)
    enquiry_log.delete()
    referring_url = request.META.get('HTTP_REFERER', '/')
    return redirect(referring_url) 

class StudentEnquiryListView(LoginRequiredMixin, ListView):
    model = StudentEnquiryModel
    
    def slist(request):
        template_name = "pending_enquiry_list.html"
        return render(request, template_name , context={"Enquiry":StudentEnquiryModel.objects.all()})
    
class StudentEnquiryUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = StudentEnquiryModel
    success_message = "Record successfully updated."
    form_class = StudentEnquiryForm
    template_name = "pending_form_view.html"

    def get_form(self, *args, **kwargs):
        form = super(StudentEnquiryUpdateView, self).get_form(*args, **kwargs)
        
        # Customize widget for the date field
        form.fields["enquiry_date"].widget = widgets.DateInput(attrs={"type": "date"})
        form.fields["date_of_birth"].widget = widgets.DateInput(attrs={"type": "date"})
        
        # Customize widget for the address field
        form.fields["address"].widget = widgets.Textarea(attrs={"rows": 1,"cols":25})
        form.fields["qualification"].widget = widgets.Textarea(attrs={"rows": 1,"cols":25})
        form.fields["studying_course"].widget = widgets.Textarea(attrs={"rows": 1,"cols":25})
        
        return form
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pk'] = self.object.pk
        return context
    
class StudentEnquiryDeleteView(LoginRequiredMixin, DeleteView):
    model = StudentEnquiryModel
    success_url = reverse_lazy("pending-enquiry-list")
    template_name="del_confirm.html"

class StudentEnquiryCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Enquiry
    template_name = "enquiry_form.html"
    form_class = EnquiryForm
    success_message = "Your Form was Submitted successfully added."
    def get_form(self, *args, **kwargs):
        form = super(StudentEnquiryCreateView, self).get_form(*args, **kwargs)
        
        # Customize widget for the date field
        form.fields["enquiry_date"].widget = widgets.DateInput(attrs={"type": "date"})
        form.fields["date_of_birth"].widget = widgets.DateInput(attrs={"type": "date"})
        form.fields["expected_date"].widget = widgets.DateInput(attrs={"type": "date"})
        
        # Customize widget for the address field
        form.fields["qualification"].widget = widgets.Textarea(attrs={"rows": 1,"cols":25})
        form.fields["studying_course"].widget = widgets.Textarea(attrs={"rows": 1,"cols":25})
        form.fields["counsellor_remark"].widget = widgets.Textarea(attrs={"rows": 1,"cols":25})
        return form
    def get(self, request, *args, **kwargs):
        # Stage 1: Select Enquiry
        enquiry_id = kwargs['enquiry_id']
        enquiry = StudentEnquiryModel.objects.get(auto_increment=enquiry_id)
        form = EnquiryForm()
        try:
            # If enquiry_id is provided, fetch the Enquiry instance
            if enquiry_id:
                enquiry_instance = StudentEnquiryModel.objects.get(pk=enquiry_id)
                
                # Pre-fill the form fields based on the Enquiry instance
                form.initial['name'] = enquiry_instance.name
                form.initial['f_name'] = enquiry_instance.f_name
                form.initial['m_name'] = enquiry_instance.m_name
                form.initial['date_of_birth'] = enquiry_instance.date_of_birth
                form.initial['address'] = enquiry_instance.address
                form.initial['address1'] = enquiry_instance.address1
                form.initial['address2'] = enquiry_instance.address2
                form.initial['date_of_birth'] = enquiry_instance.date_of_birth
                form.initial['occupation'] = enquiry_instance.student_role
                form.initial['mobile_number'] = enquiry_instance.mobile_number
                form.initial['email'] = enquiry_instance.email
                form.initial['taluka'] = enquiry_instance.taluka
                form.initial['district'] = enquiry_instance.district
                form.initial['pincode'] = enquiry_instance.pincode
                form.initial['gender'] = enquiry_instance.gender
                form.initial['qualification'] = enquiry_instance.qualification
                form.initial['qualification_status'] = enquiry_instance.qualification_status
                form.initial['studying_year'] = enquiry_instance.studying_year
                form.initial['studying_course'] = enquiry_instance.studying_course
                form.initial['need_of_study'] = enquiry_instance.need_of_study 
                form.initial['known_csc'] = enquiry_instance.known_csc  
                form.initial['course_to_join'] = enquiry_instance.course_to_join  
                form.initial['new_course'] = enquiry_instance.new_course
                form.initial['time_to_study'] = [t.id for t in enquiry.time_to_study.all()]
        except Enquiry.DoesNotExist:
                raise Http404("Enquiry does not exist")
        return render(request, 'enquiry_form.html', {'form': form, 'enquiry_id': enquiry_id, 'enquiry': enquiry})


class StudentEnquiryFormCreateView(SuccessMessageMixin, CreateView):
    model = StudentEnquiryModel
    template_name = "student_enquiry_form.html"
    form_class = StudentEnquiryForm
    success_message = "New Enquiry successfully added."

    def get_form(self, *args, **kwargs):
        form = super(StudentEnquiryFormCreateView, self).get_form(*args, **kwargs)
        form.fields['verfied'].widget = forms.HiddenInput()
        form.fields['verfied'].label = ""
        # Customize widget for the date field
        form.fields["enquiry_date"].widget = widgets.DateInput(attrs={"type": "date"})
        form.fields["date_of_birth"].widget = widgets.DateInput(attrs={"type": "date"})
        
        # Customize widget for the address field
        form.fields["qualification"].widget = widgets.Textarea(attrs={"rows": 1,"cols":25})
        form.fields["studying_course"].widget = widgets.Textarea(attrs={"rows": 1,"cols":25})
        return form
    def get_success_url(self):
        return "https://csceducation.net"