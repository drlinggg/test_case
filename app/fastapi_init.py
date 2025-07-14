from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.handlers import routers_list
from app.http_clients import ScheduleClient
from app.logic import ScheduleService
from app.middlewares import (
        ExceptionHandlerMiddleware,
)
from app.utils import TestCaseApiConfig


def get_app(prefix: str = "/api") -> FastAPI:

    desc = "test_case"

    app = FastAPI(
        title="test_case",
        description=desc,
        version="1.0.0 red baron",
        contact={"name": "Banakh Andrei", "email": "uuetsukeu@mail.ru"},
        license_info={"name": "MIT"},
        lifespan=lifespan,
    )


    app.state.config = TestCaseApiConfig.load('config.yaml')

    for route in routers_list:
        app.include_router(route)

    app.add_middleware(
        ExceptionHandlerMiddleware,
        debug = True
    )

    origins = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET"],
        allow_headers=["*"],
    )

    return app


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan function.
    """
    app.state.schedule_service = ScheduleService(
        schedule_client = ScheduleClient(app.state.config.schedule_config)
    )

    yield

app = get_app()
