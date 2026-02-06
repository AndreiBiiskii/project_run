import datetime
from pprint import pprint
from django.contrib.auth.models import User
from django.db.models import Q
from django.db.models.aggregates import Count, Avg
from rest_framework import serializers
from geopy import distance as d
from app_run.models import Run, AthleteInfo, Challenge, Position, CollectibleItem


class UserSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    # runs_finished = serializers.SerializerMethodField()
    runs_finished = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'last_name', 'first_name', 'date_joined', 'type', 'runs_finished']

    def get_type(self, obj):
        text = ''
        if not obj.is_staff:
            text = 'athlete'
        if obj.is_staff:
            text = 'coach'
        return text


class AthleteSerializer(serializers.ModelSerializer):
    athlete_data = UserSerializer(read_only=True, source='athlete')

    # runs_finished = serializers.IntegerField(read_only=True)

    class Meta:
        model = Run
        # fields = ['id', 'created_at', 'athlete', 'comment', 'status', 'athlete_data', 'distance', 'runs_finished']
        fields = '__all__'
        read_only_fields = ['run_time_seconds']

    def create(self, validated_data):
        status = Run.objects.create(status='init', **validated_data)
        return status


class AthleteInfoSerializer(serializers.ModelSerializer):
    user_id = serializers.SerializerMethodField()

    class Meta:
        model = AthleteInfo
        fields = ['user_id', 'goals', 'weight']

    def get_user_id(self, obj):
        return obj.athlete.id


class ChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = '__all__'


class PositionSerializer(serializers.ModelSerializer):
    date_time = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S.%f')
    full_distance = serializers.FloatField(read_only=True)

    class Meta:
        model = Position
        fields = '__all__'

    def validate(self, validated_data):
        if validated_data['run'].status != 'in_progress':
            raise serializers.ValidationError("Забег должен быть запущен")
        collectible_items = CollectibleItem.objects.all()
        for i in collectible_items:
            if d.distance((i.latitude, i.longitude),
                          (validated_data['latitude'], validated_data['longitude'])).km <= 0.1:
                collectible_items = CollectibleItem.objects.get(id=i.id)
                athlete = User.objects.get(id=validated_data['run'].athlete.id)
                collectible_items.athlete.add(athlete)
        return validated_data

    def validate_latitude(self, value):
        if (value < -90) or (value > 90):
            raise serializers.ValidationError("Широта должна находиться в диапазоне от -90.0 до +90.0 градусов")
        return round(value, 4)

    def validate_longitude(self, value):
        if (value < -180) or (value > 180):
            raise serializers.ValidationError("Долгота должна находиться в диапазоне от -180.0 до +180.0 градусов")
        return round(value, 4)


class CollectibleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectibleItem
        fields = ['latitude', 'longitude', 'name', 'picture', 'uid', 'value']

    def validate_latitude(self, value):
        if type(value) == float:
            if (value < -90) or (value > 90):
                raise serializers.ValidationError("Широта должна находиться в диапазоне от -90.0 до +90.0 градусов")
        return round(value, 4)

    def validate_longitude(self, value):
        if type(value) == float:
            if (value < -180) or (value > 180):
                raise serializers.ValidationError("Долгота должна находиться в диапазоне от -180.0 до +180.0 градусов")
        return round(value, 4)


class UserItemsSerializer(UserSerializer):
    items = CollectibleItemSerializer(read_only=True, many=True)

    class Meta(UserSerializer.Meta):
        model = User
        fields = UserSerializer.Meta.fields + ['items', ]
