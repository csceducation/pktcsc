from django import forms
from django.forms import ModelForm, modelformset_factory

from .models import (
    AcademicSession,
    AcademicTerm,
    SiteConfig,
    StudentClass,
    Subject,
    Book,
    Time,
    Exam
)

SiteConfigForm = modelformset_factory(
    SiteConfig,
    fields=(
        "key",
        "value",
    ),
    extra=0,
)


class AcademicSessionForm(ModelForm):
    prefix = "Academic Session"

    class Meta:
        model = AcademicSession
        fields = ["name", "current"]


class AcademicTermForm(ModelForm):
    prefix = "Academic Term"

    class Meta:
        model = AcademicTerm
        fields = ["name", "current"]


class SubjectForm(ModelForm):
    prefix = "Subject"

    class Meta:
        model = Subject
        fields = ["name",'duration',"contents"]
    def __init__(self, *args, **kwargs):
        super(SubjectForm, self).__init__(*args, **kwargs)
        self.fields['contents'].required = True
class BookForm(ModelForm):
    prefix = "Book"

    class Meta:
        model = Book
        fields = ["name"]
class TimeForm(forms.ModelForm):
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'placeholder': 'HH:MM'}, format='%H:%M'),
        label='Start Time',
        input_formats=['%H:%M']
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'placeholder': 'HH:MM'}, format='%H:%M'),
        label='End Time',
        input_formats=['%H:%M']
    )

    class Meta:
        model = Time
        fields = []

    def save(self, commit=True):
        instance = super(TimeForm, self).save(commit=False)
        start_time = self.cleaned_data.get('start_time')
        end_time = self.cleaned_data.get('end_time')
        instance.time = f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}"
        if commit:
            instance.save()
        return instance
class ExamForm(ModelForm):
    prefix = "Exam"

    class Meta:
        model = Exam
        fields = ["name","exam_mode","exam_duration"]


class StudentClassForm(ModelForm):
    prefix = "Class"

    class Meta:
        model = StudentClass
        fields = ["name"]


class CurrentSessionForm(forms.Form):
    current_session = forms.ModelChoiceField(
        queryset=AcademicSession.objects.all(),
        help_text='Click <a href="/session/create/?next=current-session/">here</a> to add new session',
    )
    current_term = forms.ModelChoiceField(
        queryset=AcademicTerm.objects.all(),
        help_text='Click <a href="/term/create/?next=current-session/">here</a> to add new term',
    )
