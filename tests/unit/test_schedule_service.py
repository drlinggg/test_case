import pytest
from datetime import date, time
from unittest.mock import AsyncMock
from app.models import TimeInterval, TimeSlot
from app.logic import ScheduleService
from app.http_clients import ObjectNotFoundError


@pytest.fixture
def mock_client():
    client = AsyncMock()
    return client


@pytest.fixture
def schedule_service(mock_client):
    return ScheduleService(mock_client)


class TestMergeIntervals:
    def test_empty_list(self, schedule_service):
        assert schedule_service._merge_intervals([]) == []

    def test_single_interval(self, schedule_service):
        intervals = [TimeInterval(time(9, 0), time(10, 0))]
        merged = schedule_service._merge_intervals(intervals)
        assert merged == intervals

    def test_non_overlapping(self, schedule_service):
        intervals = [
            TimeInterval(time(9, 0), time(10, 0)),
            TimeInterval(time(11, 0), time(12, 0))
        ]
        merged = schedule_service._merge_intervals(intervals)
        assert merged == intervals

    def test_overlapping(self, schedule_service):
        intervals = [
            TimeInterval(time(9, 0), time(10, 0)),
            TimeInterval(time(9, 30), time(10, 30))
        ]
        merged = schedule_service._merge_intervals(intervals)
        assert merged == [TimeInterval(time(9, 0), time(10, 30))]

    def test_adjacent(self, schedule_service):
        intervals = [
            TimeInterval(time(9, 0), time(10, 0)),
            TimeInterval(time(10, 0), time(11, 0))
        ]
        merged = schedule_service._merge_intervals(intervals)
        assert merged == [TimeInterval(time(9, 0), time(11, 0))]

    def test_multiple_overlaps(self, schedule_service):
        intervals = [
            TimeInterval(time(9, 0), time(10, 0)),
            TimeInterval(time(9, 30), time(10, 30)),
            TimeInterval(time(10, 15), time(11, 0))
        ]
        merged = schedule_service._merge_intervals(intervals)
        assert merged == [TimeInterval(time(9, 0), time(11, 0))]


class TestGetGapsInIntervals:
    def test_no_busy_intervals(self, schedule_service):
        work_day = TimeInterval(time(9, 0), time(18, 0))
        gaps = schedule_service._get_gaps_in_intervals([], work_day)
        assert gaps == [work_day]

    def test_full_day_busy(self, schedule_service):
        work_day = TimeInterval(time(9, 0), time(18, 0))
        busy = [work_day]
        gaps = schedule_service._get_gaps_in_intervals(busy, work_day)
        assert gaps == []

    def test_single_gap(self, schedule_service):
        work_day = TimeInterval(time(9, 0), time(18, 0))
        busy = [TimeInterval(time(10, 0), time(12, 0))]
        gaps = schedule_service._get_gaps_in_intervals(busy, work_day)
        assert gaps == [
            TimeInterval(time(9, 0), time(10, 0)),
            TimeInterval(time(12, 0), time(18, 0))
        ]

    def test_multiple_gaps(self, schedule_service):
        work_day = TimeInterval(time(8, 0), time(17, 0))
        busy = [
            TimeInterval(time(9, 0), time(10, 0)),
            TimeInterval(time(12, 0), time(13, 0)),
            TimeInterval(time(14, 0), time(15, 0))
        ]
        gaps = schedule_service._get_gaps_in_intervals(busy, work_day)
        assert gaps == [
            TimeInterval(time(8, 0), time(9, 0)),
            TimeInterval(time(10, 0), time(12, 0)),
            TimeInterval(time(13, 0), time(14, 0)),
            TimeInterval(time(15, 0), time(17, 0))
        ]


class TestIsIntervalInIntervals:
    def test_contained(self, schedule_service):
        interval = TimeInterval(time(10, 0), time(11, 0))
        intervals = [TimeInterval(time(9, 0), time(12, 0))]
        assert schedule_service._is_interval_in_intervals(interval, intervals) is True

    def test_not_contained(self, schedule_service):
        interval = TimeInterval(time(8, 0), time(9, 0))
        intervals = [TimeInterval(time(9, 0), time(12, 0))]
        assert schedule_service._is_interval_in_intervals(interval, intervals) is False

    def test_partial_overlap(self, schedule_service):
        interval = TimeInterval(time(8, 0), time(9, 30))
        intervals = [TimeInterval(time(9, 0), time(12, 0))]
        assert schedule_service._is_interval_in_intervals(interval, intervals) is False

    def test_exact_match(self, schedule_service):
        interval = TimeInterval(time(9, 0), time(12, 0))
        intervals = [interval]
        assert schedule_service._is_interval_in_intervals(interval, intervals) is True


@pytest.mark.asyncio
class TestGetBusyIntervals:
    async def test_success(self, schedule_service, mock_client):
        test_date = date(2024, 10, 10)
        mock_client.get_day_timeslots.return_value = [
            TimeInterval(time(11, 0), time(12, 0)),
            TimeInterval(time(9, 30), time(10, 30))
        ]
        
        busy = await schedule_service.get_busy_intervals(test_date)
        assert busy == [
            TimeInterval(time(9, 30), time(10, 30)),
            TimeInterval(time(11, 0), time(12, 0))
        ]
        mock_client.get_day_timeslots.assert_awaited_once_with(test_date)

    async def test_no_timeslots(self, schedule_service, mock_client):
        test_date = date(2024, 10, 10)
        mock_client.get_day_timeslots.return_value = []
        
        busy = await schedule_service.get_busy_intervals(test_date)
        assert busy == []
        mock_client.get_day_timeslots.assert_awaited_once_with(test_date)

    async def test_day_not_found(self, schedule_service, mock_client):
        test_date = date(2024, 10, 10)
        mock_client.get_day_timeslots.side_effect = ObjectNotFoundError("Day not found")
        
        with pytest.raises(ObjectNotFoundError):
            await schedule_service.get_busy_intervals(test_date)


@pytest.mark.asyncio
class TestGetFreeIntervals:
    async def test_success(self, schedule_service, mock_client):
        test_date = date(2024, 10, 10)
        mock_client.get_day_interval.return_value = TimeInterval(time(9, 0), time(18, 0))
        mock_client.get_day_timeslots.return_value = [
            TimeInterval(time(11, 0), time(12, 0))
        ]
        
        free = await schedule_service.get_free_intervals(test_date)
        assert free == [
            TimeInterval(time(9, 0), time(11, 0)),
            TimeInterval(time(12, 0), time(18, 0))
        ]

    async def test_full_day_free(self, schedule_service, mock_client):
        test_date = date(2024, 10, 10)
        mock_client.get_day_interval.return_value = TimeInterval(time(9, 0), time(18, 0))
        mock_client.get_day_timeslots.return_value = []
        
        free = await schedule_service.get_free_intervals(test_date)
        assert free == [TimeInterval(time(9, 0), time(18, 0))]

    async def test_full_day_busy(self, schedule_service, mock_client):
        test_date = date(2024, 10, 10)
        work_day = TimeInterval(time(9, 0), time(18, 0))
        mock_client.get_day_interval.return_value = work_day
        mock_client.get_day_timeslots.return_value = [work_day]
        
        free = await schedule_service.get_free_intervals(test_date)
        assert free == []


@pytest.mark.asyncio
class TestIsSlotFree:
    async def test_free_slot(self, schedule_service, mock_client):
        test_date = date(2024, 10, 10)
        slot = TimeSlot(
            day=test_date,
            interval=TimeInterval(time(10, 0), time(11, 0))
        )
        
        mock_client.get_day_interval.return_value = TimeInterval(time(9, 0), time(18, 0))
        mock_client.get_day_timeslots.return_value = [
            TimeInterval(time(11, 0), time(12, 0))
        ]
        
        assert await schedule_service.is_slot_free(slot) is True

    async def test_busy_slot(self, schedule_service, mock_client):
        test_date = date(2024, 10, 10)
        slot = TimeSlot(
            day=test_date,
            interval=TimeInterval(time(11, 0), time(12, 0))
        )
        
        mock_client.get_day_interval.return_value = TimeInterval(time(9, 0), time(18, 0))
        mock_client.get_day_timeslots.return_value = [
            TimeInterval(time(11, 0), time(12, 0))
        ]
        
        assert await schedule_service.is_slot_free(slot) is False

    async def test_partial_overlap(self, schedule_service, mock_client):
        test_date = date(2024, 10, 10)
        slot = TimeSlot(
            day=test_date,
            interval=TimeInterval(time(11, 30), time(12, 30))
        )
        
        mock_client.get_day_interval.return_value = TimeInterval(time(9, 0), time(18, 0))
        mock_client.get_day_timeslots.return_value = [
            TimeInterval(time(11, 0), time(12, 0))
        ]
        
        assert await schedule_service.is_slot_free(slot) is False


@pytest.mark.asyncio
class TestFindFreeSlot:
    async def test_found_in_first_day(self, schedule_service, mock_client):
        test_date = date(2024, 10, 10)
        interval = TimeInterval(time(10, 0), time(11, 0))
        
        mock_client.get_available_days.return_value = [test_date]
        mock_client.get_day_interval.return_value = TimeInterval(time(9, 0), time(18, 0))
        mock_client.get_day_timeslots.return_value = [
            TimeInterval(time(11, 0), time(12, 0))
        ]
        
        result = await schedule_service.find_free_slot(interval)
        assert result == TimeSlot(day=test_date, interval=interval)

    async def test_found_in_second_day(self, schedule_service, mock_client):
        days = [date(2024, 10, 10), date(2024, 10, 11)]
        interval = TimeInterval(time(10, 0), time(11, 0))
        
        mock_client.get_available_days.return_value = days
        
        mock_client.get_day_interval.side_effect = [
            TimeInterval(time(9, 0), time(18, 0)),
            TimeInterval(time(8, 0), time(17, 0))
        ]
        mock_client.get_day_timeslots.side_effect = [
            [TimeInterval(time(9, 0), time(18, 0))],
            []
        ]
        
        result = await schedule_service.find_free_slot(interval)
        assert result == TimeSlot(day=days[1], interval=interval)

    async def test_not_found(self, schedule_service, mock_client):
        days = [date(2024, 10, 10), date(2024, 10, 11)]
        interval = TimeInterval(time(10, 0), time(11, 0))
        
        mock_client.get_available_days.return_value = days
        mock_client.get_day_interval.return_value = TimeInterval(time(9, 0), time(18, 0))
        mock_client.get_day_timeslots.return_value = [
            TimeInterval(time(9, 0), time(18, 0))
        ]
       
        with pytest.raises(ObjectNotFoundError):
            await schedule_service.find_free_slot(interval)
