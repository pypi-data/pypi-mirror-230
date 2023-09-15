from .abstractions import AFactory, AContext
from .strategy import (
    AlastriaNetworkStrategy,
    EbsiNetworkStrategy,
    LacchainNetworkStrategy,
)
from .context import Context
from network_service_client.client import NetworksNames
from .models import FactoryArgsModel


class Creator(AFactory):
    @staticmethod
    def create_object(props: FactoryArgsModel) -> AContext:
        if props.net.name == NetworksNames.AlastriaDefaultName:
            return Context(AlastriaNetworkStrategy(props))
        if props.net.name == NetworksNames.LacchainDefaultName:
            return Context(LacchainNetworkStrategy(props))
        if props.net.name == NetworksNames.EbsiDefaultName:
            return Context(EbsiNetworkStrategy(props))
        raise Exception("Cant find any strategy.")
