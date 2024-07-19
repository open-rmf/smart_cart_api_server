import json
import aiohttp
from aiohttp import FormData
from fastapi import HTTPException
from urllib.parse import urljoin

class KeyCloakClient:
    def __init__(self, server_url, realm_name) -> None:
        self.server_url = server_url
        self.realm_name = realm_name
        #self.client_id = client_id
        #self.client_secret = client_secret_key

    async def check_user_exists(self, headers, user: str) -> bool:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(urljoin(self.server_url, f"admin/realms/{self.realm_name}/users?username={user}")) as response:
                if response.status != 200:
                    raise HTTPException(
                        status_code=401, detail=f"Could not get user info from keycloak. Check your configs")

                return len(json.loads(await response.text())) > 0

def keycloak_from_json(filename: str) -> KeyCloakClient:
    with open(filename) as f:
        config = json.load(f)

        if "server_url" not in config:
            raise "Could not find server url in config file"

        if "realm" not in config:
            raise "Could not find realm in config file"


        return KeyCloakClient(
                        server_url=config["server_url"],
                        realm_name=config["realm"])