import asyncio

import httpx
from lnbits.core.crud import update_payment
from lnbits.core.models import Payment
from lnbits.core.services import websocket_updater
from lnbits.helpers import get_current_extension_name
from lnbits.tasks import register_invoice_listener
from loguru import logger

from .crud import get_copilot


async def wait_for_paid_invoices():
    invoice_queue = asyncio.Queue()
    register_invoice_listener(invoice_queue, get_current_extension_name())

    while True:
        payment = await invoice_queue.get()
        await on_invoice_paid(payment)


async def on_invoice_paid(payment: Payment) -> None:
    if not payment.extra or payment.extra.get("tag") != "copilot":
        # not an copilot invoice
        return

    webhook = None
    data = None
    copilot = await get_copilot(payment.extra.get("copilotid", -1))
    if not copilot:
        logger.warning(
            f"Received payment for unknown copilot {payment.extra.get('copilotid')}"
        )
        return
    if copilot.animation1threshold:
        if int(payment.amount / 1000) >= copilot.animation1threshold:
            data = copilot.animation1
            webhook = copilot.animation1webhook
        if copilot.animation2threshold:
            if int(payment.amount / 1000) >= copilot.animation2threshold:
                data = copilot.animation2
                webhook = copilot.animation1webhook
            if copilot.animation3threshold:
                if int(payment.amount / 1000) >= copilot.animation3threshold:
                    data = copilot.animation3
                    webhook = copilot.animation1webhook
    if webhook:
        async with httpx.AsyncClient() as client:
            try:
                r = await client.post(
                    webhook,
                    json={
                        "payment_hash": payment.payment_hash,
                        "payment_request": payment.bolt11,
                        "amount": payment.amount,
                        "comment": payment.extra.get("comment"),
                    },
                    timeout=40,
                )
                r.raise_for_status()
                payment.extra["wh_status"] = r.status_code
            except (httpx.ConnectError, httpx.RequestError):
                payment.extra["wh_status"] = -1
            finally:
                await update_payment(payment)
    if payment.extra.get("comment"):
        await websocket_updater(
            copilot.id, str(data) + "-" + str(payment.extra.get("comment"))
        )

    await websocket_updater(copilot.id, str(data) + "-none")
