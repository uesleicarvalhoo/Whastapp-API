from typing import Optional

from pydantic import BaseModel


class WhatsappContact(BaseModel):
    name: Optional[str]
    number: Optional[int]
