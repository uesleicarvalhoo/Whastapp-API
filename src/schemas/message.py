from typing import Optional

from pydantic import BaseModel

from src.schemas.contact import WhatsappContact


class MessageInput(BaseModel):
    contact: WhatsappContact
    text: Optional[str]
    media: Optional[str]


class MessageOutput(BaseModel):
    success: bool
    reason: Optional[str]
    message: MessageInput
