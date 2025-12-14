# core/urls.py
from django.contrib import admin
from django.urls import path
from telemetry.views import telemetry_ingest, last_location_view
from rest_framework.response import Response
from rest_framework.views import APIView

class HealthView(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self, request):
        return Response({"status": "ok"})

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", HealthView.as_view()),
    path("api/v1/telemetry/", telemetry_ingest),  # POST
    path("api/v1/last-location/<str:device_id>/", last_location_view),  # GET
]
