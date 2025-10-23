from django.urls import path, include

urlpatterns = [
    path("vision/", include("api.urls_vision")),          
    path("flashcards/", include("api.urls_flashcards")),  
    path("object_game/", include("api.urls_object_game")) 
]
