from rest_framework import serializers

class GPSInSerializer(serializers.Serializer):
    valid   = serializers.BooleanField()

    lat     = serializers.FloatField(required=False, allow_null=True)
    lon     = serializers.FloatField(required=False, allow_null=True)  # ✅ AGREGAR
    lng     = serializers.FloatField(required=False, allow_null=True)  # opcional alias

    alt_m   = serializers.FloatField(required=False, allow_null=True)
    vel_kmh = serializers.FloatField(required=False, allow_null=True)
    sats    = serializers.IntegerField(required=False, allow_null=True)
    hdop    = serializers.FloatField(required=False, allow_null=True)

    def to_internal_value(self, data):
        d = super().to_internal_value(data)

        # Normaliza: si viene lng y no viene lon, crea lon
        if d.get("lon") is None and d.get("lng") is not None:
            d["lon"] = d["lng"]

        return d
