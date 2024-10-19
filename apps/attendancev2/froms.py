from django import forms

class DateForm(forms.Form):
    date = forms.DateField(label='Select Date', widget=forms.DateInput(attrs={'type': 'date'}))
    entrytime = forms.TimeField(label='Entry Time', widget=forms.TimeInput(attrs={'type': 'time'}))
    exittime = forms.TimeField(label='Exit Time', widget=forms.TimeInput(attrs={'type': 'time'}))
    content = forms.CharField(
        required=False,
        label='Content',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5})
    )