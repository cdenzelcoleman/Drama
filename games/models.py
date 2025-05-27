from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Game(models.Model):
    GAME_TYPES = [
        ('taps', 'Taps Game'),
        ('shake', 'Shake Game'),
    ]
    
    name = models.CharField(max_length=100)
    game_type = models.CharField(max_length=20, choices=GAME_TYPES)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_games')
    participants = models.ManyToManyField(User, through='GameParticipant', related_name='games')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_game_type_display()})"

class GameParticipant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('user', 'game')
    
    def __str__(self):
        return f"{self.user.username} in {self.game.name}"

class GameResult(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='results')
    participant = models.ForeignKey(GameParticipant, on_delete=models.CASCADE)
    score = models.IntegerField()
    rank = models.IntegerField(null=True, blank=True)
    completed_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField(default=dict)
    
    class Meta:
        ordering = ['-score', 'completed_at']
    
    def __str__(self):
        return f"{self.participant.user.username} - {self.game.name}: {self.score}"
