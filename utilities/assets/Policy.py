from utilities.assets.Asset import Asset


class Policy(Asset):
    """Policy asset class for API Gateway.
    
    :param payload: payload dict of the asset
    """
    
    def __init__(self, payload: dict) -> None:
        super().__init__(payload)
        self.name = payload["names"][0]["value"]
        self.id = payload["id"]
        self.kind: str = payload["templateKey"]
        self.asset_type = "policyActions"
        
    def _update_payload(self) -> None:
        """Updates objects payload"""
        self._payload["names"][0]["value"] = self.name
        self._payload["templateKey"] = self.kind
        