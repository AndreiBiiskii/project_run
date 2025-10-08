from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import viewsets, filters, status
from rest_framework.views import APIView

from app_run.serializers import *
from project_run.settings import base


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
    queryset = Run.objects.select_related('athlete').all()
    serializer_class = AthleteSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]  # Указываем какой класс будет использоваться для фильтра
    filterset_fields = ['status', 'athlete']
    ordering_fields = ['created_at', ]


class UsersByTypeAPIView(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.exclude(is_superuser=True)
    serializer_class = UserSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['first_name', 'last_name']
    pagination_class = StandardResultsSetPagination
    ordering_fields = ['date_joined', ]

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
        run.status = 'finished'
        run.save()
        serializer = AthleteSerializer(run)
        return Response(serializer.data)
