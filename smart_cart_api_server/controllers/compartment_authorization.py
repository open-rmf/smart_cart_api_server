from smart_cart_api_server.models.tables.CardIdADIDTable import AbstractCardIdADIDTable, UserInfo
from keycloak import KeycloakAdmin
from keycloak import KeycloakOpenIDConnection
from typing import List

def get_cart_location(cart_id: str) -> List[str]:
    #TODO(arjo) implement logic to pull cart id mapping from the server
    return []

def get_compartment_authorization(card_id_table: AbstractCardIdADIDTable, keycloak_client: KeycloakOpenIDConnection, cart_id: str, card_id: str) -> bool:
    user_info = card_id_table.lookup_cardid(card_id)
    if user_info is None:
        return False

    # Check if user exists
    keycloak_admin = KeycloakAdmin(connection=keycloak_client)
    if keycloak_admin.get_user_id(user_info.adid) is None:
        return False


    return True