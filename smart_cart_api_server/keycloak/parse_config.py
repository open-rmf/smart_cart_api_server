import json
import aiohttp
from aiohttp import FormData
from fastapi import HTTPException
from urllib.parse import urljoin

class KeyCloakClient:
    def __init__(self, server_url, realm_name, client_id, client_secret_key) -> None:
        self.server_url = server_url
        self.realm_name = realm_name
        self.client_id = client_id
        self.client_secret = client_secret_key

    async def get_token(self) -> str:
        async with aiohttp.ClientSession() as session:
            form_data = FormData()
            #grant_type=client_credentials&client_id=$client_id&client_secret=$client_secret
            form_data.add_field('grant_type', 'client_credentials')
            form_data.add_field('client_id', self.client_id)
            form_data.add_field('client_secret', self.client_secret)
            async with session.post(urljoin(self.server_url, f"/realms/{self.realm_name}/protocol/openid-connect/token"), data=form_data) as response:
                if response.status != 200:
                    raise HTTPException(
                        status_code=401, detail=f"Could not get keycloak token"
                    )
                parsed = json.loads(await response.text())
                if "access_token" in parsed:
                    return parsed["access_token"]
                raise HTTPException(
                        status_code=401, detail=f"Keycloak token malformed"
                    )


    async def check_user_exists(self, token, user) -> bool:
        headers = {"Authorization": f"Bearer {token}"}
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

        if "client_id" not in config:
            raise "Could not find client_id in config file"

        if "client_secret" not in config:
            raise "Could not find client_id in config file"

        return KeyCloakClient(
                        server_url=config["server_url"],
                        realm_name=config["realm"],
                        client_id=config["client_id"],
                        client_secret_key=config["client_secret"])