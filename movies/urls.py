from django.urls import path
from . import views

app_name = 'movies'
urlpatterns = [
    path('', views.home, name='home'),
    path('discover/', views.discover, name='discover'),
    path('<int:movie_id>/', views.movie_detail, name='detail'),
    
    # Game URLs (now tied to challenges)
    path('challenges/<uuid:challenge_id>/games/create/', views.create_challenge_game, name='create_challenge_game'),
    path('games/<uuid:game_id>/play/', views.play_game, name='play_game'),
    path('games/<uuid:game_id>/submit/', views.submit_game_result, name='submit_game_result'),
    path('games/<uuid:game_id>/results/', views.game_results, name='game_results'),
    
    # Favorites and Notifications
    path('favorites/', views.favorites, name='favorites'),
    path('notifications/', views.notifications, name='notifications'),
    
    # Friends
    path('friends/', views.friends_list, name='friends_list'),
    path('search-users/', views.search_users, name='search_users'),
    
    # API endpoints
    path('api/movies/', views.api_movies_list, name='api_movies_list'),
    path('api/movies/<int:movie_id>/', views.api_movie_detail, name='api_movie_detail'),
    path('api/movies/<int:movie_id>/rate/', views.api_rate_movie, name='api_rate_movie'),
    path('api/movies/<int:movie_id>/toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
    
    # Friend API endpoints
    path('api/friends/request/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('api/friends/respond/<int:request_id>/', views.respond_friend_request, name='respond_friend_request'),
    path('api/friends/remove/<int:user_id>/', views.remove_friend, name='remove_friend'),
    
    # Challenge URLs
    path('challenges/<uuid:challenge_id>/', views.challenge_detail, name='challenge_detail'),
    path('api/challenges/create/<int:user_id>/', views.create_challenge, name='create_challenge'),
    path('api/challenges/<uuid:challenge_id>/select-movie/', views.select_challenge_movie, name='select_challenge_movie'),
]