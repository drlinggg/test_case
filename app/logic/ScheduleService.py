from typing import List
from datetime import date

from app.http_clients import (
    ScheduleClient,
    ObjectNotFoundError
)
from app.models import TimeInterval, TimeSlot


class ScheduleService:

    def __init__(
        self,
        schedule_client: ScheduleClient
    ):
        self.schedule_client = schedule_client

    def _merge_intervals(self, intervals: List[TimeInterval]) -> List[TimeInterval]:
        sorted_intervals = sorted(intervals, key=lambda x: x.start)

        merged = []
        if not sorted_intervals:
            return merged

        current_start = sorted_intervals[0].start
        current_end = sorted_intervals[0].end

        for slot in sorted_intervals[1:]:
            if slot.start <= current_end:
                if slot.end > current_end:
                    current_end = slot.end
            else:
                merged.append(TimeInterval(start=current_start, end=current_end))
                current_start = slot.start
                current_end = slot.end
    
        merged.append(TimeInterval(start=current_start, end=current_end))
        return merged
    
    def _get_gaps_in_intervals(
        self, 
        intervals: List[TimeInterval], 
        time_range: TimeInterval
    ) -> List[TimeInterval]:
        gaps = []
        prev_end = time_range.start

        for interval in intervals:
            if prev_end < interval.start:
                gaps.append(TimeInterval(start=prev_end, end=interval.start))
            prev_end = interval.end
        if prev_end < time_range.end:
            gaps.append(TimeInterval(start=prev_end, end=time_range.end))

        return gaps

    def _find_gap_in_intervals(
        self, 
        intervals: List[TimeInterval], 
        time_range: TimeInterval,
        time_duration: int,
    ) -> TimeInterval:
        pass

    def _is_interval_in_intervals(
        self,
        current_interval: TimeInterval,
        intervals: List[TimeInterval], 
    ):
        for interval in intervals:
            if interval.start <= current_interval.start and interval.end >= current_interval.end:
                return True
        return False

    async def get_busy_intervals(self, day: date) -> List[TimeInterval]:
        time_intervals = await self.schedule_client.get_day_timeslots(day)
        return self._merge_intervals(time_intervals)


    async def get_free_intervals(self, day: date) -> List[TimeInterval]:
        busy_intervals = await self.get_busy_intervals(day)
        day_interval = await self.schedule_client.get_day_interval(day)
        return self._get_gaps_in_intervals(busy_intervals, day_interval)
        

    async def is_slot_free(self, slot: TimeSlot) -> bool:
        free_intervals = await self.get_free_intervals(slot.day)
        return self._is_interval_in_intervals(current_interval=slot.interval, intervals=free_intervals)
        

    async def find_free_slot(self, time_interval: TimeInterval):
        available_days = await self.schedule_client.get_available_days()
        for day in available_days:
            free_intervals = await self.get_free_intervals(day)
            if self._is_interval_in_intervals(
                time_interval,
                free_intervals
            ):
                return TimeSlot(day=day, interval=time_interval)
        raise ObjectNotFoundError(f"No such free time interval {time_interval}")
