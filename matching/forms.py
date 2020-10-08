from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms.widgets import TextInput
from django.forms import ModelForm
from django import forms
from django.utils.dateparse import parse_duration

from .models import User, Event


class DurationInput(TextInput):

    def _format_value(self, value):
        duration = parse_duration(value)

        seconds = duration.seconds

        minutes = seconds // 60
        minutes = minutes % 60

        hours = minutes // 60
        hours = hours % 60

        return '{:02d}:{:02d}'.format(hours, minutes)


class StudentSignUpForm(UserCreationForm):
    """Sign Up Form for Student"""

    class Meta(object):
        model = User
        fields = ("username", "university", "email", "password1", "password2",)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_student = True
        if commit:
            user.save()
        return user


class RecruiterSignUpForm(UserCreationForm):
    """Sign Up Form for Recruiter"""

    class Meta(object):
        model = User
        fields = ("username", "email", "password1", "password2",)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.enable_host_event = True
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    """Login Form"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['password'].widget.attrs['class'] = 'form-control'


class StudentEditForm(ModelForm):
    """Edit Form for Student"""

    class Meta(object):
        model = User
        fields = (
            'first_name', 'last_name', 'profile_image', 'tell', 'email',
            'nickname', 'university', 'date_of_birth', 'phone_number', 'sex',
            'year', 's_and_h', 'major', 'indestry1', 'indestry2', 'indestry3',
            'job1', 'job2', 'job3', 'company_type',
        )


class RecruiterEditForm(ModelForm):
    """Edit Form for Recruiter"""

    class Meta(object):
        model = User
        fields = (
            'first_name', 'last_name', 'profile_image', 'tell', 'email',
            'recruiter_type', 'company_name', 'department_name', 'position', 'operating_medium',
        )


class EventEditForm(ModelForm):
    """Edit Form for Event"""

    class Meta(object):
        model = Event
        fields = (
            'event_id', 'name', 'host', 'thumbnail', 'place', 'event_type_tag',
            'video_url', 'date', 'time', 'participant_num', 'comment01', 'comment02', 'enable_matching',
            'sex', 'year', 's_and_h', 'major',
            'indestry1', 'indestry2', 'indestry3',
            'job1', 'job2', 'job3', 'company_type',
        )

    date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        input_formats=['%Y-%m-%dT%H:%M']
    )

    time = DurationInput()
