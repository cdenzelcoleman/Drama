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
from .models import Movie, MovieList, MovieRating, Room, RoomMembership, Game, GameResult
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Q

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

def get_random_movies(page=1):
    import random
    # Get a random page from 1-500 to get diverse results
    random_page = random.randint(1, 100)
    
    url = f"{TMDB_BASE_URL}/discover/movie"
    params = {
        'api_key': TMDB_API_KEY,
        'page': random_page,
        'sort_by': 'popularity.desc',
        'vote_count.gte': 100  # Ensure movies have enough votes
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        # Shuffle the results for more randomness
        if 'results' in data:
            random.shuffle(data['results'])
        return data
    return None

def index(request):
    query = request.GET.get('q', '')
    genre = request.GET.get('genre', '')
    year = request.GET.get('year', '')
    random_search = request.GET.get('random', '')
    page = int(request.GET.get('page', 1))
    
    movies_data = None
    
    if query:
        movies_data = search_movies_tmdb(query, page)
    elif random_search:
        movies_data = get_random_movies(page)
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
        'random_search': random_search,
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

# Room Views
@login_required
def rooms_index(request):
    user_rooms = Room.objects.filter(
        Q(owner=request.user) | Q(members=request.user)
    ).distinct().order_by('-updated_at')
    
    context = {
        'rooms': user_rooms
    }
    return render(request, 'movies/rooms/index.html', context)

@login_required
def room_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        emails = request.POST.get('emails', '').split(',')
        
        if name:
            room = Room.objects.create(name=name, owner=request.user)
            
            # Add owner as member
            RoomMembership.objects.create(
                room=room, 
                user=request.user, 
                status='accepted'
            )
            
            # Send invites
            for email in emails:
                email = email.strip()
                if email:
                    try:
                        user = User.objects.get(email=email)
                        RoomMembership.objects.get_or_create(
                            room=room, 
                            user=user,
                            defaults={'status': 'pending'}
                        )
                    except User.DoesNotExist:
                        messages.warning(request, f"User with email {email} not found")
            
            messages.success(request, f"Room '{name}' created successfully!")
            return redirect('room_detail', room_id=room.id)
    
    return render(request, 'movies/rooms/create.html')

@login_required
def room_detail(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    
    # Check if user is member or owner
    if not (room.owner == request.user or room.members.filter(id=request.user.id).exists()):
        messages.error(request, "You don't have access to this room")
        return redirect('rooms_index')
    
    memberships = RoomMembership.objects.filter(room=room).select_related('user')
    games = Game.objects.filter(room=room).select_related('movie', 'created_by').order_by('-created_at')
    
    context = {
        'room': room,
        'memberships': memberships,
        'games': games,
        'is_owner': room.owner == request.user
    }
    return render(request, 'movies/rooms/detail.html', context)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def add_movie_to_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    
    # Check if user is member
    if not (room.owner == request.user or room.members.filter(id=request.user.id).exists()):
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        data = json.loads(request.body)
        movie_id = data.get('movie_id')
        movie = get_object_or_404(Movie, id=movie_id)
        
        room.selected_movies.add(movie)
        return JsonResponse({'success': True, 'message': f'{movie.title} added to room'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def respond_to_invitation(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    membership = get_object_or_404(RoomMembership, room=room, user=request.user)
    
    if request.method == 'POST':
        response = request.POST.get('response')
        if response in ['accepted', 'declined']:
            membership.status = response
            membership.responded_at = timezone.now()
            membership.save()
            
            if response == 'accepted':
                messages.success(request, f"You joined the room '{room.name}'!")
                return redirect('room_detail', room_id=room.id)
            else:
                messages.info(request, f"You declined the invitation to '{room.name}'")
                return redirect('rooms_index')
    
    context = {'room': room, 'membership': membership}
    return render(request, 'movies/rooms/invitation.html', context)

# Game Views  
@login_required
def create_game(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    
    # Check if user is member
    if not (room.owner == request.user or room.members.filter(id=request.user.id).exists()):
        messages.error(request, "You don't have access to this room")
        return redirect('rooms_index')
    
    if request.method == 'POST':
        movie_id = request.POST.get('movie_id')
        game_type = request.POST.get('game_type')
        
        if movie_id and game_type in ['taps', 'shake']:
            movie = get_object_or_404(Movie, id=movie_id)
            game = Game.objects.create(
                room=room,
                movie=movie,
                game_type=game_type,
                created_by=request.user
            )
            
            messages.success(request, f"{game.get_game_type_display()} game created for {movie.title}!")
            return redirect('play_game', game_id=game.id)
    
    context = {
        'room': room,
        'movies': room.selected_movies.all()
    }
    return render(request, 'movies/games/create.html', context)

@login_required
def play_game(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    
    # Check if user is member of the room
    if not (game.room.owner == request.user or game.room.members.filter(id=request.user.id).exists()):
        messages.error(request, "You don't have access to this game")
        return redirect('rooms_index')
    
    # Check if user already played
    existing_result = GameResult.objects.filter(game=game, player=request.user).first()
    
    context = {
        'game': game,
        'existing_result': existing_result
    }
    
    if game.game_type == 'taps':
        return render(request, 'games/taps/play.html', context)
    elif game.game_type == 'shake':
        return render(request, 'games/shake/play.html', context)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def submit_game_result(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    
    # Check if user is member of the room
    if not (game.room.owner == request.user or game.room.members.filter(id=request.user.id).exists()):
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        data = json.loads(request.body)
        score = int(data.get('score', 0))
        
        result, created = GameResult.objects.update_or_create(
            game=game,
            player=request.user,
            defaults={'score': score}
        )
        
        return JsonResponse({
            'success': True,
            'score': result.score,
            'created': created
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def game_results(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    
    # Check if user is member of the room
    if not (game.room.owner == request.user or game.room.members.filter(id=request.user.id).exists()):
        messages.error(request, "You don't have access to this game")
        return redirect('rooms_index')
    
    results = GameResult.objects.filter(game=game).select_related('player').order_by('-score')
    
    context = {
        'game': game,
        'results': results,
        'winner': results.first() if results else None
    }
    return render(request, 'movies/games/results.html', context)

@login_required
@csrf_exempt
@require_http_methods(["GET"])
def api_user_rooms(request):
    """API endpoint to get user's rooms"""
    user_rooms = Room.objects.filter(
        Q(owner=request.user) | Q(members=request.user)
    ).distinct().values('id', 'name')
    
    return JsonResponse(list(user_rooms), safe=False)

# Favorites Views
@login_required
def favorites(request):
    """User's favorite movies"""
    # For now, get user's highest rated movies as favorites
    favorite_ratings = MovieRating.objects.filter(
        user=request.user, 
        rating__gte=4
    ).select_related('movie').order_by('-rating', '-created_at')
    
    context = {
        'favorite_movies': [rating.movie for rating in favorite_ratings]
    }
    return render(request, 'movies/favorites.html', context)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def toggle_favorite(request, movie_id):
    """Toggle favorite status for a movie"""
    movie = get_object_or_404(Movie, id=movie_id)
    rating, created = MovieRating.objects.get_or_create(
        user=request.user,
        movie=movie,
        defaults={'rating': 5, 'review': ''}
    )
    
    if not created:
        if rating.rating >= 4:
            # Remove from favorites
            rating.rating = 3
        else:
            # Add to favorites
            rating.rating = 5
        rating.save()
    
    return JsonResponse({
        'is_favorite': rating.rating >= 4,
        'rating': rating.rating
    })

# Notifications Views
@login_required
def notifications(request):
    """User notifications"""
    # Sample notifications - in real app, these would come from database
    notifications = [
        {
            'id': 1,
            'type': 'friend_request',
            'icon': '👋',
            'title': 'New friend request',
            'message': 'John Doe sent you a friend request',
            'time': '2 hours ago',
            'unread': True
        },
        {
            'id': 2,
            'type': 'game_invite',
            'icon': '🎮',
            'title': 'Game invitation',
            'message': 'Sarah invited you to play Taps Game',
            'time': '4 hours ago',
            'unread': True
        },
        {
            'id': 3,
            'type': 'room_invite',
            'icon': '🏠',
            'title': 'Room invitation',
            'message': 'Mike added you to "Horror Movie Night"',
            'time': '1 day ago',
            'unread': False
        },
        {
            'id': 4,
            'type': 'movie_comment',
            'icon': '💬',
            'title': 'New comment',
            'message': 'Alex commented on "The Matrix"',
            'time': '2 days ago',
            'unread': False
        }
    ]
    
    context = {
        'notifications': notifications,
        'unread_count': sum(1 for n in notifications if n['unread'])
    }
    return render(request, 'movies/notifications.html', context)