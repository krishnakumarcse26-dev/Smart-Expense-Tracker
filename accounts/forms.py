"""
accounts/forms.py — Registration & Profile Forms

Django Forms handle:
1. Rendering HTML input fields
2. Validating submitted data (server-side)
3. Cleaning and returning Python objects

SECURITY: Django forms automatically sanitize input, preventing XSS attacks.
Never trust raw request.POST data — always use forms.
"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile


class UserRegistrationForm(UserCreationForm):
    """
    Extends Django's built-in UserCreationForm.
    UserCreationForm already includes: username, password1, password2.
    We ADD email as a required field.
    """
    email = forms.EmailField(
        required=True,
        help_text='Required. A valid email address.',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your@email.com'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a username'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to inherited fields
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Create password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm password'})

    def clean_email(self):
        """
        Custom validation: check email is unique.
        Methods named clean_<fieldname> run automatically during form.is_valid().
        Raising ValidationError shows the error on the form field.
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        """Override save to also store the email."""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Automatically create UserProfile when user registers
        
        return user


class UserProfileForm(forms.ModelForm):
    """Form to update the user's profile information."""

    # Fields from the User model (not UserProfile)
    first_name = forms.CharField(max_length=30, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar', 'currency']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'currency': forms.Select(attrs={'class': 'form-select'}),
        }
