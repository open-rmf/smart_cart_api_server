from datetime import datetime
from pydantic import BaseModel, Field

# Data Models
class Credentials(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    token: str
    creationDateTime: datetime = Field(..., example="2023-03-14T10:42:46.500403+08:00")
    expirationDateTime: datetime = Field(..., example="2023-03-16T10:42:46.500403+08:00")