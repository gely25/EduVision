from django.urls import path
from api import views_object_game

urlpatterns = [
    # 🌱 Intro y vistas informativas
    path("intro/", views_object_game.intro_view, name="intro_view"),
    path("instructions/", views_object_game.instructions_view, name="instructions_view"),
    path("rules/", views_object_game.rules_view, name="rules_view"),
    path("camera-test/", views_object_game.camera_test_view, name="camera_test_view"),

    # 🎮 Flujo del juego
    path("start/", views_object_game.start_view, name="start_view"),
    path("play/", views_object_game.play_view, name="play_view"),
    path("detect/", views_object_game.detectar_objeto, name="detectar_objeto"),
    path("result/", views_object_game.result_view, name="result_view"),
    path("update-score/", views_object_game.update_score_view, name="update_score_view")
]
