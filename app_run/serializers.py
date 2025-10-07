from django.contrib.auth.models import User
from rest_framework import serializers

from app_run.models import Run


# class AthleteSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Run
#         fields = ['id', 'athlete__first_name', 'create_at', 'comment']


class UserSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'date_joined', 'username', 'last_name', 'first_name', 'type']

    def get_type(self, obj):
        text = ''
        if not obj.is_staff:
            text = 'athlete'
        if obj.is_staff:
            text = 'coach'
        return text


class AthleteSerializer(serializers.ModelSerializer):
    at = UserSerializer(read_only=True, source='athlete')

    class Meta:
        model = Run
        fields = ['id', 'at',  'create_at', 'comment']
