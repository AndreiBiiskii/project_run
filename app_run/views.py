from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets, filters
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


class AthleteAPIView(viewsets.ModelViewSet):
    queryset = Run.objects.select_related('athlete').all().order_by('create_at')
    serializer_class = AthleteSerializer


class UsersByTypeAPIView(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.exclude(is_superuser=True)
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['first_name', 'last_name']

    def get_queryset(self):
        qs = self.queryset
        user_by_type = self.request.query_params.get('type', None)
        if user_by_type is not None:
            if user_by_type == 'coach':
                qs = qs.filter(is_staff=True)
            if user_by_type == 'athlete':
                qs = qs.filter(is_staff=False)
        return qs
