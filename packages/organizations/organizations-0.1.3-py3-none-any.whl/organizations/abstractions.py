from __future__ import annotations
from abc import ABC, abstractmethod
from .models import Organization
from typing import List
from network_service_client.client import NetworksNames


class AOrganizationsService(ABC):
    @staticmethod
    @abstractmethod
    def get_organization_by_operator_email(email: str) -> Organization | None:
        ...

    @staticmethod
    @abstractmethod
    def set_did(email: str, did: str, network_name: str) -> None:
        ...

    @staticmethod
    @abstractmethod
    def get_did(
        create_alastria_tx: str,
        subject_address: str,
        email: str,
    ) -> List[dict]:
        ...
