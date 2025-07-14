"""
Models are defined here
"""

from dataclasses import dataclass
from datetime import time, date

from app.schemas import TimeIntervalSchema, TimeSlotSchema
from app.utils import time_to_str, str_to_time


@dataclass(frozen=True)
class TimeInterval:
    start: time
    end: time

    @classmethod
    def from_schema(cls, schema: TimeIntervalSchema) -> "TimeInterval":
        return cls(
            start=str_to_time(schema.start),
            end=str_to_time(schema.end)
        )

    def to_schema(self) -> TimeIntervalSchema:
        return TimeIntervalSchema(
            start=time_to_str(self.start),
            end=time_to_str(self.end)
        )


@dataclass(frozen=True)
class TimeSlot:
    day: date
    interval: TimeInterval

    @classmethod
    def from_schema(cls, schema: TimeSlotSchema) -> "TimeSlot":
        return cls(
            interval=TimeInterval.from_schema(
                TimeIntervalSchema(start=schema.start, end=schema.end)
            ),
            day=schema.day
        )

    def to_schema(self) -> TimeSlotSchema:
        return TimeSlotSchema(
            start=time_to_str(self.interval.start),
            end=time_to_str(self.interval.end),
            day=self.day
        )
