from django.urls import path
from . import views

app_name = 'games'
urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create_game, name='create'),
    
    # Taps game URLs
    path('taps/', views.taps_index, name='taps_index'),
    path('taps/<int:game_id>/', views.taps_detail, name='taps_detail'),
    path('taps/<int:game_id>/play/', views.taps_play, name='taps_play'),
    
    # Connect Four game URLs
    path('connect_four/', views.connect_four_index, name='connect_four_index'),
    path('connect_four/<int:game_id>/', views.connect_four_detail, name='connect_four_detail'),
    path('connect_four/<int:game_id>/play/', views.connect_four_play, name='connect_four_play'),
]
