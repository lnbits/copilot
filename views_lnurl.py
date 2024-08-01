import json
from http import HTTPStatus

from fastapi import APIRouter, Query, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse
from lnbits.core.services import create_invoice
from lnurl.types import LnurlPayMetadata

from .crud import get_copilot

copilot_lnurl_router = APIRouter()


@copilot_lnurl_router.get(
    "/lnurl/{cp_id}", response_class=HTMLResponse, name="copilot.lnurl_response"
)
async def lnurl_response(req: Request, cp_id: str):
    cp = await get_copilot(cp_id)
    if not cp:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Copilot not found"
        )

    pay_response = {
        "tag": "payRequest",
        "callback": str(req.url_for("copilot.lnurl_callback", cp_id=cp_id)),
        "metadata": LnurlPayMetadata(json.dumps([["text/plain", str(cp.lnurl_title)]])),
        "maxSendable": 50000000,
        "minSendable": 10000,
    }

    if cp.show_message:
        pay_response["commentAllowed"] = 300
    return json.dumps(pay_response)


@copilot_lnurl_router.get(
    "/lnurl/cb/{cp_id}", response_class=HTMLResponse, name="copilot.lnurl_callback"
)
async def lnurl_callback(
    cp_id: str, amount: str = Query(None), comment: str = Query(None)
):
    cp = await get_copilot(cp_id)
    if not cp:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Copilot not found"
        )
    amount_received = int(amount)

    if amount_received < 10000:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail=(
                "Amount {round(amount_received / 1000)} "
                "is smaller than minimum 10 sats."
            ),
        )
    elif amount_received / 1000 > 10000000:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail=(
                "Amount {round(amount_received / 1000)} "
                "is greater than maximum 50000."
            ),
        )
    comment = ""
    if comment:
        if len(comment or "") > 300:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail=(
                    "Got a comment with {len(comment)} characters, "
                    "but can only accept 300"
                ),
            )
        if len(comment) < 1:
            comment = "none"
    assert cp.wallet, "Copilot wallet not found"
    _, payment_request = await create_invoice(
        wallet_id=cp.wallet,
        amount=int(amount_received / 1000),
        memo=cp.lnurl_title or "",
        unhashed_description=(
            LnurlPayMetadata(json.dumps([["text/plain", str(cp.lnurl_title)]]))
        ).encode(),
        extra={"tag": "copilot", "copilotid": cp.id, "comment": comment},
    )
    pay_response = {"pr": payment_request, "routes": []}
    return json.dumps(pay_response)
