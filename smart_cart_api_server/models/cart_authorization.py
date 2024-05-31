from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

# Data Models
class AuthorizationRequest(BaseModel):
    dateTime: datetime  = Field(..., example="2023-04-25T11:58:21.3666355+08:00")
    cartId: str
    cardId: str

class AuthorizationResponse(BaseModel):
    dateTime: datetime
    cartId: str
    cardId: str
    authorizedCompartments: List[str] = []
    unauthorizedCompartments: List[str] = []
