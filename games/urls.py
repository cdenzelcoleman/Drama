from django.urls import path
from . import views

urlpatterns = [
    # Taps game URLs
    path('taps/', views.taps_index, name='taps_index'),
    path('taps/<int:game_id>/', views.taps_detail, name='taps_detail'),
    path('taps/<int:game_id>/play/', views.taps_play, name='taps_play'),
    
    # Shake game URLs
    path('shake/', views.shake_index, name='shake_index'),
    path('shake/<int:game_id>/', views.shake_detail, name='shake_detail'),
    path('shake/<int:game_id>/play/', views.shake_play, name='shake_play'),
]
