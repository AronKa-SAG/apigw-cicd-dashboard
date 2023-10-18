from utilities.assets.Alias import Alias
from utilities.assets.EndpointAlias import EndpointAlias
from utilities.assets.SimpleAlias import SimpleAlias


class AliasFactory():
    """Factory class for aliases.
    
    :param payload: payload dict of the alias
    """
    def __init__(self):
        pass
    
    @classmethod
    def create_alias(cls, payload: dict) -> Alias | None:
        if payload["type"] == "endpoint":
            return EndpointAlias(payload)
        elif payload["type"] == "simple":
            return SimpleAlias(payload)
        else:
            return None