from django.urls import path
from . import views_vision


urlpatterns = [
    path("vision/tm/live/", views_vision.tm_live_view, name="tm_live_view"),
    path("vision/tm/start/", views_vision.start_tm_camera_view, name="start_tm_camera"),
    path("vision/tm/stop/", views_vision.stop_tm_camera_view, name="stop_tm_camera"),
    path("vision/tm/frame/", views_vision.tm_frame_view, name="tm_frame"),  
]
