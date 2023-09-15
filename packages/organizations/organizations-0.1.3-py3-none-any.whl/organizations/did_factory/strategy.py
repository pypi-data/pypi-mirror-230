import random
from .abstractions import ANetworkStrategy
from alastria_service_client.client import (
    AClient as AlastriaAClinet,
    Client as AlastriaClient,
)
from .models import FactoryArgsModel
from network_service_client.enums import ContractsNames
from alastria_service_client.validators import (
    Address,
    NetworkValidator,
    OnlyNetworkValidator,
    SignatureValidator,
    RunRawTransaction,
    PrepareIDValidator,
    DelegateCallValidator,
    CreateAlastriaIdentityValidator,
    AddKeyValidator,
    AddIdentityIssuerValidator,
    EidasLevelEnum,
)
from django.conf import settings
from multiformats import multibase


class AlastriaNetworkStrategy(ANetworkStrategy):
    def __init__(self, props: FactoryArgsModel):
        self.alastria_service_client: AlastriaAClinet = AlastriaClient(
            service_host=settings.ALASTRIA_SERVICE_HOST
        )
        self.props = props
        network_data = self.props.net
        self.network_body = NetworkValidator(
            provider=network_data.node["path"],
            identity_manager_contract_address=list(
                filter(
                    lambda contract: contract["name"]
                    == ContractsNames.AlastriaIdentityManager.value,
                    network_data.contracts,
                )
            )[0]["address"],
            identity_manager_contract_abi=list(
                filter(
                    lambda contract: contract["name"]
                    == ContractsNames.AlastriaIdentityManager.value,
                    network_data.contracts,
                )
            )[0]["abi"],
            public_key_registry_contract_address=list(
                filter(
                    lambda contract: contract["name"]
                    == ContractsNames.AlastriaPublicKeyRegistry.value,
                    network_data.contracts,
                )
            )[0]["address"],
            public_key_registry_contract_abi=list(
                filter(
                    lambda contract: contract["name"]
                    == ContractsNames.AlastriaPublicKeyRegistry.value,
                    network_data.contracts,
                )
            )[0]["abi"],
            credential_registry_contract_abi=list(
                filter(
                    lambda contract: contract["name"]
                    == ContractsNames.AlastriaCredentialRegistry.value,
                    network_data.contracts,
                )
            )[0]["abi"],
            credential_registry_contract_address=list(
                filter(
                    lambda contract: contract["name"]
                    == ContractsNames.AlastriaCredentialRegistry.value,
                    network_data.contracts,
                )
            )[0]["address"],
            chainId=network_data.chain_id,
        )

    def register_issuer(
        self,
        new_issuer_address: Address = Address(""),
        issuer_address: Address = Address(""),
        issuer_private_key: str = "",
    ) -> str:
        self.alastria_service_client.run_raw_transaction(
            RunRawTransaction(
                raw_transaction=self.alastria_service_client.signature(
                    SignatureValidator(
                        transaction=self.alastria_service_client.delegate_call(
                            DelegateCallValidator(
                                data=self.alastria_service_client.add_identity_issuer(
                                    AddIdentityIssuerValidator(
                                        new_issuer_address=new_issuer_address,
                                        network=self.network_body,
                                        eidas_level=EidasLevelEnum.Low,
                                    )
                                ).response,
                                issuer_address=issuer_address,
                                network=self.network_body,
                            ),
                        ).response,
                        private_key=issuer_private_key,
                        network=self.network_body,
                    )
                ).response,
                network=self.network_body,
            )
        )
        return "OK"

    def create_did(
        self,
        sign_address: Address = Address(""),
        issuer_address: Address = Address(""),
        public_key: str = "",
        issuer_private_key: str = "",
        new_issuer_private_key: str = "",
    ) -> str:
        self.alastria_service_client.run_raw_transaction(
            RunRawTransaction(
                raw_transaction=self.alastria_service_client.signature(
                    SignatureValidator(
                        transaction=self.alastria_service_client.delegate_call(
                            DelegateCallValidator(
                                data=self.alastria_service_client.prepare_alastria_id_encode_abi(
                                    PrepareIDValidator(
                                        sign_address=sign_address,
                                        network=self.network_body,
                                    )
                                ).response,
                                issuer_address=issuer_address,
                                network=self.network_body,
                            ),
                        ).response,
                        private_key=issuer_private_key,
                        network=self.network_body,
                    )
                ).response,
                network=self.network_body,
            )
        )
        self.alastria_service_client.run_raw_transaction(
            RunRawTransaction(
                raw_transaction=self.alastria_service_client.signature(
                    SignatureValidator(
                        transaction=self.alastria_service_client.create_alastria_identity(
                            CreateAlastriaIdentityValidator(
                                add_public_key_call_data=self.alastria_service_client.add_key(
                                    AddKeyValidator(
                                        public_key=public_key,
                                        network=self.network_body,
                                    )
                                ).response,
                                issuer_address=sign_address,
                                network=self.network_body,
                            )
                        ).response,
                        private_key=new_issuer_private_key.encode("utf-8").strip(),
                        network=self.network_body,
                    )
                ).response,
                network=self.network_body,
            )
        )

        return (
            self.props.net.did_prefix
            + self.alastria_service_client.identity_keys(
                sign_address, OnlyNetworkValidator(network=self.network_body)
            ).response[2:]
        )

    def create_did_from_external_source(
        self,
        tx: str,
        subject_address: Address = Address(""),
        issuer_address: Address = Address(""),
        issuer_private_key: str = "",
    ) -> str:
        self.alastria_service_client.run_raw_transaction(
            RunRawTransaction(
                raw_transaction=self.alastria_service_client.signature(
                    SignatureValidator(
                        transaction=self.alastria_service_client.delegate_call(
                            DelegateCallValidator(
                                data=self.alastria_service_client.prepare_alastria_id_encode_abi(
                                    PrepareIDValidator(
                                        sign_address=Address(subject_address),
                                        network=self.network_body,
                                    )
                                ).response,
                                issuer_address=Address(issuer_address),
                                network=self.network_body,
                            )
                        ).response,
                        private_key=issuer_private_key,
                        network=self.network_body,
                    )
                ).response,
                network=self.network_body,
            )
        )
        self.alastria_service_client.run_raw_transaction(
            RunRawTransaction(raw_transaction=tx, network=self.network_body)
        )
        return (
            self.props.net.did_prefix
            + self.alastria_service_client.identity_keys(
                Address(subject_address),
                OnlyNetworkValidator(network=self.network_body),
            ).response[2:]
        )


class LacchainNetworkStrategy(ANetworkStrategy):
    def __init__(self, props: FactoryArgsModel):
        self.props = props
        self.prefix = props.net.did_prefix

    def create_did(
        self,
        signAddress: Address = Address(""),
        issuer_address: Address = Address(""),
        public_key: str = "",
        issuer_private_key: str = "",
        new_issuer_private_key: str = "",
    ) -> str:
        # DID
        did = self.prefix + signAddress
        return did

    def create_did_from_external_source(
        self,
        tx: str,
        subject_address: Address = Address(""),
        issuer_address: Address = Address(""),
        issuer_private_key: str = "",
    ) -> str:
        did = self.prefix + subject_address
        return did

    def register_issuer(
        self,
        new_issuer_address: Address = Address(""),
        issuer_address: Address = Address(""),
        issuer_private_key: str = "",
    ) -> str:
        return "OK"


class EbsiNetworkStrategy(ANetworkStrategy):
    def __init__(self, props: FactoryArgsModel):
        self.props = props
        self.prefix = props.net.did_prefix

    def create_did(
        self,
        signAddress: Address = Address(""),
        issuer_address: Address = Address(""),
        public_key: str = "",
        issuer_private_key: str = "",
        new_issuer_private_key: str = "",
    ) -> str:
        randomBytes = random.randbytes(16)
        did = self.prefix + multibase.encode(randomBytes, "base58btc")
        return did

    def create_did_from_external_source(
        self,
        tx: str,
        subject_address: Address = Address(""),
        issuer_address: Address = Address(""),
        issuer_private_key: str = "",
    ) -> str:
        did = self.prefix + subject_address
        return did

    def register_issuer(
        self,
        new_issuer_address: Address = Address(""),
        issuer_address: Address = Address(""),
        issuer_private_key: str = "",
    ) -> str:
        return "OK"
