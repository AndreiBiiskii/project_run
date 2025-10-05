from django.contrib.auth.models import User
from rest_framework import serializers

from app_run.models import Run


class AthleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Run
        fields = ('athlete', 'comment')
