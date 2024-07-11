from smart_cart_api_server.models.cart_status import CartStatus
from urllib.parse import urljoin
import aiohttp
from fastapi import HTTPException

import json

async def update_cart_status(cart_status: CartStatus, api_server: str, headers: dict[str, str]) -> CartStatus:
    print(cart_status.json())
    async with aiohttp.ClientSession(headers=headers) as session:
        data = {
            "id": cart_status.cartId,
            "type": "smart_cart",
            "data": json.loads(cart_status.json()) #horrible hack cause we are still on pydantic 1.x. In pydantic 2.x we can use model_dump(round_trip=True)
        }
        async with session.put(urljoin(api_server, f"/rios"), headers={"Content-Type": "application/json"}, json=data) as response:
            if response.status != 200 and response.status != 201:
                print(response.status)
                raise HTTPException(
                    status_code=500, detail=f"got error from remote server: {await response.text()}"
                )
            print(await response.text())
            return cart_status