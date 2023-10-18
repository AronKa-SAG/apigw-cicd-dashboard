from utilities.assets.Asset import Asset


class Loadbalancer(Asset):
    """Loadbalancer asset class for API Gateway.
    
    :param payload: payload dict of the asset
    """
    
    def __init__(self, payload: dict) -> None:
        super().__init__(payload)
        self.name = "loadbalancer"
        self.id = "loadBalancer"
        self.https_urls: str = payload.get("httpsUrls", "")
        self.http_urls: str = payload.get("httpUrls", "")
        self.websocket_url = payload.get("websocketUrls", "")
        self.asset_type = "configurations"
        
    def _update_payload(self) -> None:
        """Updates objects payload."""
        self._payload["httpsUrls"] = self.https_urls
        self._payload["httpUrls"] = self.http_urls
        self._payload["websocketUrls"] = self.websocket_url
