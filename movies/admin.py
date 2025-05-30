from django.contrib import admin
from .models import Movie, MovieList, MovieRating, Game, GameResult, Challenge, Friendship, FriendRequest

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_date', 'vote_average', 'created_at')
    search_fields = ('title', 'overview')
    list_filter = ('release_date', 'vote_average')

@admin.register(MovieList)
class MovieListAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at')
    search_fields = ('name', 'user__username')

@admin.register(MovieRating)
class MovieRatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('challenge', 'movie', 'game_type', 'created_by', 'is_active', 'created_at')
    list_filter = ('game_type', 'is_active', 'created_at')

@admin.register(GameResult)
class GameResultAdmin(admin.ModelAdmin):
    list_display = ('game', 'player', 'score', 'completed_at')
    list_filter = ('completed_at',)

@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('challenger', 'challenged', 'status', 'winner', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('challenger__username', 'challenged__username')

@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('user1', 'user2', 'created_at')
    search_fields = ('user1__username', 'user2__username')

@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('from_user__username', 'to_user__username')
