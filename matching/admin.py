from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import User, Event


class UserCreationForm(forms.ModelForm):
    class Meta(object):
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2


class StudentCreationForm(UserCreationForm):
    """A form for creating new students. Includes all the required
    fields, plus a repeated password."""

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_student = True
        if commit:
            user.save()
        return user


class RecruiterCreationForm(UserCreationForm):
    """A form for creating new recruiters. Includes all the required
    fields, plus a repeated password."""

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.enable_host_event = True
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta(object):
        model = User
        fields = ('username', 'email',
                  'tell', 'profile_image', 'first_name', 'last_name',
                  'is_student', 'enable_host_event', 'is_active', 'is_admin',
                  ) + \
                 ('nickname',
                  'university', 'date_of_birth',
                  'sex', 'year', 's_and_h',
                  'major', 'indestry1', 'indestry2', 'indestry3',
                  'job1', 'job2', 'job3', 'company_type',) + \
                 ('company_name', 'department_name', 'position',)

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class UserAdmin(BaseUserAdmin):
    # The forms to add and change student instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the Student model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('username', 'first_name', 'last_name', 'email', 'is_admin', 'enable_host_event', 'is_student')
    list_filter = ('is_admin', 'enable_host_event', 'is_student')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email', 'first_name', 'last_name', 'tell', 'profile_image',)}),
        ('Student info', {'fields': ('nickname', 'university', 'date_of_birth',
                                     'sex', 'year', 's_and_h',
                                     'major', 'indestry1', 'indestry2', 'indestry3',
                                     'job1', 'job2', 'job3', 'company_type',)}),
        ('Recruiter info', {'fields': ('company_name', 'department_name', 'position',)}),
        ('Permissions', {'fields': ('enable_host_event', 'is_student', 'is_admin',)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a student.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2')}
         ),
    )
    search_fields = ('username',)
    ordering = ('username',)
    filter_horizontal = ()


class EventAdmin(admin.ModelAdmin):
    list_display = ('event_id', 'name', 'video_url',)
    list_display_links = ('event_id', 'name')
    list_filter = ('sex', 'year', 's_and_h', 'major', 'company_type')
    readonly_fields = (
        'min_matching_score', 'recommend_users', 'students', 'created_by', 'created_at', 'updated_at',)
    fieldsets = (
        (None, {'fields': ('name', 'event_id',)}),
        ('Detail',
         {'fields': (
             'video_url', 'thumbnail', 'date', 'time', 'place', 'event_type_tag', 'participant_num',
             'comment01', 'comment02', 'created_by', 'created_at', 'updated_at')}),
        ('Parameters', {'fields': ('sex', 'year', 's_and_h',
                                   'major', 'indestry1', 'indestry2', 'indestry3',
                                   'job1', 'job2', 'job3', 'company_type',)}),
        ('Matching setting',
         {'fields': ('recommend_users_num', 'enable_matching', 'min_matching_score', 'recommend_users', 'students'), }),
    )

    def save_model(self, request, obj, form, change):
        """
        Given a model instance save it to the database.
        """
        obj.created_by = '@staff'
        obj.save()


# Now register the new StudentAdmin and RecruiterAdmin...
admin.site.register(User, UserAdmin)

# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.register(Event, EventAdmin)
