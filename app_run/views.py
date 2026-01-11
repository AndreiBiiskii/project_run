import datetime
import io
from django.db.models import Sum, Max, Min
from django_filters.rest_framework import DjangoFilterBackend
from openpyxl import load_workbook
from rest_framework.decorators import api_view, action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.views import APIView
from urllib3 import request

from app_run.serializers import *
from project_run.settings import base
from geopy import distance as d


@api_view(['GET'])
def company_details(request):
    detail = {
        'company_name': base.COMPANY_NAME,
        'slogan': base.SLOGAN,
        'contacts': base.CONTACTS
    }
    return Response(detail)


class StandardResultsSetPagination(PageNumberPagination):
    page_size_query_param = 'size'


class RunAPIView(viewsets.ModelViewSet):
    queryset = Run.objects.select_related('athlete').all().annotate(full_distance=Sum('distance'))
    serializer_class = AthleteSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]  # Указываем какой класс будет использоваться для фильтра
    filterset_fields = ['status', 'athlete']
    ordering_fields = ['created_at', ]
    # full_distance = Run.objects.filter(athlete_id=queryset.athlete.id).aggregate(Sum('distance'))


class UsersByTypeAPIView(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.exclude(is_superuser=True).annotate(
        runs_finished=Count('run__status', filter=Q(run__status='finished')))
    serializer_class = UserSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['first_name', 'last_name']
    ordering_fields = ['date_joined', ]
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action == 'list':
            return UserSerializer
        if self.action == 'retrieve':
            return UserItemsSerializer
        return self.serializer_class

    # api/users/?type=athlete&ordering=date_joined&size=1
    def get_queryset(self):
        qs = self.queryset
        user_by_type = self.request.query_params.get('type', None)
        if user_by_type is not None:
            if user_by_type == 'coach':
                qs = qs.filter(is_staff=True)
            if user_by_type == 'athlete':
                qs = qs.filter(is_staff=False)

        return qs


class StartRunAPIView(APIView):
    def post(self, request, run_id=None):
        queryset = Run.objects.all()
        run = get_object_or_404(queryset, pk=run_id)
        if run.status == 'in_progress' or run.status == 'finished':
            return Response({'error': 'run in_progress or run finished', 'current_status': run.status},
                            status=status.HTTP_400_BAD_REQUEST)
        run.status = 'in_progress'
        run.save()
        serializer = AthleteSerializer(run)
        return Response(serializer.data)


class StopRunAPIView(APIView):
    def post(self, request, run_id=None):
        queryset = Run.objects.all()
        run = get_object_or_404(queryset, pk=run_id)
        if run.status != 'in_progress' or run.status == 'finished':
            return Response({'error': 'run not in_progress or finished ', 'current_status': run.status},
                            status=status.HTTP_400_BAD_REQUEST)
        positions = Position.objects.filter(run_id=run.id)
        point_run = []
        for i in positions:
            if len(positions) < 2:
                continue
            point_run.append((i.latitude, i.longitude))
        point_run_tuple = point_run
        distance = d.distance(*point_run_tuple).km
        run.distance = distance
        run.status = 'finished'
        run.save()
        result = positions.filter(run=run_id).aggregate(max_value=Max('date_time'), min_value=Min('date_time'))
        if result:
            try:
                time_difference = (result['max_value'] - result['min_value']).total_seconds()
            except:
                return Response({'error': 'Забег не успел начаться)'})
            run.run_time_seconds = time_difference
            run.save()
            print(result['max_value'], '\n', result['min_value'])
        run_count = Run.objects.filter(athlete_id=run.athlete.id, status='finished').count()
        if run_count == 10:
            Challenge.objects.create(full_name='Сделай 10 Забегов!', athlete_id=run.athlete.id)
        full_distance = Run.objects.filter(athlete_id=run.athlete.id).aggregate(Sum('distance'))
        print('******', full_distance)

        if full_distance['distance__sum'] >= 50:
            Challenge.objects.create(full_name='Пробеги 50 километров!', athlete_id=run.athlete.id)
        final_speed = run.position_set.aggregate(Avg('speed'))
        f_speed = run.position_set.last()
        f_speed.speed = final_speed['speed__avg']
        f_speed.save()
        serializer = AthleteSerializer(run)
        return Response(serializer.data)


class ChallengeAPIView(viewsets.ReadOnlyModelViewSet):
    queryset = Challenge.objects.all()
    serializer_class = ChallengeSerializer

    def get_queryset(self):
        qs = self.queryset
        athlete = self.request.query_params.get('athlete')
        if athlete:
            qs = qs.filter(athlete_id=athlete)
        return qs


class AthleteInfoAPIView(APIView):
    def get(self, request, user_id):
        try:
            objects, result = AthleteInfo.objects.get_or_create(athlete_id=user_id)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = AthleteInfoSerializer(objects)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, user_id):
        goals = request.data.get('goals', '')
        weight = request.data.get('weight', -1)
        if type(weight) == str:
            if weight.isdigit():
                weight = int(request.data.get('weight', '-1'))
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        if (weight != -1) and ((weight <= 0) or (weight >= 900)):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if (weight != -1) and (goals != ''):
            try:
                objects, result = AthleteInfo.objects.update_or_create(
                    athlete_id=user_id,
                    defaults={
                        'weight': weight,
                        'goals': goals
                    }
                )
                serializer = AthleteInfoSerializer(objects)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except:
                return Response(status=status.HTTP_404_NOT_FOUND)

        if (weight != -1) and (goals == ''):
            print(2)
            try:
                objects, result = AthleteInfo.objects.update_or_create(
                    athlete_id=user_id,
                    defaults={
                        'weight': weight,
                    }
                )
                serializer = AthleteInfoSerializer(objects)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except:
                return Response(status=status.HTTP_404_NOT_FOUND)

        if (weight == -1) and (goals != ''):
            try:
                objects, result = AthleteInfo.objects.update_or_create(
                    athlete_id=user_id,
                    defaults={
                        'goals': goals
                    }
                )
                serializer = AthleteInfoSerializer(objects)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except:
                return Response(status=status.HTTP_404_NOT_FOUND)
        try:
            objects, result = AthleteInfo.objects.get_or_create(athlete_id=user_id)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = AthleteInfoSerializer(objects)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PositionAPIView(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer

    def get_queryset(self):
        qs = self.queryset
        run_id = self.request.query_params.get('run', None)
        if run_id:
            qs = qs.filter(run_id=run_id)
        return qs

    def create(self, request, *args, **kwargs):
        try:
            last_position = Position.objects.filter(run_id=request.data['run']).last()
        except:
            response = super().create(request, *args, **kwargs)
            return Response({"data": response.data},
                            status=response.status_code)
        # if last_position is None:
        #     response = super().create(request, *args, **kwargs)
        #     return Response({"data": response.data},
        #                     status=response.status_code)
        current_distance = d.distance((last_position.latitude, last_position.longitude),
                                      (request.data['latitude'], request.data['longitude'])).km
        speed_point = (current_distance * 1000) / (
            (datetime.datetime.now() - last_position.date_time).total_seconds())
        request.data['distance'] = round(current_distance + last_position.distance, 2)
        request.data['speed'] = round(speed_point, 2)
        print(last_position.date_time, datetime.datetime.now())
        response = super().create(request, *args, **kwargs)
        return Response({"data": response.data},
                        status=response.status_code)


class CollectibleItemAPIView(viewsets.ReadOnlyModelViewSet):
    queryset = CollectibleItem.objects.all()
    serializer_class = CollectibleItemSerializer


class UploadFileAPIView(APIView):
    def post(self, request):
        uploaded_file = request.FILES.get('file')
        # file_path = default_storage.save(uploaded_file.name, uploaded_file) сохранение файла
        file_content = uploaded_file.read()
        file_stream = io.BytesIO(file_content)
        wb = load_workbook(file_stream)
        ws = wb.active
        error = []
        for row in ws.values:
            if row[0] == 'Name':
                continue
            data = {
                'name': row[0],
                'uid': row[1],
                'value': row[2],
                'latitude': row[3],
                'longitude': row[4],
                'picture': row[5],
            }
            serializer = CollectibleItemSerializer(data=data)
            if serializer.is_valid():
                CollectibleItem.objects.create(**serializer.validated_data)
            else:
                error.append(list(data.values()))
        # os.remove(file_path) удаление файла
        return Response(error)
