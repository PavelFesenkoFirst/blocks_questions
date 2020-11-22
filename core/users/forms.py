from wsgiref.handlers import format_date_time

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model

from core.users.models import Users
User = get_user_model()

class RegisterUserForm(UserCreationForm):

    class Meta:
        model = User
        fields = (
         'username', 'email', 'first_name', 'last_name', 'birth_date', 'description', 'password1', 'password2'
        )


class PhotoForm(forms.ModelForm):
    class Meta:
        model = Users
        fields = ('image',)

    def clean_photo(self):
        photo = self.cleaned_data.get('image')
        return photo
