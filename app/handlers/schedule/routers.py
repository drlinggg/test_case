"""
FastApi territory routers are defined here.
It is needed to import files which use these routers to initialize handlers.
"""

from fastapi import APIRouter


schedule_router = APIRouter(tags=["schedule"])

all = [
    "schedule_router",
]
