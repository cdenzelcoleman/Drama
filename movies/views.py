from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import requests
import json
from django.conf import settings
from .models import Movie, MovieList, MovieRating
from datetime import datetime

TMDB_API_KEY = settings.TMDB_API_KEY
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
    print(f"TMDB Search - URL: {url}, Params: {params}")
    print(f"TMDB Search - Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"TMDB Search - Results count: {len(data.get('results', []))}")
        return data
    else:
        print(f"TMDB Search - Error: {response.text}")
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
            
            try:
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
            except Exception as e:
                print(f"Error creating movie {movie_data.get('title', 'Unknown')}: {e}")
                continue
    
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

# API Views
@csrf_exempt
@require_http_methods(["GET"])
def api_movies_list(request):
    """API endpoint to get list of movies"""
    query = request.GET.get('q', '')
    page = int(request.GET.get('page', 1))
    
    movies_data = None
    if query:
        movies_data = search_movies_tmdb(query, page)
    else:
        movies_data = get_popular_movies(page)
    
    movies = []
    if movies_data and 'results' in movies_data:
        for movie_data in movies_data['results']:
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
            
            movies.append({
                'id': movie.id,
                'tmdb_id': movie.tmdb_id,
                'title': movie.title,
                'overview': movie.overview,
                'poster_url': movie.poster_url,
                'backdrop_url': movie.backdrop_url,
                'release_date': movie.release_date.isoformat() if movie.release_date else None,
                'vote_average': movie.vote_average,
                'vote_count': movie.vote_count,
                'genre_ids': movie.genre_ids
            })
    
    return JsonResponse({
        'movies': movies,
        'page': page,
        'total_pages': movies_data.get('total_pages', 1) if movies_data else 1,
        'total_results': movies_data.get('total_results', 0) if movies_data else 0
    })

@csrf_exempt
@require_http_methods(["GET"])
def api_movie_detail(request, movie_id):
    """API endpoint to get movie details"""
    try:
        movie = Movie.objects.get(id=movie_id)
        data = {
            'id': movie.id,
            'tmdb_id': movie.tmdb_id,
            'title': movie.title,
            'overview': movie.overview,
            'poster_url': movie.poster_url,
            'backdrop_url': movie.backdrop_url,
            'release_date': movie.release_date.isoformat() if movie.release_date else None,
            'vote_average': movie.vote_average,
            'vote_count': movie.vote_count,
            'genre_ids': movie.genre_ids,
            'created_at': movie.created_at.isoformat()
        }
        return JsonResponse(data)
    except Movie.DoesNotExist:
        return JsonResponse({'error': 'Movie not found'}, status=404)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def api_rate_movie(request, movie_id):
    """API endpoint to rate a movie"""
    try:
        movie = Movie.objects.get(id=movie_id)
        data = json.loads(request.body)
        rating = data.get('rating')
        review = data.get('review', '')
        
        if not rating or not (1 <= int(rating) <= 5):
            return JsonResponse({'error': 'Rating must be between 1 and 5'}, status=400)
        
        user_rating, created = MovieRating.objects.update_or_create(
            user=request.user,
            movie=movie,
            defaults={'rating': int(rating), 'review': review}
        )
        
        return JsonResponse({
            'success': True,
            'rating': user_rating.rating,
            'review': user_rating.review,
            'created': created
        })
    except Movie.DoesNotExist:
        return JsonResponse({'error': 'Movie not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)