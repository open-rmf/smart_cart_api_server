from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

# Define data models using Pydantic for validation
class Compartment(BaseModel):
    name: str
    isOpen: bool
    isEmpty: bool

class ErrorState(BaseModel):
    code: Optional[int] = None  # Optional for no error
    message: Optional[str] = None

class CartStatus(BaseModel):
    dateTime: datetime = Field(..., example="2023-04-25T11:58:21.3666355+08:00")
    cartId: str
    batteryPercentage: int
    compartments: list[Compartment]
    errorState: ErrorState
