import os
import logging
import asyncio
import uuid
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from fastmcp import FastMCP

# Import Core Client Logic
from src.core.agent_registry import AGENT_REGISTRY, get_agent_path
from src.core.mcp_client import AgentClient
from src.services.llm_service import (
    get_llm_service,
    Message as LLMMessage,
    LLMService,
    LLMConfig,
    LLMProvider
)
from src.core.governance import (
    AUTO_APPROVE_LIMIT,
    HUMAN_REVIEW_LIMIT,
    PENTARCHY_AGENTS,
    calculate_vote_outcome,
    get_risk_level,
    VoteType
)

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("zeus-agent")

# --- Data Models (from Specification) ---


class UserContext(BaseModel):
    """User context for personalization."""
    user_id: str
    tenant_id: str
    roles: List[str]
    preferences: Dict[str, Any] = {}


class ZeusInput(BaseModel):
    """Input schema for Zeus orchestrator."""
    user_message: str
    conversation_id: str
    user_context: Optional[UserContext] = None
    routing_hints: Optional[List[str]] = None
    # Literal["low", "normal", "high", "critical"] = "normal"
    priority: str = "normal"


class TokenUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ResponseMetadata(BaseModel):
    """Metadata about response generation."""
    processing_time_ms: int
    token_usage: TokenUsage
    trace_id: str
    conversation_turn: int


class ZeusOutput(BaseModel):
    """Output schema for Zeus orchestrator."""
    response: str
    agents_used: List[str]
    confidence: float
    follow_up_suggestions: List[str] = []
    metadata: ResponseMetadata

# --- Agent Implementation ---


class ZeusAgent:
    def __init__(self):
        self.name = "zeus"
        self.version = "2.0.0"
        self.mcp = FastMCP(self.name)
        self.clients: Dict[str, AgentClient] = {}
        self.llm = get_llm_service()

        # Initialize Simple LLM (HuggingFace) for routing
        hf_key = os.getenv("HUGGINGFACE_API_KEY")
        hf_endpoint = os.getenv("HUGGINGFACE_ENDPOINT_URL")

        if hf_key and hf_endpoint:
            try:
                # Check if it's an OpenAI compatible endpoint (vLLM/TGI)
                # For now, we assume it is if it's a dedicated endpoint
                base_url = hf_endpoint
                if not base_url.endswith("/v1"):
                    base_url = f"{base_url}/v1"

                simple_config = LLMConfig(
                    provider=LLMProvider.OPENAI,
                    model=os.getenv("HUGGINGFACE_MODEL",
                                    "mistralai/Mistral-7B-Instruct-v0.3"),
                    api_key=hf_key,
                    base_url=base_url,
                    max_tokens=1024
                )
                self.simple_llm = LLMService(config=simple_config)
                logger.info(
                    "Initialized secondary LLM (HuggingFace) for simple tasks")
            except Exception as e:
                logger.warning(f"Failed to initialize secondary LLM: {e}")
                self.simple_llm = self.llm
        else:
            self.simple_llm = self.llm

        # Configure routing logic
        # Complex reasoning -> OpenAI/Anthropic
        # Simple tasks -> Local/HF
        self.routing_config = {
            "complex": ["openai", "anthropic"],
            "simple": ["huggingface", "ollama"]
        }

        self.conversation_history: Dict[str, List[LLMMessage]] = {}
        logger.info(f"Initializing {self.name} Agent v{self.version}")

        # System prompt for Zeus
        self.system_prompt = """You are Zeus, the master orchestrator of KOSMOS - an AI-native enterprise operating system.

Your role is to:
1. Understand user intent and route requests to appropriate specialist agents
2. Coordinate multi-agent workflows for complex tasks
3. Synthesize responses from multiple agents into coherent answers
4. Make autonomous decisions for routine operations ($0-$50)
5. Facilitate Pentarchy voting for significant decisions ($50-$100)
6. Escalate to human review for major decisions (>$100)

Available specialist agents:
- Hermes: Communications, notifications, messaging
- AEGIS: Security, compliance, access control
- Chronos: Scheduling, time management, reminders
- Athena: Knowledge retrieval, document search, RAG
- Memorix: Memory, context management, history
- Hephaestus: DevOps, infrastructure, automation
- Nur Prometheus: Analytics, reporting, metrics
- Iris: Visualization, dashboards, UI generation
- Hestia: Personal preferences, home automation
- Morpheus: Forecasting, simulation, prediction

Be helpful, concise, and proactive. When uncertain, ask clarifying questions.
Always explain your reasoning when delegating to other agents."""

        # Intent-to-agent routing map
        self.intent_routing = {
            "hermes": ["email", "message", "notification", "communicate", "send", "notify", "alert"],
            "aegis": ["security", "permission", "access", "password", "auth", "compliance", "audit"],
            "chronos": ["schedule", "calendar", "reminder", "meeting", "time", "deadline", "event"],
            "athena": ["search", "find", "document", "knowledge", "wiki", "information", "research"],
            "memorix": ["remember", "history", "context", "previous", "recall", "memory"],
            "hephaestus": ["deploy", "server", "infrastructure", "build", "devops", "pipeline", "ci/cd"],
            "nur_prometheus": ["analytics", "metrics", "report", "dashboard", "stats", "performance"],
            "iris": ["visualize", "chart", "graph", "ui", "display", "show"],
            "hestia": ["preference", "setting", "home", "personal", "customize"],
            "morpheus": ["predict", "forecast", "simulate", "future", "trend", "projection"]
        }

        # Register tools
        self.mcp.tool()(self.process_message)
        self.mcp.tool()(self.delegate_task)
        self.mcp.tool()(self.list_available_agents)
        self.mcp.tool()(self.conduct_pentarchy_vote)

    def _detect_intent(self, message: str) -> List[str]:
        """Detect which agents should handle the message based on intent."""
        message_lower = message.lower()
        matched_agents = []

        for agent, keywords in self.intent_routing.items():
            if any(keyword in message_lower for keyword in keywords):
                matched_agents.append(agent)

        return matched_agents or ["zeus"]  # Default to Zeus if no match

    async def shutdown(self):
        """Close all agent connections."""
        logger.info("Shutting down Zeus Agent connections...")
        for name, client in self.clients.items():
            try:
                await client.close()
                logger.info(f"Closed connection to {name}")
            except Exception as e:
                logger.error(f"Error closing connection to {name}: {e}")
            except BaseException as e:
                logger.error(
                    f"Critical error closing connection to {name}: {e}")
        self.clients.clear()

    async def get_client(self, agent_name: str) -> AgentClient:
        """Get or create a client connection to an agent."""
        if agent_name not in self.clients:
            if agent_name not in AGENT_REGISTRY:
                raise ValueError(f"Unknown agent: {agent_name}")

            path = get_agent_path(agent_name)
            client = AgentClient(agent_name, path)
            await client.connect()
            self.clients[agent_name] = client

        return self.clients[agent_name]

    async def list_available_agents(self) -> List[str]:
        """List all registered agents available for delegation."""
        return list(AGENT_REGISTRY.keys())

    async def delegate_task(self, agent_name: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Delegate a task to another agent via MCP."""
        logger.info(f"Delegating to {agent_name}: {tool_name}")
        try:
            client = await self.get_client(agent_name)
            result = await client.call_tool(tool_name, arguments)
            return result
        except Exception as e:
            logger.error(f"Delegation failed: {e}")
            return {"error": str(e)}

    async def conduct_pentarchy_vote(self, proposal_id: str, cost: float, description: str) -> Dict[str, Any]:
        """Conduct a Pentarchy vote for a proposal."""
        logger.info(
            f"Conducting Pentarchy vote for {proposal_id} (Cost: ${cost})")

        risk_level = get_risk_level(cost)

        # 1. Check Auto-Approval Thresholds
        if cost < AUTO_APPROVE_LIMIT:
            return {
                "proposal_id": proposal_id,
                "outcome": "APPROVED",
                "votes": {"system": "AUTO_APPROVE"},
                "reasoning": [f"Cost below ${AUTO_APPROVE_LIMIT} auto-approval threshold"]
            }

        if cost > HUMAN_REVIEW_LIMIT:
            return {
                "proposal_id": proposal_id,
                "outcome": "HUMAN_REVIEW_REQUIRED",
                "votes": {"system": "ABSTAIN"},
                "reasoning": [f"Cost exceeds ${HUMAN_REVIEW_LIMIT} limit for autonomous approval"]
            }

        # 2. Gather Votes from Pentarchy Members
        # Filter out Zeus if he's not in the list, or handle him separately.
        voters = [agent for agent in PENTARCHY_AGENTS if agent != "zeus"]
        votes = {}
        reasons = []

        # Zeus votes as well (Orchestrator/Executive)
        votes["zeus"] = VoteType.APPROVE.value
        reasons.append("Zeus approved (orchestrator)")

        for voter in voters:
            try:
                # In a real system, we would parse the MCP result object.
                # Here we assume the tool returns a dict-like structure or we'd need to parse the JSON string from the content.
                result = await self.delegate_task(
                    voter,
                    "evaluate_proposal",
                    {"proposal_id": proposal_id, "cost": cost,
                        "description": description}
                )

                # Mock parsing logic for MVP
                # If result is a list (MCP content), we'd extract text.
                # For now, assuming direct return or simple dict for the mock flow.
                if isinstance(result, dict) and "vote" in result:
                    votes[voter] = result["vote"]
                    reasons.append(f"{voter} voted {result['vote']}")
                else:
                    votes[voter] = VoteType.APPROVE.value  # Default for mock
                    reasons.append(f"{voter} approved (mock)")

            except Exception as e:
                logger.error(f"Failed to get vote from {voter}: {e}")
                votes[voter] = "ERROR"

        # 3. Tally Votes
        outcome = calculate_vote_outcome(votes, risk_level)

        return {
            "proposal_id": proposal_id,
            "outcome": outcome,
            "votes": votes,
            "reasoning": reasons
        }

    def _determine_complexity(self, text: str, context_length: int) -> str:
        """Determine if task is complex or simple."""
        text_lower = text.lower()

        # Heuristic: Long context or long input -> Complex
        if len(text) > 1000 or context_length > 3000:
            return "complex"

        # Heuristic: Keywords indicating complexity
        # Prioritize these over simple keywords
        complex_keywords = ["analyze", "plan", "architect",
                            "design", "code", "debug", "orchestrate"]
        if any(keyword in text_lower for keyword in complex_keywords):
            return "complex"

        # Explicit simple keywords
        # Removed "hi" to avoid false positives (e.g. in "architect")
        simple_keywords = ["summarize", "explain",
                           "define", "what is", "hello"]
        if any(keyword in text_lower for keyword in simple_keywords):
            return "simple"

        return "simple"

    async def process_query(self, query: str, conversation_id: str = None) -> Dict[str, Any]:
        """Adapter for API router compatibility."""
        input_data = ZeusInput(
            user_message=query,
            conversation_id=conversation_id or str(uuid.uuid4()),
            user_context=None,
            routing_hints=[]
        )

        result = await self.process_message(input_data)
        return {
            "response": result.response,
            "metadata": result.metadata.dict()
        }

    async def process_message(self, input_data: ZeusInput) -> ZeusOutput:
        """
        Main entry point for processing a user message.
        Uses LLM for intelligent response generation with agent routing.
        """
        start_time = datetime.now()
        conversation_id = input_data.conversation_id
        logger.info(f"Processing message for conversation: {conversation_id}")

        # Get or create conversation history
        if conversation_id not in self.conversation_history:
            self.conversation_history[conversation_id] = []

        history = self.conversation_history[conversation_id]

        # Add user message to history
        history.append(LLMMessage(
            role="user", content=input_data.user_message))

        # Detect intent and route to specialist agents
        detected_agents = self._detect_intent(input_data.user_message)
        if input_data.routing_hints:
            detected_agents = list(
                set(detected_agents + input_data.routing_hints))

        logger.info(f"Detected agents for routing: {detected_agents}")

        # Gather specialist responses if agents detected
        specialist_context = ""
        agents_used = ["zeus"]

        for agent_name in detected_agents:
            if agent_name != "zeus" and agent_name in AGENT_REGISTRY:
                try:
                    logger.info(
                        f"Delegating to {agent_name} for specialist input")
                    result = await self.delegate_task(
                        agent_name,
                        "process_query",
                        {"query": input_data.user_message,
                            "conversation_id": conversation_id}
                    )
                    if result and not isinstance(result, dict) or "error" not in result:
                        specialist_context += f"\n[{agent_name.upper()} input: {result}]"
                        agents_used.append(agent_name)
                except Exception as e:
                    logger.warning(
                        f"Could not get input from {agent_name}: {e}")

        # Prepare context with routing hints
        context = ""
        if specialist_context:
            context += f"\nSpecialist agent inputs:{specialist_context}"
        if input_data.user_context:
            context += f"\n[User: {input_data.user_context.user_id}, Roles: {', '.join(input_data.user_context.roles)}]"

        # Generate response using LLM
        try:
            enhanced_prompt = self.system_prompt + context
            if specialist_context:
                enhanced_prompt += "\n\nIncorporate the specialist agent inputs into your response where relevant."

            # Determine complexity and route to appropriate LLM
            complexity = self._determine_complexity(
                input_data.user_message, len(enhanced_prompt))
            # Force complex if specialist agents were used (orchestration is complex)
            if specialist_context:
                complexity = "complex"

            selected_llm = self.llm if complexity == "complex" else self.simple_llm

            logger.info(
                f"Routing request to {complexity} LLM provider: {selected_llm.config.provider.value}")

            llm_response = await selected_llm.chat(
                messages=history,
                system_prompt=enhanced_prompt,
                temperature=0.7,
                max_tokens=2048,
            )

            response_text = llm_response.content
            token_usage = llm_response.usage

            # Add assistant response to history
            history.append(LLMMessage(role="assistant", content=response_text))

            # Keep history manageable (last 20 messages)
            if len(history) > 20:
                self.conversation_history[conversation_id] = history[-20:]

            processing_time = int(
                (datetime.now() - start_time).total_seconds() * 1000)

            return ZeusOutput(
                response=response_text,
                agents_used=agents_used,
                confidence=0.85 if len(agents_used) > 1 else 0.75,
                follow_up_suggestions=self._extract_suggestions(response_text),
                metadata=ResponseMetadata(
                    processing_time_ms=processing_time,
                    token_usage=TokenUsage(
                        prompt_tokens=token_usage.get("prompt_tokens", 0),
                        completion_tokens=token_usage.get(
                            "completion_tokens", 0),
                        total_tokens=token_usage.get("total_tokens", 0),
                    ),
                    trace_id=str(uuid.uuid4()),
                    conversation_turn=len(history) // 2,
                )
            )

        except Exception as e:
            logger.error(f"LLM error: {e}")
            processing_time = int(
                (datetime.now() - start_time).total_seconds() * 1000)

            # Fallback response
            return ZeusOutput(
                response=f"I apologize, but I encountered an issue processing your request. Error: {str(e)}. Please try again or rephrase your question.",
                agents_used=["zeus"],
                confidence=0.0,
                follow_up_suggestions=[
                    "Try rephrasing your question", "Check if the service is available"],
                metadata=ResponseMetadata(
                    processing_time_ms=processing_time,
                    token_usage=TokenUsage(
                        prompt_tokens=0, completion_tokens=0, total_tokens=0),
                    trace_id=str(uuid.uuid4()),
                    conversation_turn=len(history) // 2,
                )
            )

    def _extract_suggestions(self, response: str) -> List[str]:
        """Extract follow-up suggestions from response."""
        suggestions = []
        # Simple heuristic - could be enhanced with NLP
        if "?" in response:
            suggestions.append("Provide more details")
        if any(word in response.lower() for word in ["schedule", "calendar", "time"]):
            suggestions.append("Set a reminder")
        if any(word in response.lower() for word in ["search", "find", "look"]):
            suggestions.append("Search for more information")
        return suggestions[:3]  # Max 3 suggestions

    def run(self):
        """Start the Zeus MCP server."""
        self.mcp.run()

# --- Entry Point ---


if __name__ == "__main__":
    agent = ZeusAgent()
    agent.run()
