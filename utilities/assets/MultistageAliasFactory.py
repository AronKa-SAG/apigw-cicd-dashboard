from utilities.assets.EndpointAlias import EndpointAlias
from utilities.assets.MultistageAlias import MultistageAlias
from utilities.assets.SimpleAlias import SimpleAlias


class MultistageAliasFactory():
    """Factory class for multistage aliases.
    
    :param payload: payload dict of the alias
    """
    def __init__(self):
        pass
    
    @classmethod
    def __create_multistage_endpointalias(cls, alias: EndpointAlias) -> MultistageAlias:
        connection_params_dict = {}
        dev_values_dict = alias.get_staging_values()
        test_endpoint = dev_values_dict["endPointURI"].replace("-dev", "-test")
        qs_endpoint = dev_values_dict["endPointURI"].replace("-dev", "-qs")
        prod_endpoint = dev_values_dict["endPointURI"].replace("-dev", "-prod").replace("t04", "p04")
        test_key_alias = "client_certificate_internal_mediator_test"
        qs_key_alias = "client_certificate_internal_mediator_qs"
        prod_key_alias = "client_certificate_internal_mediator_prod"
        
        connection_params_dict["dev"] = dev_values_dict
        connection_params_dict["test"] = {
            "endPointURI": test_endpoint,
            "keystoreAlias": alias.keystore_alias,
            "keyAlias": test_key_alias,
            "truststoreAlias": alias.truststore_alias
        }
        connection_params_dict["qs"] = {
            "endPointURI": qs_endpoint,
            "keystoreAlias": alias.keystore_alias,
            "keyAlias": qs_key_alias,
            "truststoreAlias": alias.truststore_alias
        }
        connection_params_dict["prod"] = {
            "endPointURI": prod_endpoint,
            "keystoreAlias": alias.keystore_alias,
            "keyAlias": prod_key_alias,
            "truststoreAlias": alias.truststore_alias
        }  
        
        my_mulistage_alias = MultistageAlias(alias.get_payload(), connection_params_dict)
        return my_mulistage_alias

    @classmethod
    def __create_multistage_simplealias(cls, alias: SimpleAlias) -> MultistageAlias:
        connection_params_dict = {}
        dev_value = alias.get_staging_values()["value"]
        test_endpoint = dev_value.replace("-dev", "-test")
        qs_endpoint = dev_value.replace("-dev", "-qs")
        prod_endpoint = dev_value.replace("-dev", "-prod").replace("t04", "p04")

        connection_params_dict["dev"] = alias.get_staging_values()
        connection_params_dict["test"] = {
            "value": test_endpoint
        }
        connection_params_dict["qs"] = {
            "value": qs_endpoint
        }
        connection_params_dict["prod"] = {
            "value": prod_endpoint
        }  
        
        my_mulistage_alias = MultistageAlias(alias.get_payload(), connection_params_dict)
        return my_mulistage_alias

    @classmethod
    def create_multistage_alias(cls, alias) -> MultistageAlias | None:
        
        if isinstance(alias, SimpleAlias):
            return cls.__create_multistage_simplealias(alias)
        elif isinstance(alias, EndpointAlias):
            return cls.__create_multistage_endpointalias(alias)
        else:
            return None