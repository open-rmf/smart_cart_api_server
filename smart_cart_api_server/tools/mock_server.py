from smart_cart_api_server.models.token import Credentials, TokenResponse
from smart_cart_api_server.models.cart_authorization import AuthorizationRequest, AuthorizationResponse
from smart_cart_api_server.models.cart_status import CartStatus
from smart_cart_api_server.models.destination_complete import DestinationComplete
from smart_cart_api_server.models.robot_status import RobotStatus
from smart_cart_api_server.models.task_status import TaskStatus
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from datetime import datetime, timedelta
from typing import Annotated, Optional

app = FastAPI()

# Placeholder for your authorization logic
def get_compartment_authorization(cart_id: str, card_id: str) -> AuthorizationResponse:
    # Your logic to determine authorized/unauthorized compartments
    # ...
    return AuthorizationResponse(
        dateTime=datetime.now(),
        cartId=cart_id,
        cardId=card_id,
        authorizedCompartments=["top"],
        unauthorizedCompartments=["bottom", "middle"]
    )

# Authentication (placeholder)
def verify_token(token: str):
    # Your actual token verification logic
    return True

@app.post("/compartment_authorization")
async def request_compartment_authorization(data: AuthorizationRequest, token: Annotated[str, Header()]) -> AuthorizationResponse:
    if not verify_token(token):
        raise HTTPException(status_code=401, detail="Unauthorized")

    authorization_response = get_compartment_authorization(data.cartId, data.cardId)
    return authorization_response

@app.post("/cart_status_update")
async def update_cart_status(cart_status: CartStatus, token: Annotated[str, Header()]) -> CartStatus:
    if not verify_token(token):
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Process the cart status update
    print(f"Received cart status update: {cart_status}")

    # You would typically save the status to a database or
    # forward the message to RMF here

    # Return a success response
    return cart_status  # Echo back the received data

# Placeholder for RMF communication function
def notify_rmf_destination_complete(cart_id: str, destination: str):
    # Your code to communicate with RMF here
    print(f"RMF notified: Cart {cart_id} completed destination {destination}")

@app.post("/destination_complete")
async def handle_destination_complete(data: DestinationComplete, token: Annotated[str, Header()]):
    if not verify_token(token):
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Add logic to validate that completedDestination matches current cart location
    # ... (more on this below)

    try:
        notify_rmf_destination_complete(data.cartId, data.completedDestination)
        return data  # Echo back the data
    except Exception as e:
        # Proper error handling if communication with RMF fails
        raise HTTPException(status_code=500, detail=f"Error communicating with RMF: {str(e)}")

# Placeholder for retrieving data from RMF
def get_robot_status(robot_id: str) -> RobotStatus:
    # Your logic to query RMF for the robot status information
    # ...
    return RobotStatus(
        dateTime=datetime.now(),
        robotId=robot_id,
        batteryPercentage=95,
        robotState="idle",
        # ... rest of the status data
    )

@app.get("/robot_status/{robot_id}")
async def get_status(robot_id: str, token: Annotated[str, Header()]) -> RobotStatus:
    if not verify_token(token):
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        robot_status = get_robot_status(robot_id)
        return robot_status
    except Exception as e:
        # Handle potential errors when communicating with RMF
        raise HTTPException(status_code=500, detail=f"Error retrieving robot status from RMF: {str(e)}")

# Placeholder for RMF communication to query task status
def get_task_status(task_id: str) -> TaskStatus:
    # Your logic to retrieve the status information from RMF
    # ...
    return TaskStatus(
        taskId=task_id,
        dateTime=datetime.now(),
        robotId="AMR_001",
        fleetId="MiR",
        cartId="smart_cart_001",
        destinations=[
            # ... your destination data
        ],
        currentLocationIndex=0,
        travellingToIndex=None,
        authorizedDepartures=["2A DEN"],
        unauthorizedDepartures=["2B ENT"],
        status="underway"
    )



@app.get("/task_status/{task_id}")
async def retrieve_task_status(task_id: str, token: Annotated[str, Header()]) -> TaskStatus:
    if not verify_token(token):
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        task_status = get_task_status(task_id)
        return task_status
    except Exception as e:
        # Handle potential errors when communicating with RMF
        raise HTTPException(status_code=500, detail=f"Error retrieving task status from RMF: {str(e)}")

# Placeholder for RMF authentication function
def authenticate_and_get_token(username: str, password: str) -> Optional[TokenResponse]:
    # Your logic to authenticate with RMF and generate a token
    if username == "admin" and password == "admin":  # Replace with actual authentication
        expiration = datetime.now() + timedelta(days=2)  # Adjust expiration as needed
        return TokenResponse(
            token="sample_jwt_token",
            creationDateTime=datetime.now(),
            expirationDateTime=expiration
        )
    return None  # Authentication failure

@app.post("/get_token")
async def get_token(credentials: Credentials) -> TokenResponse:
    token_data = authenticate_and_get_token(credentials.username, credentials.password)

    if token_data:
        return token_data
    else:
        raise HTTPException(status_code=401, detail="The username or password is incorrect.")


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse({"message": str(exc.detail), "code": exc.status_code}, status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse({"message": str(exc.detail), "code": exc.status_code}, status_code=exc.status_code)
