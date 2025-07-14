import typing as tp
import uvicorn

from app.utils import (
    TestCaseApiConfig,
)

from .fastapi_init import app


def _run_uvicorn(configuration: dict[str, tp.Any]) -> tp.NoReturn:
    uvicorn.run(
        app,
        **configuration,
    )


def main():
    config = TestCaseApiConfig.load('config.yaml')

    uvicorn_config = {
        "host": config.app.host,
        "port": config.app.port,
    }
    _run_uvicorn(uvicorn_config)


if __name__ == "__main__":
    main()
