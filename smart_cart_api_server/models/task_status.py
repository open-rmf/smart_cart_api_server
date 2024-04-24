from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List


# Data Models (adjust if needed)
class Location(BaseModel):
    name: str
    compartment: Optional[str] = None

class TaskDestination(BaseModel):
    name: str
    compartment: Optional[str] = None
    action: str  # "pickup", "dropoff"

class TaskStatus(BaseModel):
    taskId: str
    dateTime: datetime
    robotId: str 
    fleetId: str
    cartId: str
    destinations: list[TaskDestination]
    currentLocationIndex: Optional[int] = None
    travellingToIndex: Optional[int] = None
    authorizedDepartures: List[str]
    unauthorizedDepartures: List[str]
    status: str  # "underway", "completed", etc.
