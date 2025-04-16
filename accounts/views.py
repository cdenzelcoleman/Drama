from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import EmailSignUpForm, PasswordSetupForm

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('profile')
        else:
            messages.error(request, "Invalid email or password.")
    return render(request, "accounts/login.html")

def logout_view(request):
    auth_logout(request)
    return redirect("login")

@login_required
def profile_view(request):
    return render(request, "accounts/profile.html")

def email_signup_view(request):
    if request.method == "POST":
        form = EmailSignUpForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            # Check if email is already registered
            if User.objects.filter(email=email).exists():
                messages.error(request, "Email is already registered.")
                return redirect("email_signup")
            # redirect to set a password
            request.session["signup_email"] = email
            return redirect("password_setup")
    else:
        form = EmailSignUpForm()
    return render(request, "accounts/email_signup.html", {"form": form})

def password_setup_view(request):
    email = request.session.get("signup_email")
    if not email:
        return redirect("email_signup")
    if request.method == "POST":
        form = PasswordSetupForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data["password"]
            new_user = User.objects.create_user(username=email, email=email, password=password)
            auth_login(request, new_user)
            del request.session["signup_email"]
            return redirect("profile")
    else:
        form = PasswordSetupForm()
    return render(request, "accounts/password_setup.html", {"form": form, "email": email})
