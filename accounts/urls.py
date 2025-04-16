from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('register/', views.email_signup_view, name='email_signup'),
    path('register/password/', views.password_setup_view, name='password_setup'),
]
