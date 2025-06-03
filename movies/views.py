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
from .models import Movie, MovieList, MovieRating, Game, GameResult, Friendship, FriendRequest, Challenge
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Q

TMDB_API_KEY = settings.TMDB_API_KEY
TMDB_BASE_URL = 'https://api.themoviedb.org/3'

class TMDBClient:
    """Unified client for TMDB API operations"""
    
    def __init__(self):
        self.api_key = TMDB_API_KEY
        self.base_url = TMDB_BASE_URL
    
    def _make_request(self, endpoint, params=None):
        """Make a generic request to TMDB API"""
        url = f"{self.base_url}/{endpoint}"
        request_params = {'api_key': self.api_key}
        if params:
            request_params.update(params)
        
        response = requests.get(url, params=request_params)
        if response.status_code == 200:
            return response.json()
        return None
    
    def get_movie(self, tmdb_id):
        """Get a single movie by TMDB ID"""
        return self._make_request(f"movie/{tmdb_id}")
    
    def search_movies(self, query, page=1):
        """Search for movies by query"""
        return self._make_request("search/movie", {'query': query, 'page': page})
    
    def get_popular_movies(self, page=1):
        """Get popular movies"""
        return self._make_request("movie/popular", {'page': page})
    
    def discover_movies(self, page=1, **kwargs):
        """Discover movies with custom parameters"""
        params = {'page': page}
        params.update(kwargs)
        return self._make_request("discover/movie", params)

# Create a shared TMDB client instance
tmdb_client = TMDBClient()

def create_movie_from_tmdb_data(movie_data, release_date=None):
    """
    Create or get a Movie object from TMDB data.
    
    Args:
        movie_data: Dictionary containing TMDB movie data
        release_date: Optional datetime.date object, if not provided will parse from movie_data
    
    Returns:
        Tuple of (movie, created) where movie is the Movie instance and created is boolean
    """
    if release_date is None and movie_data.get('release_date'):
        try:
            release_date = datetime.strptime(movie_data['release_date'], '%Y-%m-%d').date()
        except ValueError:
            release_date = None
    
    return Movie.objects.get_or_create(
        tmdb_id=movie_data['id'],
        defaults={
            'title': movie_data.get('title', ''),
            'overview': movie_data.get('overview', ''),
            'poster_path': movie_data.get('poster_path', ''),
            'backdrop_path': movie_data.get('backdrop_path', ''),
            'release_date': release_date,
            'vote_average': movie_data.get('vote_average', 0.0),
            'vote_count': movie_data.get('vote_count', 0),
            'genre_ids': movie_data.get('genre_ids', [])
        }
    )

def get_movie_from_tmdb(tmdb_id):
    """Legacy wrapper for TMDB client"""
    return tmdb_client.get_movie(tmdb_id)

def search_movies_tmdb(query, page=1):
    """Legacy wrapper for TMDB client"""
    return tmdb_client.search_movies(query, page)

def get_popular_movies(page=1):
    """Legacy wrapper for TMDB client"""
    return tmdb_client.get_popular_movies(page)

def get_random_movies(page=1):
    """Get random movies using discover endpoint"""
    import random
    random_page = random.randint(1, 100)
    
    data = tmdb_client.discover_movies(
        page=random_page,
        sort_by='popularity.desc',
        **{'vote_count.gte': 100}
    )
    
    # Shuffle the results for more randomness
    if data and 'results' in data:
        random.shuffle(data['results'])
    return data

def home(request):
    """Home page with banner and challengers section"""
    featured_movies = []
    active_challenges = []
    
    # Get featured movies for banner (random selection on each reload)
    try:
        import random
        from datetime import date
        current_year = date.today().year
        max_year = current_year - 1  # Only movies from previous year or earlier
        
        # Get a random page from multiple sources for variety
        random_page = random.randint(1, 10)
        
        # Use TMDB discover endpoint to get random older movies
        featured_data = tmdb_client.discover_movies(
            page=random_page,
            **{
                'primary_release_date.lte': f'{max_year}-12-31',
                'vote_average.gte': 6.5,
                'vote_count.gte': 50,
                'sort_by': random.choice(['popularity.desc', 'vote_average.desc', 'release_date.desc'])
            }
        )
        
        if featured_data and 'results' in featured_data:
                # Shuffle the results for more randomness
                movie_results = featured_data['results']
                random.shuffle(movie_results)
                
                # Filter and get movies that are old enough
                for movie_data in movie_results:
                    if len(featured_movies) >= 5:
                        break
                        
                    # Check if movie has release date and is old enough
                    if movie_data.get('release_date') and movie_data.get('backdrop_path'):
                        try:
                            release_date = datetime.strptime(movie_data['release_date'], '%Y-%m-%d').date()
                            if release_date.year <= max_year:
                                movie, created = create_movie_from_tmdb_data(movie_data, release_date)
                                featured_movies.append(movie)
                        except Exception as e:
                            print(f"Error processing movie date for {movie_data.get('title', 'Unknown')}: {e}")
                            continue
        
        # If we still don't have enough movies, try a second random page
        if len(featured_movies) < 5:
            try:
                second_random_page = random.randint(11, 20)
                
                additional_data = tmdb_client.discover_movies(
                    page=second_random_page,
                    **{
                        'primary_release_date.lte': f'{max_year}-12-31',
                        'vote_average.gte': 6.5,
                        'vote_count.gte': 50,
                        'sort_by': random.choice(['popularity.desc', 'vote_average.desc', 'release_date.desc'])
                    }
                )
                
                if additional_data and 'results' in additional_data:
                        additional_results = additional_data['results']
                        random.shuffle(additional_results)
                        
                        for movie_data in additional_results:
                            if len(featured_movies) >= 5:
                                break
                                
                            if movie_data.get('release_date') and movie_data.get('backdrop_path'):
                                try:
                                    release_date = datetime.strptime(movie_data['release_date'], '%Y-%m-%d').date()
                                    if release_date.year <= max_year:
                                        movie, created = create_movie_from_tmdb_data(movie_data, release_date)
                                        featured_movies.append(movie)
                                except Exception as e:
                                    print(f"Error creating additional movie {movie_data.get('title', 'Unknown')}: {e}")
                                    continue
            except Exception as e:
                print(f"Error getting additional movies: {e}")
                
    except Exception as e:
        print(f"Error getting featured movies: {e}")
    
    # Get active challenges for the user
    if request.user.is_authenticated:
        active_challenges = Challenge.objects.filter(
            Q(challenger=request.user) | Q(challenged=request.user),
            status='active'
        ).select_related('challenger', 'challenged', 'challenger_movie', 'challenged_movie').order_by('-created_at')[:10]
    
    context = {
        'featured_movies': featured_movies,
        'active_challenges': active_challenges,
    }
    
    return render(request, 'movies/home.html', context)

def discover(request):
    """Discover movies page with search and filtering"""
    query = request.GET.get('q', '')
    genre = request.GET.get('genre', '')
    year = request.GET.get('year', '')
    random_search = request.GET.get('random', '')
    page = int(request.GET.get('page', 1))
    challenge_id = request.GET.get('challenge', '')
    
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
                movie, created = create_movie_from_tmdb_data(movie_data)
                movies.append(movie)
            except Exception as e:
                print(f"Error creating movie {movie_data.get('title', 'Unknown')}: {e}")
                continue
    
    challenge = None
    if challenge_id:
        try:
            challenge = Challenge.objects.get(id=challenge_id)
            # Verify user is part of this challenge
            if request.user not in [challenge.challenger, challenge.challenged]:
                challenge = None
        except Challenge.DoesNotExist:
            challenge = None

    context = {
        'movies': movies,
        'query': query,
        'genre': genre,
        'year': year,
        'random_search': random_search,
        'page': page,
        'has_next': movies_data.get('page', 1) < movies_data.get('total_pages', 1) if movies_data else False,
        'has_previous': page > 1,
        'challenge': challenge
    }
    
    return render(request, 'movies/discover.html', context)

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
            movie, created = create_movie_from_tmdb_data(movie_data)
            
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


# Game Views  
@login_required
def select_game_type(request, challenge_id):
    """Select game type for challenge"""
    challenge = get_object_or_404(Challenge, id=challenge_id)
    
    # Check if user is part of this challenge
    if request.user not in [challenge.challenger, challenge.challenged]:
        messages.error(request, "You don't have access to this challenge")
        return redirect('movies:home')
    
    # Check if both movies are selected
    if not challenge.both_movies_selected:
        messages.error(request, "Both players must select movies before choosing game type")
        return redirect('movies:challenge_detail', challenge_id=challenge.id)
    
    if request.method == 'POST':
        game_type = request.POST.get('game_type')
        
        if game_type in ['taps', 'shake']:
            # Update the appropriate game type field
            if request.user == challenge.challenger:
                challenge.challenger_game_type = game_type
            else:
                challenge.challenged_game_type = game_type
            
            challenge.save()
            
            # Check if both players have selected and game types match
            if challenge.is_ready_to_play:
                # Auto-create the game and redirect both players to play
                # Use the first movie (challenger's) as the game movie
                game = Game.objects.create(
                    challenge=challenge,
                    movie=challenge.challenger_movie,
                    game_type=game_type,
                    created_by=request.user
                )
                
                messages.success(request, f"Game ready! Let's play {game.get_game_type_display()}!")
                return redirect('movies:play_game', game_id=game.id)
            else:
                messages.success(request, f"You selected {game_type.title()}. Waiting for your opponent...")
                return redirect('movies:challenge_detail', challenge_id=challenge.id)
    
    # Determine if current user has already selected a game type
    is_challenger = request.user == challenge.challenger
    user_game_type = challenge.challenger_game_type if is_challenger else challenge.challenged_game_type
    opponent_game_type = challenge.challenged_game_type if is_challenger else challenge.challenger_game_type
    opponent = challenge.challenged if is_challenger else challenge.challenger
    
    context = {
        'challenge': challenge,
        'user_game_type': user_game_type,
        'opponent_game_type': opponent_game_type,
        'opponent': opponent,
        'is_challenger': is_challenger
    }
    return render(request, 'movies/games/select_type.html', context)

@login_required
def create_challenge_game(request, challenge_id):
    """Legacy endpoint - redirect to game type selection"""
    return redirect('movies:select_game_type', challenge_id=challenge_id)

@login_required
def play_game(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    
    # Check if user is part of the challenge
    if request.user not in [game.challenge.challenger, game.challenge.challenged]:
        messages.error(request, "You don't have access to this game")
        return redirect('movies:home')
    
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
    
    # Check if user is part of the challenge
    if request.user not in [game.challenge.challenger, game.challenge.challenged]:
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
    
    # Check if user is part of the challenge
    if request.user not in [game.challenge.challenger, game.challenge.challenged]:
        messages.error(request, "You don't have access to this game")
        return redirect('movies:home')
    
    results = GameResult.objects.filter(game=game).select_related('player').order_by('-score')
    
    context = {
        'game': game,
        'results': results,
        'winner': results.first() if results else None
    }
    return render(request, 'movies/games/results.html', context)

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
    notifications = []
    
    # Real friend requests
    friend_requests = FriendRequest.objects.filter(
        to_user=request.user,
        status='pending'
    ).select_related('from_user').order_by('-created_at')
    
    for req in friend_requests:
        notifications.append({
            'id': f'friend_request_{req.id}',
            'type': 'friend_request',
            'icon': '👋',
            'title': 'New friend request',
            'message': f'{req.from_user.username} sent you a friend request',
            'time': f'{req.created_at.strftime("%b %d")}',
            'unread': True,
            'request_id': req.id
        })
    
    # Sample notifications for other features
    sample_notifications = [
        {
            'id': 2,
            'type': 'challenge_invite',
            'icon': '🎯',
            'title': 'Challenge invitation',
            'message': 'Sarah challenged you to a movie battle',
            'time': '4 hours ago',
            'unread': True
        },
        {
            'id': 3,
            'type': 'game_invite',
            'icon': '🎮',
            'title': 'Game invitation',
            'message': 'Mike invited you to play Taps Game',
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
    
    # Add sample notifications if no real friend requests
    if not friend_requests:
        notifications.extend(sample_notifications)
    
    context = {
        'notifications': notifications,
        'unread_count': len(friend_requests) + sum(1 for n in sample_notifications if n.get('unread', False))
    }
    return render(request, 'movies/notifications.html', context)

# Friend Request Views
@login_required
def friends_list(request):
    """Display user's friends and friend requests"""
    friends = Friendship.get_friends(request.user)
    pending_requests = FriendRequest.objects.filter(
        to_user=request.user, 
        status='pending'
    ).select_related('from_user').order_by('-created_at')
    sent_requests = FriendRequest.objects.filter(
        from_user=request.user, 
        status='pending'
    ).select_related('to_user').order_by('-created_at')
    
    context = {
        'friends': friends,
        'pending_requests': pending_requests,
        'sent_requests': sent_requests,
    }
    return render(request, 'movies/friends.html', context)

@login_required
def search_users(request):
    """Search for users by username"""
    query = request.GET.get('q', '').strip()
    users = []
    
    if query and len(query) >= 2:
        # Search for users by username
        users = User.objects.filter(
            username__icontains=query
        ).exclude(
            id=request.user.id  # Exclude current user
        )[:10]  # Limit results
        
        # Add friendship status to each user
        for user in users:
            user.is_friend = Friendship.are_friends(request.user, user)
            user.has_pending_request = FriendRequest.objects.filter(
                from_user=request.user,
                to_user=user,
                status='pending'
            ).exists()
            user.has_received_request = FriendRequest.objects.filter(
                from_user=user,
                to_user=request.user,
                status='pending'
            ).exists()
    
    context = {
        'users': users,
        'query': query,
    }
    return render(request, 'movies/search_users.html', context)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def send_friend_request(request, user_id):
    """Send a friend request to another user"""
    try:
        to_user = get_object_or_404(User, id=user_id)
        
        # Check if they're already friends
        if Friendship.are_friends(request.user, to_user):
            return JsonResponse({'error': 'You are already friends with this user'}, status=400)
        
        # Check if request already exists
        existing_request = FriendRequest.objects.filter(
            from_user=request.user,
            to_user=to_user,
            status='pending'
        ).first()
        
        if existing_request:
            return JsonResponse({'error': 'Friend request already sent'}, status=400)
        
        # Check if reverse request exists
        reverse_request = FriendRequest.objects.filter(
            from_user=to_user,
            to_user=request.user,
            status='pending'
        ).first()
        
        if reverse_request:
            # Auto-accept if they also want to be friends
            reverse_request.accept()
            return JsonResponse({
                'success': True,
                'message': f'You are now friends with {to_user.username}!',
                'status': 'friends'
            })
        
        # Get message from request
        data = json.loads(request.body) if request.body else {}
        message = data.get('message', '')
        
        # Create friend request
        FriendRequest.objects.create(
            from_user=request.user,
            to_user=to_user,
            message=message
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Friend request sent to {to_user.username}',
            'status': 'pending'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def respond_friend_request(request, request_id):
    """Accept or decline a friend request"""
    try:
        friend_request = get_object_or_404(
            FriendRequest, 
            id=request_id, 
            to_user=request.user,
            status='pending'
        )
        
        data = json.loads(request.body)
        action = data.get('action')
        
        if action == 'accept':
            success = friend_request.accept()
            if success:
                return JsonResponse({
                    'success': True,
                    'message': f'You are now friends with {friend_request.from_user.username}!'
                })
        elif action == 'decline':
            success = friend_request.decline()
            if success:
                return JsonResponse({
                    'success': True,
                    'message': 'Friend request declined'
                })
        
        return JsonResponse({'error': 'Invalid action'}, status=400)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def remove_friend(request, user_id):
    """Remove a friend"""
    try:
        friend = get_object_or_404(User, id=user_id)
        
        # Find and delete the friendship
        friendship = Friendship.objects.filter(
            Q(user1=request.user, user2=friend) | Q(user1=friend, user2=request.user)
        ).first()
        
        if friendship:
            friendship.delete()
            return JsonResponse({
                'success': True,
                'message': f'Removed {friend.username} from friends'
            })
        else:
            return JsonResponse({'error': 'Not friends with this user'}, status=400)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Challenge Views
@login_required
def challenge_detail(request, challenge_id):
    """View and interact with a specific challenge"""
    challenge = get_object_or_404(Challenge, id=challenge_id)
    
    # Check if user is part of this challenge
    if request.user not in [challenge.challenger, challenge.challenged]:
        messages.error(request, "You don't have access to this challenge")
        return redirect('movies:home')
    
    # Determine if current user is challenger or challenged
    is_challenger = request.user == challenge.challenger
    user_movie = challenge.challenger_movie if is_challenger else challenge.challenged_movie
    opponent_movie = challenge.challenged_movie if is_challenger else challenge.challenger_movie
    opponent = challenge.challenged if is_challenger else challenge.challenger
    
    context = {
        'challenge': challenge,
        'is_challenger': is_challenger,
        'user_movie': user_movie,
        'opponent_movie': opponent_movie,
        'opponent': opponent,
        'can_select_movie': not user_movie
    }
    
    return render(request, 'movies/challenge_detail.html', context)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def select_challenge_movie(request, challenge_id):
    """Select a movie for a challenge"""
    try:
        challenge = get_object_or_404(Challenge, id=challenge_id)
        
        # Check if user is part of this challenge
        if request.user not in [challenge.challenger, challenge.challenged]:
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        data = json.loads(request.body)
        movie_id = data.get('movie_id')
        movie = get_object_or_404(Movie, id=movie_id)
        
        # Update the appropriate movie field (allow changing selection)
        if request.user == challenge.challenger:
            challenge.challenger_movie = movie
        else:
            challenge.challenged_movie = movie
        
        challenge.save()
        
        return JsonResponse({
            'success': True,
            'movie_title': movie.title,
            'ready_for_game': challenge.is_ready_for_game
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def create_challenge(request, user_id):
    """Create a new challenge with another user"""
    try:
        challenged_user = get_object_or_404(User, id=user_id)
        
        # Check if they're friends
        if not Friendship.are_friends(request.user, challenged_user):
            return JsonResponse({'error': 'You can only challenge friends'}, status=400)
        
        # Check if challenge already exists
        existing_challenge = Challenge.objects.filter(
            Q(challenger=request.user, challenged=challenged_user) |
            Q(challenger=challenged_user, challenged=request.user),
            status='active'
        ).first()
        
        if existing_challenge:
            return JsonResponse({'error': 'Active challenge already exists with this user'}, status=400)
        
        # Create challenge
        challenge = Challenge.objects.create(
            challenger=request.user,
            challenged=challenged_user
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Challenge sent to {challenged_user.username}!',
            'challenge_id': str(challenge.id)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def cancel_challenge(request, challenge_id):
    """Cancel an active challenge"""
    try:
        challenge = get_object_or_404(Challenge, id=challenge_id)
        
        # Check if user is part of this challenge
        if request.user not in [challenge.challenger, challenge.challenged]:
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        # Check if challenge can be cancelled (only active challenges)
        if challenge.status != 'active':
            return JsonResponse({'error': 'This challenge cannot be cancelled'}, status=400)
        
        # Update challenge status to cancelled
        challenge.status = 'cancelled'
        challenge.save()
        
        # Also cancel any associated games
        associated_games = Game.objects.filter(challenge=challenge, is_active=True)
        for game in associated_games:
            game.is_active = False
            game.ended_at = timezone.now()
            game.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Challenge cancelled successfully'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)