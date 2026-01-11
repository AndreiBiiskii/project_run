import datetime
from django.contrib.auth.models import User
from django.db import models

from project_run.settings.base import CHOICES_STATUS


class Run(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    athlete = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    status = models.CharField(choices=CHOICES_STATUS, default=False)
    distance = models.FloatField(blank=True, null=True)
    run_time_seconds = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.athlete.username


class AthleteInfo(models.Model):
    goals = models.CharField(max_length=255, blank=True, null=True)
    weight = models.SmallIntegerField(blank=True, null=True)
    athlete = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.athlete.username


class Challenge(models.Model):
    full_name = models.CharField(max_length=100)
    athlete = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.full_name


class Position(models.Model):
    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    date_time = models.DateTimeField(auto_now_add=True)
    speed = models.FloatField(default=0.0)
    distance = models.FloatField(default=0.0)


class CollectibleItem(models.Model):
    name = models.CharField(max_length=100)
    uid = models.CharField(max_length=50)
    latitude = models.FloatField()
    longitude = models.FloatField()
    picture = models.URLField()
    value = models.IntegerField()
    athlete = models.ManyToManyField(User, related_name='items')
