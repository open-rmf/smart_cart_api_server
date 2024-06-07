from smart_cart_api_server.models.token import Credentials, TokenResponse
from smart_cart_api_server.models.cart_authorization import (
    AuthorizationRequest,
    AuthorizationResponse,
)
from smart_cart_api_server.models.cart_status import CartStatus
from smart_cart_api_server.models.destination_complete import DestinationComplete
from smart_cart_api_server.models.robot_status import RobotStatus
from smart_cart_api_server.models.task_status import TaskStatus

from smart_cart_api_server.models.tables.CardIdADIDTable import CSVCardIdADIDTable

from smart_cart_api_server.controllers.robot_status import get_robot_status
from smart_cart_api_server.controllers.task_status import get_task_status
from smart_cart_api_server.controllers.compartment_authorization import (
    get_compartment_authorization,
)
from smart_cart_api_server.controllers.destination_complete import (
    notify_rmf_destination_complete,
)

from smart_cart_api_server.keycloak.parse_config import keycloak_from_json

from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from datetime import datetime, timedelta
from typing import Annotated, Optional

app = FastAPI()

import os

# LOAD CONFIGS
api_server_url = "http://localhost:8000/"
if "API_SERVER_URL" in os.environ:
    api_server_url = os.environ["API_SERVER_URL"]

keycloak_connection = None
if "ENABLE_KEYCLOACK" in os.environ:
    keycloak_connection = keycloak_from_json("keycloak_config.json")

# Connect to CardID Table
card_table = CSVCardIdADIDTable(os.environ["RMF_SCAS_CARD_ID_CSV"])


def get_auth_headers(header: str | None = Header(None, alias="Authorization")):
    if header is None:
        raise HTTPException(status_code=401, detail="Authorization header is missing")
    return {"Authorization": header}


@app.post("/compartment_authorization")
async def request_compartment_authorization(
    data: AuthorizationRequest,
    auth_header: dict[str, str] = Depends(get_auth_headers),
) -> AuthorizationResponse:
    authorization_response = get_compartment_authorization(
        card_table,
        keycloak_connection,
        data.cartId,
        data.cardId,
        api_server=api_server_url,
        headers=auth_header
    )
    return authorization_response


@app.post("/cart_status_update")
async def update_cart_status(
    cart_status: CartStatus, auth_header: dict[str, str] = Depends(get_auth_headers)
) -> CartStatus:
    # Process the cart status update
    print(f"Received cart status update: {cart_status}")

    # You would typically save the status to a database

    # Return a success response
    return cart_status  # Echo back the received data


@app.post("/destination_complete")
async def handle_destination_complete(
    data: DestinationComplete, auth_headers: dict[str, str] = Depends(get_auth_headers)
):
    try:
        await notify_rmf_destination_complete(
            data.cartId, data.completedDestination, data.success, api_server_url, auth_headers
        )
        return data  # Echo back the data
    except Exception as e:
        # Proper error handling if communication with RMF fails
        raise HTTPException(
            status_code=500, detail=f"Error communicating with RMF: {str(e)}"
        )


@app.get("/robot_status/{robot_id}")
async def get_status(
    robot_id: str, auth_headers: dict[str, str] = Depends(get_auth_headers)
) -> RobotStatus:
    print(api_server_url)
    try:
        robot_status = await get_robot_status(
            robot_id, api_server=api_server_url, headers=auth_headers
        )
        return robot_status
    except Exception as e:
        # Handle potential errors when communicating with RMF
        raise HTTPException(
            status_code=500, detail=f"Error retrieving robot status from RMF: {str(e)}"
        )


@app.get("/task_status/{task_id}")
async def retrieve_task_status(
    task_id: str, auth_header: dict[str, str] = Depends(get_auth_headers)
) -> TaskStatus:
    try:
        task_status = await get_task_status(
            task_id, api_server=api_server_url, headers=auth_header
        )
        return task_status
    except Exception as e:
        # Handle potential errors when communicating with RMF
        raise HTTPException(
            status_code=500, detail=f"Error retrieving task status from RMF: {str(e)}"
        )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        {"message": str(exc.detail), "code": exc.status_code},
        status_code=exc.status_code,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        {"message": str(exc.detail), "code": exc.status_code},
        status_code=exc.status_code,
    )
