from .models import Accounts
from django.forms import ModelForm
from django.utils import timezone
from django import forms

class AccountsForm(ModelForm):
    class Meta:
        model = Accounts
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(AccountsForm, self).__init__(*args, **kwargs)
        self.fields['Date'].initial = timezone.now()
        self.fields['Date'].widget = forms.DateInput(attrs={'type': 'date'})
