import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Game, GameResult, Challenge

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.game_group_name = f'game_{self.game_id}'
        self.user = self.scope["user"]
        
        # Check if user is authenticated and part of this game
        if not self.user.is_authenticated:
            await self.close()
            return
            
        game = await self.get_game()
        if not game or not await self.user_can_access_game(game):
            await self.close()
            return
        
        # Join game group
        await self.channel_layer.group_add(
            self.game_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send current game state to the connecting user
        await self.send_game_state()
    
    async def disconnect(self, close_code):
        # Leave game group
        await self.channel_layer.group_discard(
            self.game_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data['type']
            
            if message_type == 'player_ready':
                await self.handle_player_ready()
            elif message_type == 'game_action':
                await self.handle_game_action(data)
            elif message_type == 'game_complete':
                await self.handle_game_complete(data)
            
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Error processing message: {str(e)}'
            }))
    
    async def handle_player_ready(self):
        """Handle when a player signals they're ready to start"""
        await self.channel_layer.group_send(
            self.game_group_name,
            {
                'type': 'player_ready_update',
                'user_id': self.user.id,
                'username': self.user.username
            }
        )
    
    async def handle_game_action(self, data):
        """Handle real-time game actions (taps, shakes, etc.)"""
        action_data = data.get('data', {})
        
        # Broadcast the action to all players in the game
        await self.channel_layer.group_send(
            self.game_group_name,
            {
                'type': 'game_action_update',
                'user_id': self.user.id,
                'username': self.user.username,
                'action': action_data.get('action'),
                'score': action_data.get('score', 0),
                'timestamp': action_data.get('timestamp')
            }
        )
    
    async def handle_game_complete(self, data):
        """Handle when a player completes the game"""
        score = data.get('score', 0)
        
        # Save the result to database
        await self.save_game_result(score)
        
        # Broadcast completion to all players
        await self.channel_layer.group_send(
            self.game_group_name,
            {
                'type': 'game_complete_update',
                'user_id': self.user.id,
                'username': self.user.username,
                'score': score
            }
        )
    
    # Group message handlers
    async def player_ready_update(self, event):
        """Send player ready update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'player_ready',
            'user_id': event['user_id'],
            'username': event['username']
        }))
    
    async def game_action_update(self, event):
        """Send game action update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'game_action',
            'user_id': event['user_id'],
            'username': event['username'],
            'action': event['action'],
            'score': event['score'],
            'timestamp': event['timestamp']
        }))
    
    async def game_complete_update(self, event):
        """Send game completion update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'game_complete',
            'user_id': event['user_id'],
            'username': event['username'],
            'score': event['score']
        }))
    
    async def game_start_countdown(self, event):
        """Send countdown update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'countdown',
            'count': event['count']
        }))
    
    async def send_game_state(self):
        """Send current game state to the user"""
        game = await self.get_game()
        players = await self.get_game_players(game)
        results = await self.get_game_results(game)
        
        await self.send(text_data=json.dumps({
            'type': 'game_state',
            'game': {
                'id': str(game.id),
                'game_type': game.game_type,
                'movie_title': game.movie.title,
                'is_active': game.is_active
            },
            'players': players,
            'results': results
        }))
    
    # Database operations
    @database_sync_to_async
    def get_game(self):
        try:
            return Game.objects.select_related('challenge', 'movie').get(id=self.game_id)
        except Game.DoesNotExist:
            return None
    
    @database_sync_to_async
    def user_can_access_game(self, game):
        """Check if user can access this game"""
        return self.user in [game.challenge.challenger, game.challenge.challenged]
    
    @database_sync_to_async
    def get_game_players(self, game):
        """Get players for this game"""
        return [
            {
                'id': game.challenge.challenger.id,
                'username': game.challenge.challenger.username
            },
            {
                'id': game.challenge.challenged.id,
                'username': game.challenge.challenged.username
            }
        ]
    
    @database_sync_to_async
    def get_game_results(self, game):
        """Get current game results"""
        results = GameResult.objects.filter(game=game).select_related('player')
        return [
            {
                'user_id': result.player.id,
                'username': result.player.username,
                'score': result.score
            }
            for result in results
        ]
    
    @database_sync_to_async
    def save_game_result(self, score):
        """Save game result to database"""
        game = Game.objects.get(id=self.game_id)
        result, created = GameResult.objects.update_or_create(
            game=game,
            player=self.user,
            defaults={'score': score}
        )
        return result