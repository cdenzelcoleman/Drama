from django.shortcuts import render
from django.http import HttpResponse

def taps_index(request):
    return HttpResponse("Taps Game Index")

def taps_detail(request, game_id):
    return HttpResponse(f"Taps Game Detail for game {game_id}")

def taps_play(request, game_id):
    return HttpResponse(f"Playing Taps Game {game_id}")

def shake_index(request):
    return HttpResponse("Shake Game Index")

def shake_detail(request, game_id):
    return HttpResponse(f"Shake Game Detail for game {game_id}")

def shake_play(request, game_id):
    return HttpResponse(f"Playing Shake Game {game_id}")
