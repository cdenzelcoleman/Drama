from django.contrib import admin
from .models import Movie, MovieList, MovieRating, Room, RoomMembership, Game, GameResult

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

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'is_active', 'created_at')
    search_fields = ('name', 'owner__username')
    list_filter = ('is_active', 'created_at')

@admin.register(RoomMembership)
class RoomMembershipAdmin(admin.ModelAdmin):
    list_display = ('room', 'user', 'status', 'invited_at')
    list_filter = ('status', 'invited_at')

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('room', 'movie', 'game_type', 'created_by', 'is_active', 'created_at')
    list_filter = ('game_type', 'is_active', 'created_at')

@admin.register(GameResult)
class GameResultAdmin(admin.ModelAdmin):
    list_display = ('game', 'player', 'score', 'completed_at')
    list_filter = ('completed_at',)
