"""
All FastApi routers are defined here.

It is needed to import files which use these routers to initialize handlers.
"""

from app.handlers.system import system_router
from app.handlers.schedule import schedule_router


routers_list = [
    schedule_router,
    system_router,
]

all = [
    "routers_list",
]
