from fastapi import Query, Request
from lnurl import encode as lnurl_encode
from pydantic import BaseModel


class CreateCopilotData(BaseModel):
    user: str | None = Query(None)
    title: str | None = Query(None)
    lnurl_toggle: int = Query(0)
    wallet: str | None = Query(None)
    animation1: str | None = Query(None)
    animation2: str | None = Query(None)
    animation3: str | None = Query(None)
    animation1threshold: int = Query(0)
    animation2threshold: int = Query(0)
    animation3threshold: int = Query(0)
    animation1webhook: str | None = Query(None)
    animation2webhook: str | None = Query(None)
    animation3webhook: str | None = Query(None)
    lnurl_title: str | None = Query(None)
    show_message: int = Query(0)
    show_ack: int = Query(0)
    show_price: str | None = Query(None)
    amount_made: int = Query(0)
    timestamp: int = Query(0)
    fullscreen_cam: int = Query(0)
    iframe_url: str | None = Query(None)


class Copilot(BaseModel):
    id: str
    user: str | None = None
    title: str
    lnurl_toggle: int
    wallet: str | None = None
    animation1: str | None = None
    animation2: str | None = None
    animation3: str | None = None
    animation1threshold: int
    animation2threshold: int
    animation3threshold: int
    animation1webhook: str | None = None
    animation2webhook: str | None = None
    animation3webhook: str | None = None
    lnurl_title: str | None = None
    show_message: int
    show_ack: int
    show_price: str | None = None
    amount_made: int
    timestamp: int
    fullscreen_cam: int
    iframe_url: str | None = None

    def lnurl(self, req: Request) -> str:
        url = str(req.url_for("copilot.lnurl_response", cp_id=self.id))
        return lnurl_encode(url)
