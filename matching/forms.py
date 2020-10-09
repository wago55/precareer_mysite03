from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms.widgets import TextInput
from django.forms import ModelForm
from django import forms
from django.utils.dateparse import parse_duration

from .models import User, Event
from .match import do_match
from .utils import constract


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
            'first_name', 'last_name', 'profile_image', 'email',
            'nickname', 'university', 'date_of_birth', 'sex',
            'year', 's_and_h', 'major', 'indestry1', 'indestry2', 'indestry3',
            'job1', 'job2', 'job3', 'company_type',
        )


class RecruiterEditForm(ModelForm):
    """Edit Form for Recruiter"""

    class Meta(object):
        model = User
        fields = (
            'first_name', 'last_name', 'profile_image', 'email',
            'recruiter_type', 'company_name', 'department_name', 'position', 'operating_medium',
        )


class EventEditForm(ModelForm):
    """Edit Form for Event"""
    year = forms.MultipleChoiceField(
        label='卒業年',
        choices=constract.YEAR_CATEGORY,
        widget=forms.CheckboxSelectMultiple,
    )

    date = forms.DateTimeField(
        label='開始日時',
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        input_formats=['%Y-%m-%dT%H:%M']
    )

    time = DurationInput()

    class Meta(object):
        model = Event
        fields = (
            'event_id', 'name', 'host', 'thumbnail', 'place', 'event_type_tag',
            'video_url', 'date', 'time', 'participant_num',
            'comment01', 'comment02',
            'year', 's_and_h',
            'indestry1', 'indestry2', 'indestry3',
        )

    def save(self, commit=True):
        """
        Save this form's self.instance object if commit=True. Otherwise, add
        a save_m2m() method to the form which can be called after the instance
        is saved manually at a later time. Return the model instance.
        """
        if self.errors:
            raise ValueError(
                "The %s could not be %s because the data didn't validate." % (
                    self.instance._meta.object_name,
                    'created' if self.instance._state.adding else 'changed',
                )
            )
        do_match()
        if commit:
            # If committing, save the instance and the m2m data immediately.
            self.instance.save()
            self._save_m2m()
        else:
            # If not committing, add a method to the form to allow deferred
            # saving of m2m data.
            self.save_m2m = self._save_m2m
        return self.instance
