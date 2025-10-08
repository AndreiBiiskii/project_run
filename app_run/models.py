from django.contrib.auth.models import User
from django.db import models

from project_run.settings.base import CHOICES_STATUS


class Run(models.Model):
    create_at = models.DateTimeField(auto_now_add=True)
    athlete = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    status = models.CharField(choices=CHOICES_STATUS, default=False)

    def __str__(self):
        return self.athlete.username
