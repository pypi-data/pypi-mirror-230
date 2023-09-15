from .abstractions import AContext, ANetworkStrategy


class Context(AContext):
    def __init__(self, strategy: ANetworkStrategy):
        self.strategy = strategy

    def request(self) -> ANetworkStrategy:
        return self.strategy
