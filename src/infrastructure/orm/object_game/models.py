from django.db import models
from django.contrib.auth.models import User


class GameSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.PositiveIntegerField(default=0)
    total_words = models.PositiveIntegerField(default=0)
    date_played = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Partida de {self.user.username} - {self.score}/{self.total_words * 10}"

    class Meta:
        app_label = "api" 