from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from .models import UserProfile
from movies.models import Friendship, FriendRequest
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
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    # Get actual friends using the Friendship model
    friends = Friendship.get_friends(request.user)
    
    # Get pending friend requests sent to this user
    pending_requests = FriendRequest.objects.filter(
        to_user=request.user,
        status='pending'
    )
    
    return render(request, "accounts/profile.html", {
        'profile': profile,
        'friends': friends,
        'pending_requests': pending_requests
    })

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
            UserProfile.objects.create(user=new_user)
            auth_login(request, new_user)
            del request.session["signup_email"]
            return redirect("profile")
    else:
        form = PasswordSetupForm()
    return render(request, "accounts/password_setup.html", {"form": form, "email": email})

@login_required
def add_friend(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    if to_user == request.user:
        messages.error(request, "You cannot add yourself as a friend.")
        return redirect('accounts:profile')
    
    # Check if already friends
    if Friendship.are_friends(request.user, to_user):
        messages.info(request, f"You are already friends with {to_user.username}")
        return redirect('accounts:profile')
    
    # Create or get existing friend request
    friend_request, created = FriendRequest.objects.get_or_create(
        from_user=request.user,
        to_user=to_user,
        defaults={'status': 'pending'}
    )
    
    if created:
        messages.success(request, f"Friend request sent to {to_user.username}")
    else:
        if friend_request.status == 'pending':
            messages.info(request, "Friend request already sent")
        elif friend_request.status == 'declined':
            messages.info(request, "Friend request was previously declined")
    
    return redirect('accounts:profile')

@login_required
def accept_friend(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
    
    if friend_request.accept():
        messages.success(request, f"You are now friends with {friend_request.from_user.username}")
    else:
        messages.error(request, "Unable to accept friend request")
    
    return redirect('accounts:profile')

@login_required
def decline_friend(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
    
    if friend_request.decline():
        messages.success(request, f"Declined friend request from {friend_request.from_user.username}")
    else:
        messages.error(request, "Unable to decline friend request")
    
    return redirect('accounts:profile')

@login_required
def search_users(request):
    query = request.GET.get('q', '')
    users = []
    
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query)
        ).exclude(id=request.user.id)[:10]
    
    return render(request, 'accounts/search_users.html', {
        'users': users,
        'query': query
    })
