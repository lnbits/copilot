import asyncio

from fastapi import APIRouter
from loguru import logger

from .crud import db
from .tasks import wait_for_paid_invoices
from .views import copilot_generic_router
from .views_api import copilot_api_router
from .views_lnurl import copilot_lnurl_router

copilot_static_files = [
    {
        "path": "/copilot/static",
        "name": "copilot_static",
    }
]
copilot_ext: APIRouter = APIRouter(prefix="/copilot", tags=["copilot"])
copilot_ext.include_router(copilot_generic_router)
copilot_ext.include_router(copilot_api_router)
copilot_ext.include_router(copilot_lnurl_router)

scheduled_tasks: list[asyncio.Task] = []


def copilot_stop():
    for task in scheduled_tasks:
        try:
            task.cancel()
        except Exception as ex:
            logger.warning(ex)


def copilot_start():
    from lnbits.tasks import create_permanent_unique_task

    task = create_permanent_unique_task("ext_copilot", wait_for_paid_invoices)
    scheduled_tasks.append(task)


__all__ = ["copilot_ext", "copilot_start", "copilot_static_files", "copilot_stop", "db"]
