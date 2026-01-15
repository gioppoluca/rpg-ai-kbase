from __future__ import annotations

import time
import uuid

from fastapi import APIRouter, Depends

from app.api.deps import require_api_key
from app.core.config import settings
from app.models.openai import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ListModelsResponse,
    OpenAIModel,
    ChatCompletionChoice,
    ChatCompletionChoiceMessage,
)
from app.rag.pipeline import answer

router = APIRouter(tags=["openai"])


@router.get("/v1/models", response_model=ListModelsResponse)
async def list_models(_=Depends(require_api_key)):
    # The model id shown in Open WebUI's model picker.
    return ListModelsResponse(data=[OpenAIModel(id="local-rag")])


@router.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(req: ChatCompletionRequest, _=Depends(require_api_key)):
    # Use the last user message as the query.
    user_msgs = [m.content for m in req.messages if m.role == "user"]
    query = user_msgs[-1] if user_msgs else ""

    rag = await answer(query)
    content = rag["answer"]

    return ChatCompletionResponse(
        id=f"chatcmpl-{uuid.uuid4().hex}",
        created=int(time.time()),
        model=req.model,
        choices=[
            ChatCompletionChoice(
                index=0,
                message=ChatCompletionChoiceMessage(content=content),
                finish_reason="stop",
            )
        ],
        usage={},
    )
