from django.contrib.auth.models import User
from rest_framework import serializers

from app_run.models import Run


class UserSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'last_name', 'first_name', 'date_joined', 'type']

    def get_type(self, obj):
        text = ''
        if not obj.is_staff:
            text = 'athlete'
        if obj.is_staff:
            text = 'coach'
        return text


class AthleteSerializer(serializers.ModelSerializer):
    athlete_data = UserSerializer(read_only=True, source='athlete')

    class Meta:
        model = Run
        fields = '__all__'

    def create(self, validated_data):
        status = Run.objects.create(status='init', **validated_data)
        return status
