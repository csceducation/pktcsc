from django import forms
from .models import CourseModel,CourseSubjectModel,CourseBookModel,CourseExamModel

class CourseModelForm(forms.ModelForm):
    class Meta:
        model = CourseModel
        fields = ['status', 'course_name', 'course_s_name', 'course_duration', 'course_fee']

    def __init__(self, *args, **kwargs):
        super(CourseModelForm, self).__init__(*args, **kwargs)
        # Add any customizations to form fields here, if needed
        # For example, you can set placeholders, additional attributes, etc.
        self.fields['course_duration'].widget.attrs['placeholder'] = 'Enter course duration in Hours'
        self.fields['course_name'].widget.attrs['placeholder'] = 'Enter Full name of the Course'
        self.fields['course_s_name'].widget.attrs['placeholder'] = "Enter the short  name of course"
 
class CourseSubjectModelForm(forms.ModelForm):
    class Meta:
        model = CourseSubjectModel
        fields = ['course', 'sub_name']

    def __init__(self, *args, **kwargs):
        super(CourseSubjectModelForm, self).__init__(*args, **kwargs)

class CourseBookModelForm(forms.ModelForm):
    class Meta:
        models = CourseBookModel
        field = '__all__'
        
class CourseExamModelForm(forms.ModelForm):
    class Meta:
        models = CourseExamModel
        field = '__all__'
        