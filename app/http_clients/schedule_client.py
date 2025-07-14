from datetime import date
import pandas as pd
from typing import List

from .exceptions import (
    ObjectNotFoundError,
    handle_exceptions,
)
from .http_client import (
    BaseClient,
)
from .requests import (
    handle_get_request,
)
from app.models import TimeInterval
from app.utils import str_to_time


class ScheduleClient(BaseClient):

    def __post_init__(self):
        if not (self.config.host.startswith("http")):
            self.config.host = f"http://{self.config.host}"

    def __str__(self):
        return "ScheduleClient"

    @handle_exceptions
    async def get_day_timeslots(self, day: date) -> list[TimeInterval]:
        url = f"{self.config.host}:{self.config.port}/test-task/"
        headers = {"accept": "application/json"}
        data = await handle_get_request(url=url, headers=headers)

        if not data or 'days' not in data:
            raise ObjectNotFoundError(f"No data available for date {date}")


        date_str = day.isoformat()
        day_id = None
        for d in data['days']:
            if d['date'] == date_str:
                day_id = d['id']
                break
    
        if day_id is None:
            raise ObjectNotFoundError(f"No such day in schedule {str(day)}")

        timeslots_df = pd.DataFrame(data['timeslots'])
        filtered_df = timeslots_df[timeslots_df['day_id'] == day_id][['start', 'end']]

        time_intervals = [
            TimeInterval(start=str_to_time(row['start']), end=str_to_time(row['end']))
            for _, row in filtered_df.iterrows()
        ]

        return time_intervals


    @handle_exceptions
    async def get_day_interval(self, day: date) -> TimeInterval:
        url = f"{self.config.host}:{self.config.port}/test-task/"
        headers = {"accept": "application/json"}
        data = await handle_get_request(url=url, headers=headers)
    
        if not data or 'days' not in data:
            raise ObjectNotFoundError(f"No data available for date {day}")
    
        date_str = day.isoformat()
    
        for working_day in data['days']:
            if working_day['date'] == date_str:
                return TimeInterval(
                    start=str_to_time(working_day['start']),
                    end=str_to_time(working_day['end'])
                )
    
        raise ObjectNotFoundError(f"No work hours found for date {day}")

    @handle_exceptions
    async def get_available_days(self) -> List[date]:
        url = f"{self.config.host}:{self.config.port}/test-task/"
        headers = {"accept": "application/json"}
        data = await handle_get_request(url=url, headers=headers)
    
        if not data or 'days' not in data:
            raise ObjectNotFoundError(f"No data available")

        days_df = pd.DataFrame(data['days'])
        days_df['date'] = pd.to_datetime(days_df['date']).dt.date
        unique_dates = days_df['date'].unique().tolist()
        unique_dates.sort()
        return unique_dates
