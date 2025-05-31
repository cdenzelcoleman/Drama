from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('register/', views.email_signup_view, name='email_signup'),
    path('register/password/', views.password_setup_view, name='password_setup'),
    path('friends/add/<int:user_id>/', views.add_friend, name='add_friend'),
    path('friends/accept/<int:request_id>/', views.accept_friend, name='accept_friend'),
    path('friends/decline/<int:request_id>/', views.decline_friend, name='decline_friend'),
    path('friends/search/', views.search_users, name='search_users'),
    path('upload-avatar/', views.upload_avatar, name='upload_avatar'),
]
