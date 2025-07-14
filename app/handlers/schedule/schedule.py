from fastapi import Query, Request, status
from datetime import date

from app.schemas import (
    TimeSlotSchema, 
    TimeIntervalSchema,
    ErrorResponse,
    GatewayErrorResponse,
    ObjectNotFoundResponse,
    TimeoutErrorResponse
)
from app.models import TimeSlot, TimeInterval

from .routers import schedule_router


@schedule_router.get(
    '/schedule/busy_slots',
    response_model=list[TimeIntervalSchema],
    responses={
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
        502: {"model": GatewayErrorResponse, "description": "todo"},
        404: {"model": ObjectNotFoundResponse, "description": "todo"},
        504: {"model": TimeoutErrorResponse, "description": "todo"},
    },
    status_code=status.HTTP_200_OK,
)
async def get_busy_slots(
    request: Request,
    day: date,
):
    schedule_service = request.app.state.schedule_service
    return [interval.to_schema() for interval in await schedule_service.get_busy_intervals(day)]


@schedule_router.get(
    '/schedule/free_slots',
    response_model=list[TimeIntervalSchema],
    responses={
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
        502: {"model": GatewayErrorResponse, "description": "todo"},
        404: {"model": ObjectNotFoundResponse, "description": "todo"},
        504: {"model": TimeoutErrorResponse, "description": "todo"},
    },
    status_code=status.HTTP_200_OK,
)
async def get_free_slots(
    request: Request,
    day: date,
):
    schedule_service = request.app.state.schedule_service
    return [interval.to_schema() for interval in await schedule_service.get_free_intervals(day)]


@schedule_router.get(
    '/schedule/is_slot_free',
    response_model=bool,
    responses={
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
        502: {"model": GatewayErrorResponse, "description": "todo"},
        404: {"model": ObjectNotFoundResponse, "description": "todo"},
        504: {"model": TimeoutErrorResponse, "description": "todo"},
    },
    status_code=status.HTTP_200_OK,
)
async def is_slot_free(
    request: Request,
    time_slot: TimeSlotSchema = Query(..., description="todo"),
):
    schedule_service = request.app.state.schedule_service
    return await schedule_service.is_slot_free(TimeSlot.from_schema(time_slot))


@schedule_router.get(
    '/schedule/find_free_slot',
    response_model=TimeSlotSchema,
    responses={
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
        502: {"model": GatewayErrorResponse, "description": "todo"},
        404: {"model": ObjectNotFoundResponse, "description": "todo"},
        504: {"model": TimeoutErrorResponse, "description": "todo"},
    },
    status_code=status.HTTP_200_OK,
)
async def find_free_slot(
    request: Request,
    start: str = Query(..., description="todo"),
    end: str = Query(..., description="todo"),
):

    time_interval = TimeIntervalSchema(start=start,end=end)
    schedule_service = request.app.state.schedule_service
    return (await schedule_service.find_free_slot(TimeInterval.from_schema(time_interval))).to_schema()

@schedule_router.post(
    '/schedule/hire_me',
    response_model=str,
    status_code=status.HTTP_201_CREATED,
)
async def hire_me(
):
    return 't.me/abanakh'
