from rest_framework import serializers

class GPSInSerializer(serializers.Serializer):
    valid   = serializers.BooleanField()
    lat     = serializers.FloatField(required=False, allow_null=True)
    lng     = serializers.FloatField(required=False, allow_null=True)   # alias de lon en payload
    alt_m   = serializers.FloatField(required=False, allow_null=True)
    vel_kmh = serializers.FloatField(required=False, allow_null=True)
    sats    = serializers.IntegerField(required=False, allow_null=True)
    hdop    = serializers.FloatField(required=False, allow_null=True)

    def to_internal_value(self, data):
        d = super().to_internal_value(data)
        # Normaliza 'lng' -> 'lon'
        if 'lng' in data and 'lon' not in d:
            d['lon'] = float(data['lng']) if data['lng'] is not None else None
        return d

class AmbInSerializer(serializers.Serializer):
    ok      = serializers.BooleanField()
    temp_c  = serializers.FloatField(required=False, allow_null=True)
    hum_pct = serializers.FloatField(required=False, allow_null=True)

class ProbeInSerializer(serializers.Serializer):
    ok     = serializers.BooleanField()
    temp_c = serializers.FloatField(required=False, allow_null=True)

class TelemetryInSerializer(serializers.Serializer):
    device_id = serializers.CharField()
    ts_ms     = serializers.IntegerField(required=False)   # opcional: si no viene, la API usará now()
    amb       = AmbInSerializer(required=False)
    probe     = ProbeInSerializer(required=False)
    gps       = GPSInSerializer(required=False)
