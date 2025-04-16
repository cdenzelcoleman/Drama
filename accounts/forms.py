from django import forms

class EmailSignUpForm(forms.Form):
    email = forms.EmailField(
        label='Enter your email',
        widget=forms.EmailInput(attrs={'placeholder': 'you@example.com', 'class': 'form-control'})
    )

class PasswordSetupForm(forms.Form):
    password = forms.CharField(
        label='Enter your password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password_confirm = forms.CharField(
        label='Confirm your password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data
