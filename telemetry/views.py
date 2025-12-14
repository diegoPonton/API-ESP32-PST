# telemetry/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .serializers import TelemetryInSerializer
from .influx import write_telemetry_and_gps, query_last_location

@api_view(["POST"])
def telemetry_ingest(request):
    s = TelemetryInSerializer(data=request.data)
    if not s.is_valid():
        return Response({"errors": s.errors}, status=status.HTTP_400_BAD_REQUEST)
    data = s.validated_data
    write_telemetry_and_gps(data)
    return Response({"status": "created"}, status=status.HTTP_201_CREATED)

@api_view(["GET"])
def last_location_view(request, device_id):
    rows = query_last_location(device_id)
    if not rows:
        return Response({"device_id": device_id, "found": False})
    r = rows[0]
    return Response({
        "device_id": device_id, "found": True,
        "ts": r["_time"],
        "lat": r.get("lat"), "lon": r.get("lon"),
        "alt_m": r.get("alt_m"), "vel_kmh": r.get("vel_kmh"),
        "sats": r.get("sats"), "hdop": r.get("hdop"),
    })
