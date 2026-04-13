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
    new_email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Leave blank to keep current email', 'class': 'input-premium w-full pl-12 pr-6 py-4 font-bold text-slate-700'}),
        required=False
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Leave blank to keep current password', 'class': 'input-premium w-full pl-12 pr-6 py-4 font-bold text-slate-700'}), 
        required=False
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'address']

    def clean_new_email(self):
        email = self.cleaned_data.get('new_email')
        if email:
            if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("This email is already in use by another account.")
        return email

    def clean_new_password(self):
        password = self.cleaned_data.get('new_password')
        if password:
            if len(password) < 8:
                raise forms.ValidationError("Password must be at least 8 characters long.")
            if not any(char.isupper() for char in password):
                raise forms.ValidationError("Password must contain at least one capital letter.")
            special_characters = "!@#$%^&*()-+?_=,<>/\"'.;:|[]{}\\`~"
            if not any(char in special_characters for char in password):
                raise forms.ValidationError("Password must contain at least one special symbol.")
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('new_password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user

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