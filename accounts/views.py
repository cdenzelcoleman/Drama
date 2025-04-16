from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages
from .forms import EmailSignUpForm

User = get_user_model()

def email_signup_view(request):
    if request.method == 'POST':
        form = EmailSignUpForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            # Next steps: create a user or redirect to set password
            # For demo, we'll just pass email to the next step
            request.session['signup_email'] = email
            return redirect('password_setup')
    else:
        form = EmailSignUpForm()
    return render(request, 'accounts/email_signup.html', {'form': form})

def password_setup_view(request):
    email = request.session.get('signup_email')
    if not email:
        return redirect('email_signup') 
    # Process password creation form here...