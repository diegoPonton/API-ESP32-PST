from typing import Optional
from hmac import compare_digest

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

from .serializers import TelemetryInSerializer
from .influx import write_telemetry_and_gps, query_last_location, query_last_telemetry




def _require_bearer_token(request) -> Optional[Response]:
    """
    Valida `Authorization: Bearer <API_WRITE_TOKEN>` para POST de ingreso.
    Si no hay API_WRITE_TOKEN en settings (dev), no bloquea.
    """
    expected = getattr(settings, "API_WRITE_TOKEN", None)
    if not expected:
        # En desarrollo puede ir sin token; en prod debes ponerlo.
        return None

    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return Response(
            {"detail": "Missing Bearer token"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    supplied = auth.split(" ", 1)[1].strip()
    if not compare_digest(supplied, expected):
        return Response(
            {"detail": "Invalid token"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    return None


@api_view(["POST"])
def telemetry_ingest(request):
    """
    Ingesta de telemetría + GPS (privado). Requiere token si está configurado.
    """
    # Seguridad
    maybe_error = _require_bearer_token(request)
    if maybe_error is not None:
        return maybe_error

    # Validación
    s = TelemetryInSerializer(data=request.data)
    if not s.is_valid():
        return Response(
            {"errors": s.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Escritura
    data = s.validated_data
    try:
        write_telemetry_and_gps(data)
    except Exception as e:
        # Evita exponer detalles internos en producción
        return Response(
            {"detail": "Failed to write telemetry"},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    return Response({"status": "created"}, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([AllowAny])  # lectura pública
def last_location_view(request, device_id: str):
    """
    Última ubicación GPS pública para el dispositivo.
    """
    try:
        rows = query_last_location(device_id)
    except Exception:
        return Response(
            {"detail": "Query error"},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    if not rows or rows[0].get("lat") is None or rows[0].get("lon") is None:
        return Response({"device_id": device_id, "found": False})

    r = rows[0]
    return Response(
        {
            "device_id": device_id,
            "found": True,
            "ts": r.get("_time"),
            "lat": r.get("lat"),
            "lon": r.get("lon"),
            "alt_m": r.get("alt_m"),
            "vel_kmh": r.get("vel_kmh"),
            "sats": r.get("sats"),
            "hdop": r.get("hdop"),
        }
    )


@api_view(["GET"])
@permission_classes([AllowAny])  # lectura pública
def last_telemetry_view(request, device_id: str):
    """
    Última telemetría (sensores) pública para el dispositivo.
    """
    try:
        rows = query_last_telemetry(device_id)
    except Exception:
        return Response(
            {"detail": "Query error"},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    if not rows:
        return Response({"device_id": device_id, "found": False})

    r = rows[0]
    return Response(
        {
            "device_id": device_id,
            "found": True,
            "ts": r.get("_time"),
            "amb_temp_c": r.get("amb_temp_c"),
            "amb_hum_pct": r.get("amb_hum_pct"),
            "probe_temp_c": r.get("probe_temp_c"),
        }
    )