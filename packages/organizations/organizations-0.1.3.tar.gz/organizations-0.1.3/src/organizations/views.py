from rest_framework.viewsets import ViewSet
from rest_framework.permissions import AllowAny
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.response import Response
from waffle.decorators import waffle_switch
from django.http.response import HttpResponseBadRequest
from .enums import OrganizationsSwitches
from .serializers import (
    OperatorDIDSerializer,
    OrganizationSerializer,
    SuccessOrganizationsResponseSerializer,
    CreateDIDSerializer,
    CreateDIDResponseSerializer,
)

from .service import OrganizationsService


class OrganizationsView(ViewSet):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        method="get",
        manual_parameters=[
            openapi.Parameter(
                "operator_email",
                openapi.IN_QUERY,
                description="",
                type=openapi.TYPE_STRING,
            )
        ],
        responses={200: openapi.Response("", OrganizationSerializer)},
    )
    @waffle_switch(OrganizationsSwitches.Organizations.value)
    @action(detail=False, methods=["get"])
    def get_organization_by_operator_email(self, request):
        operator_email: str = request.GET["operator_email"]
        organization = OrganizationsService.get_organization_by_operator_email(operator_email)
        if organization:
            return Response(OrganizationSerializer(organization).data)

        return HttpResponseBadRequest("Invalid email.")

    @swagger_auto_schema(
        method="post",
        request_body=CreateDIDSerializer,
        responses={200: openapi.Response("", CreateDIDResponseSerializer)},
    )
    @waffle_switch(OrganizationsSwitches.Organizations.value)
    @waffle_switch(
        OrganizationsSwitches.OrganizationsDID.value or OrganizationsSwitches.OperatorsDID.value
    )
    @action(detail=False, methods=["post"])
    def get_did(self, request):
        create_alastria_tx: str = request.data["create_alastria_tx"]
        subject_address: str = request.data["subject_address"]
        email: str = request.data["email"]
        return Response(OrganizationsService.get_did(create_alastria_tx, subject_address, email))

    @swagger_auto_schema(
        method="post",
        request_body=OperatorDIDSerializer,
        responses={200: openapi.Response("", SuccessOrganizationsResponseSerializer)},
    )
    @waffle_switch(OrganizationsSwitches.Organizations.value)
    @waffle_switch(
        OrganizationsSwitches.OrganizationsDID.value or OrganizationsSwitches.OperatorsDID.value
    )
    @action(detail=False, methods=["post"])
    def set_did(self, request):
        email: str = request.data["email"]
        did: str = request.data["did"]
        network_name: str = request.data["network_name"]
        OrganizationsService.set_did(email, did, network_name)
        return Response({"response": "OK"})
