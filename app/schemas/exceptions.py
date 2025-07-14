"""
Response models for errors are defined here
"""

from typing import Optional
from pydantic import BaseModel, Field

class ErrorResponse(BaseModel):
    detail: str = "Exception occurred"
    error: Optional[str] = None
    error_type: Optional[str] = None
    path: Optional[str] = None
    trace: Optional[str] = None

class GatewayErrorResponse(BaseModel):
    detail: str = Field(default="did not get a response from the upstream server in order to complete the request")


class TimeoutErrorResponse(BaseModel):
    detail: str = Field(
        default="did not get a response in time from the upstream server in order to complete the request")


class ObjectNotFoundResponse(BaseModel):
    detail: str = Field(
        default="couldnt find something:("
    )
