"""
Chat router - handles chat interactions with the agent
"""
from fastapi import APIRouter, Depends
from behflow_agent.builder import AgentBuilder
from app.api.models.models import ChatRequest, ChatResponse
from app.api.models.user import User
from app.api.routers.auth import get_current_user_from_header
from shared.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["chat"])

# Models are defined in `app.api.models.models` and imported above


@router.post("/chat")
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user_from_header)
) -> ChatResponse:
    """
    Main chat endpoint
    Calls the agent service to process user messages
    Requires authentication
    """
    logger.info("Chat request from user=%s session=%s", current_user.username, request.session_id)

    # Build agent instance using factory pattern
    agent = AgentBuilder.build()
    logger.debug("Agent built: %s", type(agent))
    
    # TODO: Implement actual agent invocation logic
    # For now, return a placeholder response with user info
    response_text = f"Hello {current_user.name}, processing your message: {request.message}"
    logger.info("Chat response prepared for user=%s session=%s", current_user.username, request.session_id)
    
    return ChatResponse(
        response=response_text,
        session_id=request.session_id or "new-session"
    )
