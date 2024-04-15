import asyncio
from loguru import logger

from fastapi import APIRouter

from lnbits.db import Database
from lnbits.helpers import template_renderer
from lnbits.tasks import create_permanent_unique_task

db = Database("ext_copilot")

copilot_static_files = [
    {
        "path": "/copilot/static",
        "name": "copilot_static",
    }
]
copilot_ext: APIRouter = APIRouter(prefix="/copilot", tags=["copilot"])


def copilot_renderer():
    return template_renderer(["copilot/templates"])


from .lnurl import *  # noqa
from .tasks import wait_for_paid_invoices
from .views import *  # noqa
from .views_api import *  # noqa

scheduled_tasks: list[asyncio.Task] = []


def copilot_stop():
    for task in scheduled_tasks:
        try:
            task.cancel()
        except Exception as ex:
            logger.warning(ex)


def copilot_start():
    task = create_permanent_unique_task("ext_copilot", wait_for_paid_invoices)
    scheduled_tasks.append(task)
