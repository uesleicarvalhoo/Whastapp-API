from fastapi import APIRouter
from fastapi.responses import FileResponse
from starlette.exceptions import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST

from src.schemas.message import MessageInput
from src.talkers import whatsapp_talker

router = APIRouter()


@router.get("/qrcode")
async def qrcode():
    if whatsapp_talker.is_logged:
        raise HTTPException(HTTP_400_BAD_REQUEST, {"message": "Whatsapp is alread logged!"})

    return FileResponse(whatsapp_talker.get_qrcode(), media_type="image/png")


@router.post("/message")
async def message(payload: MessageInput):
    return whatsapp_talker.send_message(payload)
