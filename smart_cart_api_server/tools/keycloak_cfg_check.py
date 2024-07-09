# Tool to diagnose issues with KeyCloak
from smart_cart_api_server.keycloak.parse_config import *
import asyncio
import sys

async def client():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} username")
        return

    client = keycloak_from_json("keycloak_config.json")
    token = await client.get_token()
    exists = await client.check_user_exists(token, sys.argv[1])
    print(f"admin user exists {exists}")

def main():
    asyncio.run(client())

if __name__ == "__main__":
    main()