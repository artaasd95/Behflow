"""
Chat router - handles chat interactions with the agent
"""
from fastapi import APIRouter
from behflow_agent.builder import AgentBuilder
from app.api.models.models import ChatRequest, ChatResponse

router = APIRouter(tags=["chat"])

# Models are defined in `app.api.models.models` and imported above


@router.post("/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Main chat endpoint
    Calls the agent service to process user messages
    """
    # Build agent instance using factory pattern
    agent = AgentBuilder.build()
    
    # TODO: Implement actual agent invocation logic
    # For now, return a placeholder response
    response_text = "Agent response placeholder"
    
    return ChatResponse(
        response=response_text,
        session_id=request.session_id or "new-session"
    )
