from fastapi import APIRouter
from fastapi.responses import FileResponse
from starlette.exceptions import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST

from src.database.models import Message
from src.schemas.contact import WhatsappContact
from src.schemas.message import MessageInput, MessageOutput
from src.talkers import whatsapp_talker

router = APIRouter()


@router.get("/qrcode")
async def qrcode():
    if whatsapp_talker.is_logged:
        raise HTTPException(HTTP_400_BAD_REQUEST, {"message": "Whatsapp is alread logged!"})

    return FileResponse(whatsapp_talker.get_qrcode(), media_type="image/png")


@router.post("/message", response_model=MessageOutput)
async def message(payload: MessageInput):
    msg = whatsapp_talker.send_message(payload)

    if msg.success:
        Message.create(1, msg.message)

    return msg


@router.get("/contact", response_model=WhatsappContact)
async def contact():
    return whatsapp_talker.get_contact_info()
