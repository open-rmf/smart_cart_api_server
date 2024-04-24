from fastapi import FastAPI, HTTPException, Depends, Query
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


# Data Models (adjust if needed, based on your RMF integration)
class Location(BaseModel):
    name: str
    compartment: Optional[str] = None

class TaskDestination(BaseModel):
    name: str
    compartment: Optional[str] = None
    action: str  # e.g., "pickup", "dropoff"

class Task(BaseModel):
    taskId: str
    dateTime: datetime
    robotId: str
    fleetId: str 
    cartId: str
    destinations: list[TaskDestination]
    currentLocationIndex: int 
    travellingToIndex: Optional[int] = None
    authorizedDepartures: list[str] 
    unauthorizedDepartures: list[str]
    status: str 

class RobotStatus(BaseModel):
    dateTime: datetime
    robotId: str
    batteryPercentage: int
    robotState: str  # "idle", "working", etc.
    currentLocation: Optional[Location] = None
    travellingTo: Optional[Location] = None
    task: Optional[Task] = None




