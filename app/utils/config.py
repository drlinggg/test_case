"""Configs are defined here"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TextIO

import yaml


@dataclass
class AppConfig:
    host: str
    port: int


@dataclass
class ApiConfig:
    """defaut api config"""

    host: str
    port: int


@dataclass
class TestCaseApiConfig:
    app: AppConfig
    schedule_config: ApiConfig

    @classmethod
    def load(cls, file: str | Path | TextIO) -> "TestCaseApiConfig":
        """Import config from the given filename or raise `ValueError` on error."""

        try:
            if isinstance(file, (str, Path)):
                with open(file, "r", encoding="utf-8") as file_r:
                    data = yaml.safe_load(file_r)
            else:
                data = yaml.safe_load(file)

            return cls(
                app=AppConfig(**data.get("app", {})),
                schedule_config=ApiConfig(**data.get("schedule_client", {})),
            )
        except Exception as exc:
            raise ValueError(f"Could not read app config file: {file}") from exc

