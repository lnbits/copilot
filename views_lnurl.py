import json

from fastapi import APIRouter, Query, Request
from lnbits.core.services import create_invoice
from lnurl import (
    CallbackUrl,
    LightningInvoice,
    LnurlErrorResponse,
    LnurlPayActionResponse,
    LnurlPayMetadata,
    LnurlPayResponse,
    MilliSatoshi,
)
from pydantic import parse_obj_as

from .crud import get_copilot

copilot_lnurl_router = APIRouter()


@copilot_lnurl_router.get("/lnurl/{cp_id}", name="copilot.lnurl_response")
async def lnurl_response(
    req: Request, cp_id: str
) -> LnurlPayResponse | LnurlErrorResponse:
    cp = await get_copilot(cp_id)
    if not cp:
        return LnurlErrorResponse(reason="Copilot not found.")

    callback_url = parse_obj_as(
        CallbackUrl, str(req.url_for("copilot.lnurl_callback", cp_id=cp_id))
    )

    pay_response = LnurlPayResponse(
        callback=callback_url,
        metadata=LnurlPayMetadata(json.dumps([["text/plain", str(cp.lnurl_title)]])),
        minSendable=MilliSatoshi(10000),
        maxSendable=MilliSatoshi(50000000),
    )

    if cp.show_message:
        pay_response.commentAllowed = 300

    return pay_response


@copilot_lnurl_router.get("/lnurl/cb/{cp_id}", name="copilot.lnurl_callback")
async def lnurl_callback(
    cp_id: str, amount: str = Query(None), comment: str = Query(None)
) -> LnurlPayActionResponse | LnurlErrorResponse:
    cp = await get_copilot(cp_id)
    if not cp:
        return LnurlErrorResponse(reason="Copilot not found.")

    amount_received = int(amount)
    amount_rounded = round(amount_received / 1000)
    if amount_received < 10000:
        return LnurlErrorResponse(
            reason=f"Amount {amount_rounded} is smaller than minimum 10 sats."
        )
    elif amount_received / 1000 > 10000000:
        return LnurlErrorResponse(
            reason=f"Amount {amount_rounded} is greater than maximum 10000000 sats."
        )

    if comment:
        if len(comment) > 300:
            return LnurlErrorResponse(
                reason=(
                    f"Got a comment with {len(comment)} characters, "
                    "but can only accept 300"
                )
            )

    payment = await create_invoice(
        wallet_id=cp.wallet,
        amount=int(amount_received / 1000),
        memo=cp.lnurl_title or "",
        unhashed_description=(
            LnurlPayMetadata(json.dumps([["text/plain", str(cp.lnurl_title)]]))
        ).encode(),
        extra={"tag": "copilot", "copilotid": cp.id, "comment": comment},
    )

    invoice = parse_obj_as(LightningInvoice, payment.bolt11)
    return LnurlPayActionResponse(pr=invoice)
