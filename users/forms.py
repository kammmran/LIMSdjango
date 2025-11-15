from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Role


class UserRegistrationForm(UserCreationForm):
    """Form for registering new users."""
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 
                  'phone', 'department', 'employee_id', 'password1', 'password2']


class UserUpdateForm(forms.ModelForm):
    """Form for updating user information."""
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'role', 
                  'phone', 'department', 'employee_id', 'is_active']


class LoginForm(AuthenticationForm):
    """Custom login form."""
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))


class RoleForm(forms.ModelForm):
    """Form for creating/editing roles."""
    class Meta:
        model = Role
        fields = '__all__'
