from http import HTTPStatus
from typing import Optional

from fastapi import Depends, Query, Request
from fastapi.exceptions import HTTPException

from lnbits.core.services import websocketUpdater
from lnbits.decorators import WalletTypeInfo, get_key_type, require_admin_key

from . import copilot_ext
from .crud import (
    create_copilot,
    delete_copilot,
    get_copilot,
    get_copilots,
    update_copilot,
)
from .models import CreateCopilotData, Copilot

#######################COPILOT##########################


@copilot_ext.get("/api/v1/copilot")
async def api_copilots_retrieve(wallet: WalletTypeInfo = Depends(get_key_type)):
    wallet_user = wallet.wallet.user
    copilots = [copilot.dict() for copilot in await get_copilots(wallet_user)]
    try:
        return copilots
    except:
        raise HTTPException(status_code=HTTPStatus.NO_CONTENT, detail="No copilots")


@copilot_ext.get("/api/v1/copilot/{copilot_id}", dependencies=[Depends(get_key_type)])
async def api_copilot_retrieve(
    req: Request,
    copilot_id: str,
):
    copilot = await get_copilot(copilot_id)
    if not copilot:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Copilot not found"
        )
    if not copilot.lnurl_toggle:
        return copilot
    return {**copilot.dict(), **{"lnurl": copilot.lnurl(req)}}


@copilot_ext.post("/api/v1/copilot")
async def api_copilot_create(
    data: CreateCopilotData,
    wallet: WalletTypeInfo = Depends(require_admin_key),
) -> Copilot:
    data.user = wallet.wallet.user
    data.wallet = wallet.wallet.id
    return await create_copilot(data, inkey=wallet.wallet.inkey)


@copilot_ext.put("/api/v1/copilot/{copilot_id}")
async def api_copilot_update(
    data: CreateCopilotData,
    copilot_id: str,
    wallet: WalletTypeInfo = Depends(require_admin_key),
) -> Copilot:
    copilot = await get_copilot(copilot_id)
    if not copilot:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Copilot does not exist"
        )

    data.user = wallet.wallet.user
    data.wallet = wallet.wallet.id
    return await update_copilot(data, copilot_id=copilot_id)


@copilot_ext.delete("/api/v1/copilot/{copilot_id}", dependencies=[Depends(require_admin_key)])
async def api_copilot_delete(
    copilot_id: str,
):
    copilot = await get_copilot(copilot_id)

    if not copilot:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Copilot does not exist"
        )

    await delete_copilot(copilot_id)

    return "", HTTPStatus.NO_CONTENT


@copilot_ext.get("/api/v1/copilot/ws/{copilot_id}/{comment}/{data}")
async def api_copilot_ws_relay(copilot_id: str, comment: str, data: str):
    copilot = await get_copilot(copilot_id)
    if not copilot:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Copilot does not exist"
        )
    try:
        await websocketUpdater(copilot_id, str(data) + "-" + str(comment))
    except:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Not your copilot")
    return ""
