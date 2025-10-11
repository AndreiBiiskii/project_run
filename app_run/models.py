from botocore.endpoint_provider import TreeRule
from django.contrib.auth.models import User
from django.db import models

from project_run.settings.base import CHOICES_STATUS


class Run(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    athlete = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    status = models.CharField(choices=CHOICES_STATUS, default=False)

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
