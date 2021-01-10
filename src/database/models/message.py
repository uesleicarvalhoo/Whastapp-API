from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.database.models import BaseModel
from src.schemas.message import MessageInput
from src.utils.datetime import get_now_datetime


class Message(BaseModel):
    __tablename__ = "messages"
    id = Column("id", Integer, primary_key=True)
    text = Column("text", String(1000))
    contact_number = Column("contact_number", String(13))
    media = Column("media", String(100))
    created_at = Column("created_at", DateTime, default=get_now_datetime)
    updated_at = Column("updated_at", DateTime, onupdate=get_now_datetime())
    conversation_id = Column("conversation_id", Integer, ForeignKey("conversations.id"), nullable=False)

    conversation = relationship("Conversation", back_populates="messages")

    @staticmethod
    def create(conversation_id: int, msg: MessageInput) -> BaseModel:
        model = Message(
            text=msg.text, contact_number=msg.contact.number, media=msg.media, conversation_id=conversation_id
        )

        model.save()

        return model
