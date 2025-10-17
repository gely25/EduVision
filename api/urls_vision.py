from django.urls import path
from . import views_vision




urlpatterns = [
    path("vision/live/", views_vision.live_view, name="live_view"),
    path("vision/start/", views_vision.start_camera_view, name="start_camera"),
    path("vision/stop/", views_vision.stop_camera_view, name="stop_camera"),
    path("vision/objects/", views_vision.objects_view, name="objects_view"),
    path("vision/frame/", views_vision.get_frame_view, name="frame_view"),  # 👈 ESTE ENDPOINT ES CLAVE
    path("vision/detect/", views_vision.DetectView.as_view(), name="detect"),
]
