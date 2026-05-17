from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.chat_service import ChatService

router = APIRouter()

chat_service = ChatService()


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1)


@router.post("/chat")
async def chat(request: ChatRequest):

    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    response = chat_service.ask_question(question)

    return response
