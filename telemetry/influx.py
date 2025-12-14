# telemetry/influx.py

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from django.conf import settings
from datetime import datetime, timezone

# ─────────────────────────────────────────────
# Cliente InfluxDB (singleton)
# ─────────────────────────────────────────────
_client = None
_write_api = None
_query_api = None


def _get_client():
    global _client, _write_api, _query_api
    if _client is None:
        _client = InfluxDBClient(
            url=settings.INFLUX_URL,
            token=settings.INFLUX_TOKEN,
            org=settings.INFLUX_ORG,
            timeout=10_000,
        )
        _write_api = _client.write_api(write_options=SYNCHRONOUS)
        _query_api = _client.query_api()
    return _client, _write_api, _query_api


def _to_ns(ts_ms: int) -> int:
    """Convierte milisegundos a nanosegundos."""
    return int(ts_ms) * 1_000_000


# ─────────────────────────────────────────────
# Escritura de telemetría + GPS
# ─────────────────────────────────────────────
def write_telemetry_and_gps(payload: dict):
    _, write_api, _ = _get_client()
    bucket = settings.INFLUX_BUCKET

    device_id = payload.get("device_id", "unknown")
    ts_ms = payload.get("ts_ms")

    # ── TELEMETRÍA ───────────────────────────
    p = Point("telemetry").tag("device_id", device_id)

    amb = payload.get("amb") or {}
    if amb.get("ok"):
        if amb.get("temp_c") is not None:
            p = p.field("amb_temp_c", float(amb["temp_c"]))
        if amb.get("hum_pct") is not None:
            p = p.field("amb_hum_pct", float(amb["hum_pct"]))

    probe = payload.get("probe") or {}
    if probe.get("ok") and probe.get("temp_c") is not None:
        p = p.field("probe_temp_c", float(probe["temp_c"]))

    # Timestamp: si viene ts_ms lo usamos, si no, now()
    if ts_ms is not None:
        p = p.time(_to_ns(ts_ms), WritePrecision.NS)
    else:
        p = p.time(datetime.now(timezone.utc), WritePrecision.MS)

    # Escribimos solo si hay fields
    if len(p._fields) > 0:
        write_api.write(bucket=bucket, record=p)

    # ── GPS ─────────────────────────────────
    gps = payload.get("gps") or {}
    if gps.get("valid"):
        pg = Point("gps").tag("device_id", device_id)

        # Fields GPS
        for k in ("lat", "lon", "alt_m", "vel_kmh", "hdop"):
            v = gps.get(k)
            if v is not None:
                pg = pg.field(k, float(v))

        if gps.get("sats") is not None:
            pg = pg.field("sats", int(gps["sats"]))

        # Timestamp GPS
        if ts_ms is not None:
            pg = pg.time(_to_ns(ts_ms), WritePrecision.NS)
        else:
            pg = pg.time(datetime.now(timezone.utc), WritePrecision.MS)

        # Escribimos solo si hay fields
        if len(pg._fields) > 0:
            write_api.write(bucket=bucket, record=pg)


# ─────────────────────────────────────────────
# Query: última ubicación GPS
# ─────────────────────────────────────────────
def query_last_location(device_id: str):
    _, _, query_api = _get_client()
    bucket = settings.INFLUX_BUCKET

    flux = f'''
from(bucket: "{bucket}")
  |> range(start: -7d)
  |> filter(fn: (r) => r._measurement == "gps" and r.device_id == "{device_id}")
  |> pivot(rowKey:["_time"], columnKey:["_field"], valueColumn:"_value")
  |> keep(columns: ["_time","device_id","lat","lon","alt_m","vel_kmh","sats","hdop"])
  |> sort(columns: ["_time"], desc: true)
  |> limit(n: 1)
'''

    tables = query_api.query(org=settings.INFLUX_ORG, query=flux)
    rows = []
    for table in tables:
        for record in table.records:
            rows.append(record.values)

    return rows
