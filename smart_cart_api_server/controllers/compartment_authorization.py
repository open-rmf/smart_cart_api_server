from smart_cart_api_server.models.tables.CardIdADIDTable import AbstractCardIdADIDTable, UserInfo
from smart_cart_api_server.controllers.robot_status import get_robot_status
from keycloak import KeycloakAdmin
from keycloak import KeycloakOpenIDConnection
from typing import List

async def get_compartment_authorization(
        card_id_table: AbstractCardIdADIDTable,
        keycloak_client: KeycloakOpenIDConnection| None,
        cart_id: str, card_id: str,
        api_server: str,  headers: dict[str, str] | None = None) -> bool:

    print("Attempting user lookup")
    user_info = card_id_table.lookup_cardid(card_id)
    if user_info is None:
        return False

    print("Attempting keycloak connection")
    # Check if user exists
    if keycloak_client is not None:
        keycloak_admin = KeycloakAdmin(connection=keycloak_client)
        if keycloak_admin.get_user_id(user_info.adid) is None:
            return False

    print("Retrieving status")
    status = await get_robot_status(cart_id, api_server, headers)

    if status.currentLocationIndex is None:
        return False

    if status.destinations[status.currentLocationIndex] not in user_info.waypoints:
        return False

    return True