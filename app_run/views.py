from rest_framework.decorators import api_view
from rest_framework.response import Response

from project_run.settings import base


@api_view(['GET'])
def company_details(request):
    detail = {
            'company_name': base.COMPANY_NAME,
            'slogan': base.SLOGAN,
            'contacts': base.CONTACTS
        }
    return Response(detail)
