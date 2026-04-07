from django import forms
from account.models import User, UserProfile
from django.contrib.auth.forms import UserCreationForm

class RegForm(UserCreationForm):
    class Meta:
        model=User
        fields=["first_name","last_name","email"]

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if first_name and not first_name.isalpha():
            raise forms.ValidationError("First name must contain only alphabetic characters.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if last_name and not last_name.isalpha():
            raise forms.ValidationError("Last name must contain only alphabetic characters.")
        return last_name
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email=forms.CharField(max_length=100,widget=forms.EmailInput(attrs={'placeholder':'Enter Email','class':'form-control'})) 
    password=forms.CharField(max_length=100,widget=forms.PasswordInput(attrs={'placeholder':'Enter Password','class':'form-control'}))

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if first_name and not first_name.isalpha():
            raise forms.ValidationError("First name must contain only alphabetic characters.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if last_name and not last_name.isalpha():
            raise forms.ValidationError("Last name must contain only alphabetic characters.")
        return last_name

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_image', 'phone_number', 'location']

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            if not phone_number.isdigit():
                raise forms.ValidationError("Phone number must contain only digits.")
            elif len(phone_number) != 10:
                raise forms.ValidationError("Phone number must be exactly 10 digits long.")
            elif phone_number[0] not in ['6', '7', '8', '9']:
                raise forms.ValidationError("Phone number must start with 6, 7, 8, or 9.")
        return phone_number