from __future__ import annotations
from celery import shared_task
from django.conf import settings
from network_service_client.client import (
    Client as NetworkClient,
    Network as NetworkDTO,
    NetworksNames,
)
from organizations.did_factory.models import FactoryArgsModel
from organizations.did_factory.factory import Creator
from organizations.models import Organization, OrganizationDID, Issuer


@shared_task
def create_organization_did(organization_id: int) -> None:
    organization = Organization.objects.get(pk=organization_id)
    for net in organization.networks:
        network_data: NetworkDTO = NetworkClient(
            service_host=settings.NETWORK_SERVICE_HOST
        ).get_network_by_name(NetworksNames[net])
        props = FactoryArgsModel(net=network_data)
        context = Creator().create_object(props).request()
        did: str = context.create_did(
            organization.keys.address,
            settings.ISSUER_ADDRESS,
            str(organization.keys.public_key),
            settings.ISSUER_PRIVATE_KEY,
            organization.keys.private_key,  # TODO: encrypt this
        )

        organization_did = OrganizationDID(
            network_name=NetworksNames[net],
            organization=organization,
            did=did,
        )

        organization_did.save()


@shared_task
def register_issuer_by_network_task(organization_id: int, net: str) -> None:
    organization = Organization.objects.get(pk=organization_id)
    issuer: Issuer = Issuer.objects.get(organization=organization)
    organization_did: OrganizationDID | None = OrganizationDID.objects.filter(
        organization=organization, network_name=NetworksNames[net]
    ).first()
    if not organization_did:
        raise Exception(
            f"You cannot register an organization without DID as an issuer, organization: {organization.id} network: {NetworksNames[net]}"
        )
    network_data: NetworkDTO = NetworkClient(
        service_host=settings.NETWORK_SERVICE_HOST
    ).get_network_by_name(NetworksNames[net])
    props = FactoryArgsModel(net=network_data)
    context = Creator().create_object(props).request()
    context.register_issuer(
        organization.keys.address,
        settings.ISSUER_ADDRESS,
        settings.ISSUER_PRIVATE_KEY,
    )
    issuer.active = True
    issuer.save()


@shared_task
def register_issuer_task(organization_id: int) -> None:
    organization = Organization.objects.get(pk=organization_id)
    for net in organization.networks:
        register_issuer_by_network_task.delay(organization_id, net)
