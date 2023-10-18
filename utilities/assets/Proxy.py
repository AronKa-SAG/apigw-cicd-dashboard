from utilities.assets.Asset import Asset


class Proxy(Asset):
    """Proxy asset class for API Gateway.
    
    :param payload: payload dict of the asset
    """
    
    def __init__(self, payload: dict) -> None:
        super().__init__(payload)
        self.name = payload.get("proxyAlias", "")
        self.id = "outboundproxy"
        self.host: str = payload.get("host", "")
        self.port: str = payload.get("port", "")
        self.username = payload.get("username", "")
        self.password = payload.get("password", "")
        self.protocol = payload.get("protocol", "")
        self.is_default = payload.get("isDefault", "")
        self.asset_type = "is"
        
    def _update_payload(self) -> None:
        """Updates objects payload."""
        self._payload["host"] = self.host
        self._payload["port"] = self.port
        self._payload["username"] = self.username
        self._payload["passwort"] = self.password
        self._payload["protocol"] = self.protocol
        self._payload["isDefault"] = self.is_default
