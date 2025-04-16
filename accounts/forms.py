# accounts/forms.py
from django import forms

class EmailSignUpForm(forms.Form):
    email = forms.EmailField(label='Enter your email')
