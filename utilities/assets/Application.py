from utilities.assets.Asset import Asset


class Application(Asset):
    """Application asset class for API Gateway.
    
    :param payload: payload dict of the asset
    """
    
    def __init__(self, payload: dict) -> None:
        try:
            fix_payload = payload["applications"][0]
        except KeyError:
            fix_payload = payload
        super().__init__(fix_payload)
        self.name = fix_payload["name"]
        self.id = fix_payload["id"]
        self.description: str = fix_payload.get("description", "")
        self.is_suspended: bool = fix_payload.get("isSuspended", False)
        self.api_list: list[str] = fix_payload.get("consumingAPIs", [])
        self.asset_type = "applications"
    
    def _update_payload(self) -> None:
        """Updates objects payload"""
        self._payload["name"] = self.name
        self._payload["description"] = self.description
        self._payload["isSuspended"] = self.is_suspended
