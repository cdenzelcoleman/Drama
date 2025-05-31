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
    return game_play(request, game_id, 'taps')

@login_required
def shake_index(request):
    shake_games = Game.objects.filter(game_type='shake', is_active=True).order_by('-created_at')
    return render(request, 'games/shake/index.html', {'games': shake_games})

@login_required
def shake_detail(request, game_id):
    return game_detail(request, game_id, 'shake')

@login_required
def shake_play(request, game_id):
    return game_play(request, game_id, 'shake')

@login_required
def create_game(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        game_type = request.POST.get('game_type')
        description = request.POST.get('description', '')
        
        if name and game_type in ['taps', 'shake']:
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