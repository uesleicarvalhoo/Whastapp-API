from datetime import date, datetime, time
from typing import Dict

from sqlalchemy.ext.declarative import declarative_base

from src.database import session

DeclarativeModel = declarative_base()


class BaseModel(DeclarativeModel):
    __abstract__ = True
    editable_fields = []

    def populate_object(self, **data: dict) -> None:
        columns = self.__table__.columns.keys()
        for key, value in data.items():
            if key in columns:
                setattr(self, key, value)

    def to_dict(self) -> Dict:
        return {col: getattr(self, col) for col in self.__table__.columns.keys()}

    def to_json(self) -> Dict:
        data = self.to_dict()

        for col, value in data.items():
            if isinstance(value, datetime) or isinstance(value, date) or isinstance(value, time):
                data[col] = value.isoformat()

        return data

    def save(self) -> None:
        session.add(self)
        session.commit()

    def delete(self) -> None:
        session.delete(self)
        session.commit()

    def update(self, **data: Dict) -> None:
        for col in data.copy().keys():
            if col not in self.editable_fields:
                data.pop(col, None)

        self.populate_object(**data)
