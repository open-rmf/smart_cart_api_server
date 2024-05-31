from keycloak import KeycloakAdmin
from keycloak import KeycloakOpenIDConnection
from smart_cart_api_server.keycloak.parse_config import keycloak_from_json

keycloak_connection: KeycloakOpenIDConnection = keycloak_from_json("keycloak_config.json")

keycloak_admin = KeycloakAdmin(connection=keycloak_connection)


def start():
    print(keycloak_admin.get_user_id("admin"))