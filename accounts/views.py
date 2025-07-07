from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import UserProfile
from movies.models import Friendship, FriendRequest
from .forms import SignUpForm

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)
        if user is not None:
            auth_login(request, user)
            return HttpResponseRedirect('/accounts/profile/')
        else:
            messages.error(request, "Invalid email or password.")
    return render(request, "accounts/login.html")

def logout_view(request):
    auth_logout(request)
    return HttpResponseRedirect('/accounts/login/')

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

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile if it doesn't exist
            UserProfile.objects.get_or_create(user=user)
            # Log the user in automatically
            auth_login(request, user)
            messages.success(request, 'Account created successfully!')
            return HttpResponseRedirect('/accounts/profile/')
    else:
        form = SignUpForm()
    
    return render(request, 'accounts/signup.html', {'form': form})

@login_required
def add_friend(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    if to_user == request.user:
        messages.error(request, "You cannot add yourself as a friend.")
        return HttpResponseRedirect('/accounts/profile/')
    
    # Check if already friends
    if Friendship.are_friends(request.user, to_user):
        messages.info(request, f"You are already friends with {to_user.username}")
        return HttpResponseRedirect('/accounts/profile/')
    
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
    
    return HttpResponseRedirect('/accounts/profile/')

@login_required
def accept_friend(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
    
    if friend_request.accept():
        messages.success(request, f"You are now friends with {friend_request.from_user.username}")
    else:
        messages.error(request, "Unable to accept friend request")
    
    return HttpResponseRedirect('/accounts/profile/')

@login_required
def decline_friend(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
    
    if friend_request.decline():
        messages.success(request, f"Declined friend request from {friend_request.from_user.username}")
    else:
        messages.error(request, "Unable to decline friend request")
    
    return HttpResponseRedirect('/accounts/profile/')

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

@login_required
def upload_avatar(request):
    if request.method == 'POST' and request.FILES.get('avatar'):
        try:
            profile, _ = UserProfile.objects.get_or_create(user=request.user)
            profile.avatar = request.FILES['avatar']
            profile.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'No file provided'})
