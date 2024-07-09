import json
from keycloak import KeycloakOpenIDConnection

def keycloak_from_json(filename: str) -> KeycloakOpenIDConnection:
    with open(filename) as f:
        config = json.load(f)

        if "server_url" not in config:
            raise "Could not find server url in config file"

        if "realm" not in config:
            raise "Could not find realm in config file"

        if "client_id" not in config:
            raise "Could not find client_id in config file"

        if "client_secret" not in config:
            raise "Could not find client_id in config file"

        return KeycloakOpenIDConnection(
                        server_url=config["server_url"],
                        realm_name=config["realm"],
                        client_id=config["client_id"],
                        client_secret_key=config["client_secret"],
                        verify=True)