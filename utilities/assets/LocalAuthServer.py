from utilities.assets.Asset import Asset


class LocalAuthServer(Asset):
    """Local authorization server alias asset class for API Gateway.
    
    :param payload: payload dict of the asset
    """
    
    def __init__(self, payload: dict) -> None:
        fix_payload = payload["alias"]
        super().__init__(fix_payload)
        self.name = fix_payload["name"]
        self.id = fix_payload["id"]
        self.local_introspection_config: dict = fix_payload.get("localIntrospectionConfig", {})
        self.token_generator_config: dict = fix_payload.get("tokenGeneratorConfig", {})
        self.ssl_config: dict = fix_payload.get("sslConfig", {})
        self.asset_type = "alias"
        
    def _update_payload(self) -> None:
        """Updates objects payload."""
        self._payload["name"]= self.name
        self._payload["localIntrospectionConfig"] = self.local_introspection_config
        self._payload["tokenGeneratorConfig"]= self.token_generator_config
        self._payload["sslConfig"]= self.ssl_config
        
    def update_token_generator_config(self, access_token_exp_interval: int, auth_code_exp_interval: int, expiry: int, algorithm: str) -> None:
        """Update the token generator config."""
        self.token_generator_config.update({
            "accessTokenExpInterval": access_token_exp_interval,
            "authCodeExpInterval": auth_code_exp_interval, 
            "expiry": expiry, 
            "algorithm": algorithm
            })
        
    def update_local_introspection_config(self, issuer: str) -> None:
        """Update the local introspection config."""
        self.local_introspection_config.update({
            "issuer": issuer
            })
    
    def update_ssl_config(self, key_store_alias: str, key_alias: str) -> None:
        """Update the ssl config."""
        self.ssl_config.update({
            "keyStoreAlias": key_store_alias,
            "keyAlias": key_alias
            })
        