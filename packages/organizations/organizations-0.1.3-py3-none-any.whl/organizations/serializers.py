from rest_framework import serializers
from .models import Organization
from typing import List


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ("networks", "name", "email", "phone", "keys")


class SuccessOrganizationsResponseSerializer(serializers.Serializer):
    response = serializers.CharField(max_length=2)


class DIDSerializer(serializers.Serializer):
    did = serializers.CharField(max_length=255)
    network_name = serializers.CharField(max_length=255)


class CreateDIDResponseSerializer(serializers.Serializer):
    dids = List[DIDSerializer]


class CreateDIDSerializer(serializers.Serializer):
    create_alastria_tx = serializers.CharField(max_length=1255)
    subject_address = serializers.CharField(max_length=255)
    email = serializers.CharField(max_length=255)


class OperatorDIDSerializer(serializers.Serializer):
    did = serializers.CharField(max_length=255)
    email = serializers.CharField(max_length=255)
    network_name = serializers.CharField(max_length=255)
