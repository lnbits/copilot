from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from lnbits.core.models import User
from lnbits.decorators import check_user_exists
from lnbits.helpers import template_renderer

copilot_generic_router: APIRouter = APIRouter()


def copilot_renderer():
    return template_renderer(["copilot/templates"])


templates = Jinja2Templates(directory="templates")


@copilot_generic_router.get("/", response_class=HTMLResponse)
async def index(request: Request, user: User = Depends(check_user_exists)):
    return copilot_renderer().TemplateResponse(
        "copilot/index.html", {"request": request, "user": user.dict()}
    )


@copilot_generic_router.get("/cp/", response_class=HTMLResponse)
async def compose(request: Request):
    return copilot_renderer().TemplateResponse(
        "copilot/compose.html", {"request": request}
    )


@copilot_generic_router.get("/pn/", response_class=HTMLResponse)
async def panel(request: Request):
    return copilot_renderer().TemplateResponse(
        "copilot/panel.html", {"request": request}
    )


@copilot_generic_router.get("/chat/{chat_id}", response_class=HTMLResponse)
async def chat(request: Request, chat_id):
    return copilot_renderer().TemplateResponse(
        "copilot/chat.html", {"request": request, "chat_id": chat_id}
    )
