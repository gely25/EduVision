from django.urls import path
from api import views_dashboard, views_vision

urlpatterns = [
    path("tm/live/", views_vision.tm_live_view, name="tm_live_view"),
    path("tm/start/", views_vision.start_tm_camera_view, name="start_tm_camera"),
    path("tm/stop/", views_vision.stop_tm_camera_view, name="stop_tm_camera"),
    path("tm/frame/", views_vision.tm_frame_view, name="tm_frame"),
    path("dashboard/", views_dashboard.dashboard_view, name="dashboard"),
]
