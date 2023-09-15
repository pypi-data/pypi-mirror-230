from dataclasses import dataclass
from network_service_client.client import (
    Network as NetworkDTO,
)


@dataclass
class FactoryArgsModel:
    net: NetworkDTO
