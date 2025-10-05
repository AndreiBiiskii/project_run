from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets

from app_run.models import Run
from app_run.serializers import AthleteSerializer
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
    queryset = Run.objects.all()
    serializer_class = AthleteSerializer
