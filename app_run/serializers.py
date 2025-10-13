from pprint import pprint
from geopy import distance as d
from django.contrib.auth.models import User
from rest_framework import serializers

from app_run.models import Run, AthleteInfo, Challenge, Position, CollectibleItem


class UserSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    runs_finished = serializers.SerializerMethodField()

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

    def get_runs_finished(self, obj):
        return User.objects.filter(run__athlete=obj, run__status='finished').count()


class AthleteSerializer(serializers.ModelSerializer):
    athlete_data = UserSerializer(read_only=True, source='athlete')

    # distance = serializers.SerializerMethodField()

    class Meta:
        model = Run
        # fields = ['id', 'created_at', 'athlete', 'comment', 'status', 'athlete_data', 'distance']
        fields = '__all__'

    def create(self, validated_data):
        status = Run.objects.create(status='init', **validated_data)
        return status

    # def get_distance(self, obj):
    #     positions = Position.objects.filter(run=obj.id)
    #     point_run = []
    #     for i in positions:
    #         if len(positions) < 2:
    #             continue
    #         point_run.append((i.latitude, i.longitude))
    #     point_run_tuple = point_run
    #     distance = d.distance(*point_run_tuple).km
    #     return distance


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
    class Meta:
        model = Position
        fields = '__all__'

    def validate(self, validated_data):
        pprint(validated_data)
        if validated_data['run'].status != 'in_progress':
            raise serializers.ValidationError("Забег должен быть запущен")
        return validated_data

        return

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
        fields = '__all__'

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
