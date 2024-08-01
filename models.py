from typing import Optional

from fastapi import Query, Request
from lnbits.lnurl import encode as lnurl_encode
from pydantic import BaseModel


class CreateCopilotData(BaseModel):
    user: str = Query(None)
    title: str = Query(None)
    lnurl_toggle: int = Query(0)
    wallet: str = Query(None)
    animation1: str = Query(None)
    animation2: str = Query(None)
    animation3: str = Query(None)
    animation1threshold: int = Query(0)
    animation2threshold: int = Query(0)
    animation3threshold: int = Query(0)
    animation1webhook: str = Query(None)
    animation2webhook: str = Query(None)
    animation3webhook: str = Query(None)
    lnurl_title: str = Query(None)
    show_message: int = Query(0)
    show_ack: int = Query(0)
    show_price: str = Query(None)
    amount_made: int = Query(0)
    timestamp: int = Query(0)
    fullscreen_cam: int = Query(0)
    iframe_url: str = Query(None)


class Copilot(BaseModel):
    id: str
    user: Optional[str]
    title: str
    lnurl_toggle: int
    wallet: Optional[str]
    animation1: Optional[str]
    animation2: Optional[str]
    animation3: Optional[str]
    animation1threshold: int
    animation2threshold: int
    animation3threshold: int
    animation1webhook: Optional[str]
    animation2webhook: Optional[str]
    animation3webhook: Optional[str]
    lnurl_title: Optional[str]
    show_message: int
    show_ack: int
    show_price: Optional[str]
    amount_made: int
    timestamp: int
    fullscreen_cam: int
    iframe_url: Optional[str]

    def lnurl(self, req: Request) -> str:
        url = str(req.url_for("copilot.lnurl_response", cp_id=self.id))
        return lnurl_encode(url)
