from http import HTTPStatus

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from lnbits.core.models import WalletTypeInfo
from lnbits.core.services import websocket_updater
from lnbits.decorators import require_admin_key, require_invoice_key

from .crud import (
    create_copilot,
    delete_copilot,
    get_copilot,
    get_copilots,
    update_copilot,
)
from .models import Copilot, CreateCopilotData

copilot_api_router = APIRouter()


@copilot_api_router.get("/api/v1/copilot")
async def api_copilots_retrieve(wallet: WalletTypeInfo = Depends(require_invoice_key)):
    wallet_user = wallet.wallet.user
    copilots = await get_copilots(wallet_user)
    return copilots


@copilot_api_router.get(
    "/api/v1/copilot/{copilot_id}", dependencies=[Depends(require_invoice_key)]
)
async def api_copilot_retrieve(copilot_id: str) -> Copilot:
    copilot = await get_copilot(copilot_id)
    if not copilot:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Copilot not found."
        )

    return copilot


@copilot_api_router.post("/api/v1/copilot")
async def api_copilot_create(
    data: CreateCopilotData,
    wallet: WalletTypeInfo = Depends(require_admin_key),
) -> Copilot:
    data.user = wallet.wallet.user
    data.wallet = wallet.wallet.id
    return await create_copilot(data)


@copilot_api_router.put("/api/v1/copilot/{copilot_id}")
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
    for key, value in data.dict().items():
        if value:
            setattr(copilot, key, value)
    return await update_copilot(copilot)


@copilot_api_router.delete(
    "/api/v1/copilot/{copilot_id}", dependencies=[Depends(require_admin_key)]
)
async def api_copilot_delete(copilot_id: str) -> None:
    copilot = await get_copilot(copilot_id)
    if not copilot:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Copilot does not exist"
        )

    await delete_copilot(copilot_id)


@copilot_api_router.get("/api/v1/copilot/ws/{copilot_id}/{comment}/{data}")
async def api_copilot_ws_relay(copilot_id: str, comment: str, data: str):
    copilot = await get_copilot(copilot_id)
    if not copilot:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Copilot does not exist"
        )
    try:
        await websocket_updater(copilot_id, f"{data} - {comment}")
    except Exception as exc:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Not your copilot"
        ) from exc
    return ""
