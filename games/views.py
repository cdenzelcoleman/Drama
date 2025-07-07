from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import Game, GameParticipant, GameResult
import json

def index(request):
    games = Game.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'games/index.html', {'games': games})

@login_required
def taps_index(request):
    taps_games = Game.objects.filter(game_type='taps', is_active=True).order_by('-created_at')
    return render(request, 'games/taps/index.html', {'games': taps_games})

@login_required
def game_detail(request, game_id, game_type):
    game = get_object_or_404(Game, id=game_id, game_type=game_type)
    participant, _ = GameParticipant.objects.get_or_create(
        user=request.user,
        game=game
    )
    
    leaderboard = GameResult.objects.filter(game=game).order_by('-score')[:10]
    
    template_name = f'games/{game_type}/detail.html'
    return render(request, template_name, {
        'game': game,
        'participant': participant,
        'leaderboard': leaderboard
    })

@login_required
def taps_detail(request, game_id):
    return game_detail(request, game_id, 'taps')

@login_required
def game_play(request, game_id, game_type):
    game = get_object_or_404(Game, id=game_id, game_type=game_type)
    participant, _ = GameParticipant.objects.get_or_create(
        user=request.user,
        game=game
    )
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            score = int(data.get('score', 0))
            game_data = data.get(game_type, [])
            
            participant.score = max(participant.score, score)
            participant.completed_at = timezone.now()
            participant.save()
            
            GameResult.objects.create(
                game=game,
                participant=participant,
                score=score,
                data={game_type: game_data, 'timestamp': timezone.now().isoformat()}
            )
            
            return JsonResponse({'success': True, 'score': score})
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({'success': False, 'error': 'Invalid data'})
    
    template_name = f'games/{game_type}/play.html'
    return render(request, template_name, {
        'game': game,
        'participant': participant
    })

@login_required
def taps_play(request, game_id):
    game = get_object_or_404(Game, id=game_id, game_type='taps')
    participant, _ = GameParticipant.objects.get_or_create(
        user=request.user,
        game=game
    )
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            score = int(data.get('score', 0))
            taps_data = data.get('taps', {})
            
            participant.score = max(participant.score, score)
            participant.completed_at = timezone.now()
            participant.save()
            
            GameResult.objects.create(
                game=game,
                participant=participant,
                score=score,
                data={'taps': taps_data, 'timestamp': timezone.now().isoformat()}
            )
            
            return JsonResponse({'success': True, 'score': score})
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({'success': False, 'error': 'Invalid data'})
    
    return render(request, 'games/taps/play_simple.html', {
        'game': game,
        'participant': participant
    })

@login_required
def connect_four_index(request):
    connect_four_games = Game.objects.filter(game_type='connect_four', is_active=True).order_by('-created_at')
    return render(request, 'games/connect_four/index.html', {'games': connect_four_games})

@login_required
def connect_four_detail(request, game_id):
    game = get_object_or_404(Game, id=game_id, game_type='connect_four')
    
    # Get user's best result if authenticated
    user_best_result = None
    if request.user.is_authenticated:
        user_results = GameResult.objects.filter(
            game=game, 
            participant__user=request.user
        ).order_by('-score', '-created_at')
        if user_results.exists():
            user_best_result = user_results.first()
    
    # Get recent results for display
    recent_results = GameResult.objects.filter(game=game).order_by('-created_at')[:6]
    
    return render(request, 'games/connect_four/detail.html', {
        'game': game,
        'user_best_result': user_best_result,
        'recent_results': recent_results
    })

@login_required
def connect_four_play(request, game_id):
    game = get_object_or_404(Game, id=game_id, game_type='connect_four')
    participant, _ = GameParticipant.objects.get_or_create(
        user=request.user,
        game=game
    )
    
    # Check for existing result
    existing_result = GameResult.objects.filter(
        game=game, 
        participant=participant
    ).order_by('-created_at').first()
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            score = int(data.get('score', 0))  # 1 for win, 0 for loss/draw
            moves = int(data.get('moves', 0))
            duration = int(data.get('duration', 0))
            result_type = data.get('result', 'draw')
            
            # Update participant score (track wins)
            if score == 1:
                participant.score = participant.score + 1
            participant.completed_at = timezone.now()
            participant.save()
            
            # Create game result
            GameResult.objects.create(
                game=game,
                participant=participant,
                score=score,
                data={
                    'moves': moves,
                    'duration': duration,
                    'result': result_type,
                    'timestamp': timezone.now().isoformat()
                }
            )
            
            return JsonResponse({'success': True, 'score': score})
        except (json.JSONDecodeError, ValueError) as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return render(request, 'games/connect_four/play.html', {
        'game': game,
        'participant': participant,
        'existing_result': existing_result
    })

@login_required
def create_game(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        game_type = request.POST.get('game_type')
        description = request.POST.get('description', '')
        
        if name and game_type in ['taps', 'connect_four']:
            game = Game.objects.create(
                name=name,
                game_type=game_type,
                description=description,
                created_by=request.user
            )
            messages.success(request, f'Game "{name}" created successfully!')
            return redirect('games:detail', game_id=game.id)
        else:
            messages.error(request, 'Please provide valid game details.')
    
    return render(request, 'games/create.html')