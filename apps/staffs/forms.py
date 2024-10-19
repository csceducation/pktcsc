from django import forms
from .models import Staff

class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = '__all__'

    def clean_mobile_number(self):
        mobile_number = self.cleaned_data['mobile_number']
        return mobile_number