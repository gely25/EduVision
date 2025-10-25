from django.urls import path, include

from api import views_auth, views_dashboard, views_home

urlpatterns = [
    path("vision/", include("api.urls_vision")),          
    path("flashcards/", include("api.urls_flashcards")),  
    path("object_game/", include("api.urls_object_game")),
    path("signup/", views_auth.signup_view, name="signup"),
    path("dashboard/", views_dashboard.dashboard_view, name="dashboard"),
    path("dashboard/summary/", views_dashboard.dashboard_summary_api, name="dashboard_summary_api"),

    
     
]
