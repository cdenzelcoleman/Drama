from django.db import models
from django.contrib.auth.models import User
import uuid

class Movie(models.Model):
    tmdb_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=255)
    overview = models.TextField(blank=True)
    poster_path = models.CharField(max_length=255, blank=True)
    backdrop_path = models.CharField(max_length=255, blank=True)
    release_date = models.DateField(null=True, blank=True)
    vote_average = models.FloatField(default=0.0)
    vote_count = models.IntegerField(default=0)
    genre_ids = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    @property
    def poster_url(self):
        if self.poster_path:
            return f"https://image.tmdb.org/t/p/w500{self.poster_path}"
        return None
    
    @property
    def backdrop_url(self):
        if self.backdrop_path:
            return f"https://image.tmdb.org/t/p/w1280{self.backdrop_path}"
        return None

class MovieList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='movie_lists')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    movies = models.ManyToManyField(Movie, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s {self.name}"

class MovieRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'movie')
    
    def __str__(self):
        return f"{self.user.username} rated {self.movie.title}: {self.rating}/5"

class Game(models.Model):
    GAME_TYPES = [
        ('taps', 'Taps'),
        ('shake', 'Shake'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    challenge = models.ForeignKey('Challenge', on_delete=models.CASCADE, related_name='games')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='games')
    game_type = models.CharField(max_length=10, choices=GAME_TYPES)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_movie_games')
    is_active = models.BooleanField(default=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_game_type_display()} for {self.movie.title} in Challenge: {self.challenge.challenger.username} vs {self.challenge.challenged.username}"

class GameResult(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='results')
    player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='game_results')
    score = models.IntegerField()
    completed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('game', 'player')
    
    def __str__(self):
        return f"{self.player.username}: {self.score} in {self.game}"

class Friendship(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friendships_initiated')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friendships_received')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user1', 'user2')
        constraints = [
            models.CheckConstraint(
                check=~models.Q(user1=models.F('user2')),
                name='friendship_no_self_friendship'
            )
        ]
    
    def __str__(self):
        return f"{self.user1.username} ↔ {self.user2.username}"
    
    @classmethod
    def are_friends(cls, user1, user2):
        """Check if two users are friends"""
        return cls.objects.filter(
            models.Q(user1=user1, user2=user2) | models.Q(user1=user2, user2=user1)
        ).exists()
    
    @classmethod
    def get_friends(cls, user):
        """Get all friends of a user"""
        friendships = cls.objects.filter(
            models.Q(user1=user) | models.Q(user2=user)
        ).select_related('user1', 'user2')
        
        friends = []
        for friendship in friendships:
            if friendship.user1 == user:
                friends.append(friendship.user2)
            else:
                friends.append(friendship.user1)
        return friends

class Challenge(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('waiting_for_movie', 'Waiting for Movie Selection'),
        ('waiting_for_game', 'Waiting for Game Selection'),
        ('ready_to_play', 'Ready to Play'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    GAME_TYPE_CHOICES = [
        ('taps', 'Taps'),
        ('shake', 'Shake'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    challenger = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_challenges')
    challenged = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_challenges')
    challenger_movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='challenger_selections', null=True, blank=True)
    challenged_movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='challenged_selections', null=True, blank=True)
    challenger_game_type = models.CharField(max_length=10, choices=GAME_TYPE_CHOICES, null=True, blank=True)
    challenged_game_type = models.CharField(max_length=10, choices=GAME_TYPE_CHOICES, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='won_challenges', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~models.Q(challenger=models.F('challenged')),
                name='challenge_no_self_challenge'
            )
        ]
    
    def __str__(self):
        return f"{self.challenger.username} vs {self.challenged.username} ({self.status})"
    
    @property
    def both_movies_selected(self):
        return self.challenger_movie and self.challenged_movie
    
    @property
    def both_game_types_selected(self):
        return self.challenger_game_type and self.challenged_game_type
    
    @property
    def game_types_match(self):
        return (self.challenger_game_type and self.challenged_game_type and 
                self.challenger_game_type == self.challenged_game_type)
    
    @property
    def is_ready_for_game_selection(self):
        return self.status == 'active' and self.both_movies_selected and not self.both_game_types_selected
    
    @property
    def is_ready_to_play(self):
        return (self.status in ['active', 'ready_to_play'] and self.both_movies_selected and 
                self.both_game_types_selected and self.game_types_match)

class FriendRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]
    
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_friend_requests')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_friend_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(blank=True, max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('from_user', 'to_user')
        constraints = [
            models.CheckConstraint(
                check=~models.Q(from_user=models.F('to_user')),
                name='friend_request_no_self_request'
            )
        ]
    
    def __str__(self):
        return f"{self.from_user.username} → {self.to_user.username} ({self.status})"
    
    def accept(self):
        """Accept the friend request and create friendship"""
        if self.status == 'pending':
            self.status = 'accepted'
            self.save()
            
            # Create friendship (ensure consistent ordering)
            user1, user2 = sorted([self.from_user, self.to_user], key=lambda u: u.id)
            Friendship.objects.get_or_create(user1=user1, user2=user2)
            return True
        return False
    
    def decline(self):
        """Decline the friend request"""
        if self.status == 'pending':
            self.status = 'declined'
            self.save()
            return True
        return False
