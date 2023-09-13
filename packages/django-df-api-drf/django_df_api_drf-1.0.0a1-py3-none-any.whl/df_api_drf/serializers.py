from rest_framework import serializers


class ErrorSerializer(serializers.Serializer):
    message = serializers.CharField(required=True)
    code = serializers.CharField(required=True)
    field = serializers.CharField(required=False)
    extra_data = serializers.JSONField(required=False)


class ErrorResponseSerializer(serializers.Serializer):
    errors = ErrorSerializer(many=True, required=True)
