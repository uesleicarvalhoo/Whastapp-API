from fastapi import APIRouter
from starlette.responses import JSONResponse

from src.database.models import Conversation

router = APIRouter()


@router.get("/conversation", response_class=JSONResponse)
def get_all_conversations(id: int):
    if conversation := Conversation.get(id=id):
        return conversation.to_dict()

    return {}
