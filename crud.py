from lnbits.db import Database
from lnbits.helpers import urlsafe_short_hash

from .models import Copilot, CreateCopilotData

db = Database("ext_copilot")


async def create_copilot(data: CreateCopilotData) -> Copilot:
    copilot_id = urlsafe_short_hash()
    copilot = Copilot(id=copilot_id, **data.dict())
    await db.insert("copilot.newer_copilots", copilot)
    return copilot


async def update_copilot(copilot: Copilot) -> Copilot:
    await db.update("copilot.newer_copilots", copilot)
    return copilot


async def get_copilot(copilot_id: str) -> Copilot | None:
    return await db.fetchone(
        "SELECT * FROM copilot.newer_copilots WHERE id = :id",
        {"id": copilot_id},
        Copilot,
    )


async def get_copilots(user: str) -> list[Copilot]:
    return await db.fetchall(
        'SELECT * FROM copilot.newer_copilots WHERE "user" = :user',
        {"user": user},
        Copilot,
    )


async def delete_copilot(copilot_id: str) -> None:
    await db.execute(
        "DELETE FROM copilot.newer_copilots WHERE id = :id", {"id": copilot_id}
    )
