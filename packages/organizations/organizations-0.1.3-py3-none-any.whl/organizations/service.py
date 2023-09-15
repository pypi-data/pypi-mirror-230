from __future__ import annotations
from .abstractions import AOrganizationsService
from .models import Organization, OperatorDID, UserProxy, Subject, SubjectDID
from django.conf import settings
from network_service_client.client import (
    Client as NetworkClient,
    Network as NetworkDTO,
    NetworksNames,
)
from organizations.did_factory.models import FactoryArgsModel
from organizations.did_factory.factory import Creator
from typing import List


class OrganizationsService(AOrganizationsService):
    @staticmethod
    def get_organization_by_operator_email(email: str) -> Organization | None:
        return Organization.objects.filter(operators__email=email).first()

    @staticmethod
    def set_did(email: str, did: str, network_name: str) -> None:
        subject: Subject | None = Subject.objects.filter(email=email).first()
        operator: UserProxy | None = UserProxy.objects.filter(email=email).first()

        if subject:
            subject_did = SubjectDID(network_name=network_name, subject=subject, did=did)
            subject_did.save()
        if operator:
            operator_did = OperatorDID(network_name=network_name, operator=operator, did=did)
            operator_did.save()

    @staticmethod
    def get_did(
        create_alastria_tx: str,
        subject_address: str,
        email: str,
    ) -> List[dict]:
        response: List[dict] = []

        organization: Organization = Organization.objects.filter(
            operators__email=email
        ).first()  # TODO ADD SUPPORT FOR SUBJECTS AND INTERMEDIARY

        for net in organization.networks:
            network_data: NetworkDTO = NetworkClient(
                service_host=settings.NETWORK_SERVICE_HOST
            ).get_network_by_name(NetworksNames[net])
            props = FactoryArgsModel(net=network_data)
            context = Creator().create_object(props).request()

            did: str = context.create_did_from_external_source(
                create_alastria_tx,
                subject_address,
                settings.ISSUER_ADDRESS,
                settings.ISSUER_PRIVATE_KEY,
            )
            OrganizationsService.set_did(email, did, net)
            response.append({"network_name": net, "did": did})

        return response
