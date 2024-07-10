from fastapi import FastAPI, HTTPException, Depends, Query
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
from smart_cart_api_server.models.task_status import TaskStatus, TaskDestination

# Data Models (adjust if needed, based on your RMF integration)
class RobotStatus(BaseModel):
    dateTime: datetime
    robotId: str
    batteryPercentage: int
    robotState: str  # "idle", "working", etc.
    currentLocation: Optional[TaskDestination] = None
    travellingTo: Optional[TaskDestination] = None
    task: Optional[TaskStatus] = None




