from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class ChatRequest(BaseModel):
    message: str
    conversation_id: str = "default"
    user_id: str = "user"

class TokenUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class ResponseMetadata(BaseModel):
    processing_time_ms: int
    token_usage: TokenUsage
    trace_id: str
    conversation_turn: int

class ChatResponse(BaseModel):
    response: str
    agents_used: List[str]
    confidence: float
    follow_up_suggestions: List[str] = []
    metadata: ResponseMetadata

class VoteRequest(BaseModel):
    proposal_id: str
    cost: float
    description: str

class VoteResponse(BaseModel):
    proposal_id: str
    outcome: str
    votes: Dict[str, str]
    reasoning: List[str]
