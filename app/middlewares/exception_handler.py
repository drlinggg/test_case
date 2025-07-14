"""Exception handling middleware is defined here."""

import itertools
import traceback

import structlog
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.http_clients import (
    APIConnectionError,
    APITimeoutError,
    ObjectNotFoundError,
)
from app.schemas import (
    ErrorResponse,
    GatewayErrorResponse,
    TimeoutErrorResponse,
    ObjectNotFoundResponse
)


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    """
    This fastapi middleware is used to catch either the low python exceptions
    or the http_client's ones and make valid returns for unexpected situations
    such as lost connection
    """

    def __init__(self, app, debug: bool):
        """
        Passing debug as a list with single element is a hack to be able to change the value
        on the application startup.
        """
        super().__init__(app)
        self._debug = debug

    async def dispatch(self, request: Request, call_next):
        logger = structlog.get_logger()
        try:
            return await call_next(request)

        except APIConnectionError as exc:
            logger.error(f"status: 502, detail: {{content: Couldn't connect to upstream server, info: { {str(exc)} }")
            return JSONResponse(
                content=GatewayErrorResponse(
                    detail=f"Couldn't connect to upstream server, info: { {str(exc)} }"
                ).dict(),
                status_code=502,
            )

        except APITimeoutError as exc:
            logger.error(
                f"status: 504, detail: {{content: Didn't receive a timely response from upstream server, info: {str(exc)}}}"
            )
            return JSONResponse(
                content=TimeoutErrorResponse(
                    detail=f"Didn't receive a timely response from upstream server, info: {str(exc)}"
                ).dict(),
                status_code=504,
            )

        except ObjectNotFoundError as exc:
            logger.error(
                f"status: 404, detail: {{ "
                f"content: Given object or its data is not found, "
                f"therefore further calculations are impossible, "
                f"info: {str(exc)}}}"
            )
            return JSONResponse(
                content=ObjectNotFoundResponse(
                    detail=f"couldn't find object or its data, detail: {{ {str(exc)} }}"
                ).dict(),
                status_code=404
            )

        except Exception as exc:  # pylint: disable=broad-except
            trace = list(
                itertools.chain.from_iterable(map(lambda x: x.split("\n"), traceback.format_tb(exc.__traceback__)))
            )

            logger.error(
                f"status: 500, error: {str(exc)}, error_type: {str(type(exc))}, path: {request.url.query}, trace: {trace}"
            )

            if self._debug:
                return JSONResponse(
                    content=ErrorResponse(
                        error=str(exc), error_type=str(type(exc)), path=request.url.path, trace=" ".join(trace)
                    ).dict(),
                    status_code=500,
                )

            return JSONResponse(content=ErrorResponse().dict(), status_code=500)
