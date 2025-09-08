from datetime import datetime, timezone

from fastapi import Query
from pydantic import BaseModel, Field


class CreateCopilotData(BaseModel):
    user: str | None = None
    title: str | None = None
    lnurl_toggle: int | None = 0
    wallet: str | None = None
    animation1: str | None = None
    animation2: str | None = None
    animation3: str | None = None
    animation1threshold: int | None = 0
    animation2threshold: int | None = 0
    animation3threshold: int | None = 0
    animation1webhook: str | None = None
    animation2webhook: str | None = None
    animation3webhook: str | None = None
    lnurl_title: str | None = None
    show_message: int | None = 0
    show_ack: int | None = 0
    show_price: str | None = None
    amount_made: int | None = 0
    timestamp: datetime | None = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    fullscreen_cam: int | None = 0
    iframe_url: str | None = None


class Copilot(BaseModel):
    id: str
    user: str | None
    title: str
    lnurl_toggle: int
    wallet: str
    animation1: str | None
    animation2: str | None
    animation3: str | None
    animation1threshold: int
    animation2threshold: int
    animation3threshold: int
    animation1webhook: str | None
    animation2webhook: str | None
    animation3webhook: str | None
    lnurl_title: str | None
    show_message: int
    show_ack: int
    show_price: str | None
    amount_made: int
    timestamp: datetime
    fullscreen_cam: int
    iframe_url: str | None
