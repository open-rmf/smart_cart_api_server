from datetime import datetime
from pydantic import BaseModel, Field

# Data model for the request/response
class DestinationComplete(BaseModel):
    dateTime: datetime = Field(..., example="2023-04-25T11:58:21.3666355+08:00")
    cartId: str
    completedDestination: str

