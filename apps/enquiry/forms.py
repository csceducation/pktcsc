from django import forms
from django.core.exceptions import ValidationError
from django.forms import widgets
from apps.corecode.models import Time

from .models import Enquiry, Enquirylogs ,StudentEnquiryModel


class EnquiryForm(forms.ModelForm):
    class Meta:
        model = Enquiry
        fields = '__all__'  # Use all fields from the model

    def __init__(self, *args, **kwargs):
        super(EnquiryForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.required:
                self.fields[field_name].label = f"{field.label} *"
        self.fields["enquiry_date"].widget = widgets.DateInput(attrs={"type": "date"})
        self.fields["date_of_birth"].widget = widgets.DateInput(attrs={"type": "date"})
        self.fields["expected_date"].widget = widgets.DateInput(attrs={"type": "date"})
        self.fields["time_to_study"] = forms.ModelMultipleChoiceField(
        queryset=Time.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True  
    )
        # Customize widget for the address field
        self.fields["qualification"].widget = widgets.Textarea(attrs={"rows": 1,"cols":25})
        self.fields["studying_course"].widget = widgets.Textarea(attrs={"rows": 1,"cols":25})
        self.fields["counsellor_remark"].widget = widgets.Textarea(attrs={"rows": 1,"cols":25})
        self.fields["student_company_name"].required = False
        self.fields["expected_date"].required = False
        self.fields["studying_course"].required = False
        for field_name, field in self.fields.items():
            field.widget.attrs["autocomplete"] = "off"
        optional_fields = [
            "student_company_name",
            "counsellor_remark",
            "studying_course",
            "studying_year",
        
            # Add more fields as needed
        ]
        for field_name in optional_fields:
            self.fields[field_name].required = False
        # Group fields into sections
        personal_info_fields = ['name', 'f_name','m_name','address','address1','address2','taluka', 'district','pincode', 'mobile_number', 'email','date_of_birth','student_role', 'student_company_name','gender']
        office_use_fields = ['enquiry_date','counsellor', 'counsellor_remark', 'enquiry_status','expected_date']
        qualification_fiedls = ['qualification', 'qualification_status', 'studying_year', 'studying_course','student_college_name']
        others_fields = [
            
             'need_of_study', 'course_to_join','new_course', 'time_to_study', 'known_csc'
        ]

        # Set fieldsets for sections
        self.fieldsets = {
            'personal_info': personal_info_fields,
            'office_use': office_use_fields,
            'qualification_use' :qualification_fiedls,
            'others': others_fields,
        }

    def fieldsets_as_dict(self):
        # Convert fieldsets to a dictionary for use in templates
        return {key: [self[field] for field in fields] for key, fields in self.fieldsets.items()}


 # Use all fields from the model
class LogForm(forms.ModelForm):
    
    class Meta:
        model = Enquirylogs
        fields = ['contact_by','staff_contact','exp_date','comment','student','log_date']
    def __init__(self,*args, **kwargs):
        super(LogForm, self).__init__(*args, **kwargs)
        self.fields['student'].widget.attrs['style'] = "display:none;"
        self.fields['student'].label = ""
        self.fields['comment'].widget = forms.widgets.Textarea(attrs={"rows": 1,"cols":25})
        self.fields["exp_date"].widget = forms.widgets.DateInput(attrs={"type": "date"})
        self.fields["log_date"].widget = forms.widgets.DateInput(attrs={"type": "date"})

class StudentEnquiryForm(forms.ModelForm):
    class Meta:
        model = StudentEnquiryModel
        fields = '__all__'  # Use all fields from the model

    def __init__(self, *args, **kwargs):
        super(StudentEnquiryForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.required:
                self.fields[field_name].label = f"{field.label} *"
        self.fields["student_company_name"].required = False
        self.fields["studying_course"].required = False
        self.fields["time_to_study"] = forms.ModelMultipleChoiceField(
        queryset=Time.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True  
    )
        for field_name, field in self.fields.items():
            field.widget.attrs["autocomplete"] = "off"
        optional_fields = [
            "student_company_name",
            "studying_course",
            "studying_year",
        
            # Add more fields as needed
        ]
        for field_name in optional_fields:
            self.fields[field_name].required = False
        # Group fields into sections
        personal_info_fields = ['name', 'f_name','m_name','address','address1','address2','taluka', 'district','pincode', 'mobile_number', 'email','date_of_birth','student_role', 'student_company_name','gender']
        qualification_fiedls = ['qualification', 'qualification_status', 'studying_year', 'studying_course','student_college_name']
        others_fields = [
            
             'need_of_study', 'course_to_join','new_course', 'time_to_study', 'known_csc',"verfied"
        ]

        # Set fieldsets for sections
        self.fieldsets = {
            'personal_info': personal_info_fields,
            'qualification_use' :qualification_fiedls,
            'others': others_fields,
        }

    def fieldsets_as_dict(self):
        # Convert fieldsets to a dictionary for use in templates
        return {key: [self[field] for field in fields] for key, fields in self.fieldsets.items()}
