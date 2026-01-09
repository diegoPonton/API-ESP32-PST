from django.contrib import admin
from django.urls import path
from rest_framework.response import Response
from rest_framework.views import APIView

from telemetry.views import telemetry_ingest, last_location_view, last_telemetry_view


class HealthView(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self, request):
        return Response({"status": "ok"})

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", HealthView.as_view()),

    # API pública de lectura:
    path("api/v1/last-location/<str:device_id>/", last_location_view),

    # API de ingreso (protegida con token Bearer):
    path("api/v1/telemetry/", telemetry_ingest),

    path("api/v1/last-telemetry/<str:device_id>/", last_telemetry_view),

]
