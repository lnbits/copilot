from typing import List, Optional

from lnbits.db import Database
from lnbits.helpers import insert_query, update_query, urlsafe_short_hash

from .models import Copilot, CreateCopilotData

db = Database("ext_copilot")


async def create_copilot(data: CreateCopilotData) -> Copilot:
    copilot_id = urlsafe_short_hash()
    copilot = Copilot(id=copilot_id, **data.dict())
    await db.execute(
        insert_query("copilot.newer_copilots", copilot),
        copilot.dict(),
    )
    return copilot


async def update_copilot(data: Copilot) -> Copilot:
    copilot = await db.execute(
        update_query("copilot.newer_copilots", data),
        data.dict(),
    )
    return copilot


async def get_copilot(copilot_id: str) -> Optional[Copilot]:
    row = await db.fetchone(
        "SELECT * FROM copilot.newer_copilots WHERE id = :id", {"id": copilot_id}
    )
    return Copilot(**row) if row else None


async def get_copilots(user: str) -> List[Copilot]:
    rows = await db.fetchall(
        'SELECT * FROM copilot.newer_copilots WHERE "user" = :user', {"user": user}
    )
    return [Copilot(**row) for row in rows]


async def delete_copilot(copilot_id: str) -> None:
    await db.execute(
        "DELETE FROM copilot.newer_copilots WHERE id = :id", {"id": copilot_id}
    )
