from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta

class UserTime(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='time')
    remaining_time = models.DurationField(default=timedelta(minutes=0))

    def add_time(self, minutes):
        self.remaining_time += timedelta(minutes=minutes)
        self.save()

    def reduce_time(self, minutes):
        self.remaining_time -= timedelta(minutes=minutes)
        self.save()

    def __str__(self):
        return f"{self.user.username}: {self.remaining_time}"
