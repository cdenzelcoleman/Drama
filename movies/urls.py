from django.urls import path
from . import views

app_name = 'movies'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:movie_id>/', views.movie_detail, name='detail'),
    
    # Room URLs
    path('rooms/', views.rooms_index, name='rooms_index'),
    path('rooms/create/', views.room_create, name='room_create'),
    path('rooms/<uuid:room_id>/', views.room_detail, name='room_detail'),
    path('rooms/<uuid:room_id>/add-movie/', views.add_movie_to_room, name='add_movie_to_room'),
    path('rooms/<uuid:room_id>/invitation/', views.respond_to_invitation, name='respond_to_invitation'),
    
    # Game URLs
    path('rooms/<uuid:room_id>/games/create/', views.create_game, name='create_game'),
    path('games/<uuid:game_id>/play/', views.play_game, name='play_game'),
    path('games/<uuid:game_id>/submit/', views.submit_game_result, name='submit_game_result'),
    path('games/<uuid:game_id>/results/', views.game_results, name='game_results'),
    
    # API endpoints
    path('api/movies/', views.api_movies_list, name='api_movies_list'),
    path('api/movies/<int:movie_id>/', views.api_movie_detail, name='api_movie_detail'),
    path('api/movies/<int:movie_id>/rate/', views.api_rate_movie, name='api_rate_movie'),
    path('api/user-rooms/', views.api_user_rooms, name='api_user_rooms'),
]