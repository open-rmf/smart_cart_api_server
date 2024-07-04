from smart_cart_api_server.models.tables.CardIdADIDTable import AbstractCardIdADIDTable, UserInfo
from smart_cart_api_server.controllers.robot_status import get_robot_status
from smart_cart_api_server.keycloak.parse_config import KeyCloakClient
from typing import List

async def get_compartment_authorization(
        card_id_table: AbstractCardIdADIDTable,
        keycloak_client: KeyCloakClient | None,
        cart_id: str, card_id: str,
        api_server: str,  headers: dict[str, str] | None = None) -> bool:

    print("Attempting user lookup")
    user_info = card_id_table.lookup_cardid(card_id)
    if user_info is None:
        return False

    print("Attempting keycloak connection")
    # Check if user exists
    if keycloak_client is not None:
        keycloak_token = await keycloak_client.get_token()
        if not await keycloak_client.check_user_exists(keycloak_token, user_info.adid):
            print("User was not found in keycloak")
            return False

    print("Retrieving status")
    status = await get_robot_status(cart_id, api_server, headers)

    if status.currentLocation is None:
        print("Robot is moving cant open door")
        return False

    if status.currentLocation.name not in user_info.waypoints:
        print(f"robot is at {status.currentLocation.name} which is not in {user_info.waypoints}")
        return False

    return True