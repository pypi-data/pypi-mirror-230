from abc import ABC, abstractmethod
from .models import FactoryArgsModel
from alastria_service_client.validators import Address


class ANetworkStrategy(ABC):
    @abstractmethod
    def register_issuer(
        self,
        new_issuer_address: Address = Address(""),
        issuer_address: Address = Address(""),
        issuer_private_key: str = "",
    ) -> str:
        """"""

    @abstractmethod
    def create_did(
        self,
        sign_address: Address = Address(""),
        issuer_address: Address = Address(""),
        public_key: str = "",
        issuer_private_key: str = "",
        new_issuer_private_key: str = "",
    ) -> str:
        """"""

    @abstractmethod
    def create_did_from_external_source(
        self,
        create_alastria_tx: str,
        subject_address: Address = Address(""),
        issuer_address: Address = Address(""),
        issuer_private_key: str = "",
    ) -> str:
        """"""


class AContext(ABC):
    @abstractmethod
    def request(self) -> ANetworkStrategy:
        """"""


class AFactory(ABC):
    @staticmethod
    @abstractmethod
    def create_object(props: FactoryArgsModel) -> AContext:
        """"""
