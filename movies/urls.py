from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Main movie search or landing page
    path('search/', views.search, name='search'),  # Search functionality for movies
    path('movie/<int:movie_id>/', views.moviedetail, name='moviedetail'),  # Detail page for a specific movie
    path('movie/<int:movie_id>/review/', views.add_review, name='addreview'),  # Endpoint to add a review for the movie
]
