"""
Response models are defined here
"""

from datetime import time, date
import re

from pydantic import BaseModel, Field, field_validator

class TimeIntervalSchema(BaseModel):
    start: str = Field(default="12:00")
    end: str = Field(default="13:00")

    @field_validator('start', 'end')
    def validate_time_format(cls, v):
        if not re.match(r"^([0-1][0-9]|2[0-3]):[0-5][0-9]$", v):
            raise ValueError("Invalid time format. Use HH:MM")
        return v


class TimeSlotSchema(TimeIntervalSchema):
    day: date = Field(default=date.today().isoformat())
