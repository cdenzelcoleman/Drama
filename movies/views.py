from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
import requests
from django.conf import settings
from .models import Movie, MovieList, MovieRating
from datetime import datetime

TMDB_API_KEY = '8c8e1a50c91ae21ca9f8489a809b1cf0'
TMDB_BASE_URL = 'https://api.themoviedb.org/3'

def get_movie_from_tmdb(tmdb_id):
    url = f"{TMDB_BASE_URL}/movie/{tmdb_id}"
    params = {'api_key': TMDB_API_KEY}
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data
    return None

def search_movies_tmdb(query, page=1):
    url = f"{TMDB_BASE_URL}/search/movie"
    params = {
        'api_key': TMDB_API_KEY,
        'query': query,
        'page': page
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return None

def get_popular_movies(page=1):
    url = f"{TMDB_BASE_URL}/movie/popular"
    params = {
        'api_key': TMDB_API_KEY,
        'page': page
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return None

def index(request):
    query = request.GET.get('q', '')
    genre = request.GET.get('genre', '')
    year = request.GET.get('year', '')
    page = int(request.GET.get('page', 1))
    
    movies_data = None
    
    if query:
        movies_data = search_movies_tmdb(query, page)
    else:
        movies_data = get_popular_movies(page)
    
    movies = []
    if movies_data and 'results' in movies_data:
        for movie_data in movies_data['results']:
            if genre and genre not in [str(g) for g in movie_data.get('genre_ids', [])]:
                continue
            
            if year and movie_data.get('release_date'):
                movie_year = movie_data['release_date'][:4]
                if movie_year != year:
                    continue
            
            movie, created = Movie.objects.get_or_create(
                tmdb_id=movie_data['id'],
                defaults={
                    'title': movie_data.get('title', ''),
                    'overview': movie_data.get('overview', ''),
                    'poster_path': movie_data.get('poster_path', ''),
                    'backdrop_path': movie_data.get('backdrop_path', ''),
                    'release_date': datetime.strptime(movie_data['release_date'], '%Y-%m-%d').date() if movie_data.get('release_date') else None,
                    'vote_average': movie_data.get('vote_average', 0.0),
                    'vote_count': movie_data.get('vote_count', 0),
                    'genre_ids': movie_data.get('genre_ids', [])
                }
            )
            movies.append(movie)
    
    context = {
        'movies': movies,
        'query': query,
        'genre': genre,
        'year': year,
        'page': page,
        'has_next': movies_data.get('page', 1) < movies_data.get('total_pages', 1) if movies_data else False,
        'has_previous': page > 1
    }
    
    return render(request, 'movies/index.html', context)

@login_required
def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    user_rating = None
    
    try:
        user_rating = MovieRating.objects.get(user=request.user, movie=movie)
    except MovieRating.DoesNotExist:
        pass
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        review = request.POST.get('review', '')
        
        if rating:
            user_rating, created = MovieRating.objects.update_or_create(
                user=request.user,
                movie=movie,
                defaults={'rating': int(rating), 'review': review}
            )
            messages.success(request, 'Rating saved successfully!')
    
    context = {
        'movie': movie,
        'user_rating': user_rating
    }
    
    return render(request, 'movies/detail.html', context)