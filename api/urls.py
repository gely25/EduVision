from django.urls import path, include

from api import views_auth, views_home

urlpatterns = [
    path("vision/", include("api.urls_vision")),          
    path("flashcards/", include("api.urls_flashcards")),  
    path("object_game/", include("api.urls_object_game")),
    path("signup/", views_auth.signup_view, name="signup"),
    
     
]
