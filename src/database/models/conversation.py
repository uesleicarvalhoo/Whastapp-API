from typing import Dict, List

from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.orm import relationship

from src.database import session
from src.database.models import BaseModel
from src.utils.datetime import get_now_datetime


class Conversation(BaseModel):
    __tablename__ = "conversations"
    id = Column("id", Integer, primary_key=True)
    started_at = Column("started_at", DateTime)
    finished_at = Column("finished_at", DateTime)
    messages = relationship("Message", back_populates="conversation")

    @staticmethod
    def create() -> BaseModel:
        model = Conversation(started_at=get_now_datetime())
        model.save()
        return model

    def finish(self) -> None:
        self.finished_at = get_now_datetime()
        self.save()

    def to_dict(self) -> Dict:
        data = super().to_dict()
        data["messages"] = [message.to_dict() for message in self.messages]

        return data

    def get(**kwargs) -> List[Dict]:
        model = session.query(Conversation).filter_by(**kwargs).first()
        model
        return model
