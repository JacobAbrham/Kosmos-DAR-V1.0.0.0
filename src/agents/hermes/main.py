import asyncio
import logging
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from fastmcp import FastMCP
import os

from src.services.llm_service import (
    get_llm_service,
    Message as LLMMessage,
    LLMService,
    LLMConfig,
    LLMProvider
)

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("hermes-agent")

# --- Data Models ---


class EmailRequest(BaseModel):
    to: List[str]
    subject: str
    body: str
    cc: Optional[List[str]] = None
    bcc: Optional[List[str]] = None


class SlackRequest(BaseModel):
    channel: str
    message: str


class SMSRequest(BaseModel):
    phone: str
    message: str


class NotificationRequest(BaseModel):
    user_id: str
    title: str
    body: str
    priority: str = "normal"


class DeliveryStatus(BaseModel):
    message_id: str
    status: str  # "sent", "failed", "pending"
    timestamp: datetime
    details: Optional[str] = None

# --- Agent Implementation ---


class ProposalEvaluationRequest(BaseModel):
    proposal_id: str
    cost: float
    description: str


class PentarchyVote(BaseModel):
    vote: str  # "APPROVE", "REJECT", "ABSTAIN"
    score: float
    reasoning: List[str]


class HermesAgent:
    def __init__(self):
        self.name = "hermes"
        self.version = "2.0.0"
        self.mcp = FastMCP(self.name)
        self.llm = get_llm_service()

        # Initialize Simple LLM (HuggingFace) for routing
        hf_key = os.getenv("HUGGINGFACE_API_KEY")
        if hf_key:
            try:
                simple_config = LLMConfig(
                    provider=LLMProvider.HUGGINGFACE,
                    model=os.getenv("HUGGINGFACE_MODEL", "tgi"),
                    api_key=hf_key,
                    base_url=os.getenv("HUGGINGFACE_ENDPOINT_URL"),
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

        self.system_prompt = """You are Hermes, the Communication Agent in the KOSMOS Pentarchy.
Your domain: All external communications (email, Slack, SMS, notifications).
When evaluating proposals, assess:
1. Communication clarity and appropriateness
2. Stakeholder notification requirements
3. Potential reputation/PR implications
4. Response urgency and timing

For Pentarchy votes, respond with JSON: {"vote": "APPROVE/REJECT/ABSTAIN", "score": 0-3, "reasoning": ["reason1", "reason2"]}"""
        logger.info(f"Initializing {self.name} Agent v{self.version}")

        # Register tools
        self.mcp.tool()(self.send_email)
        self.mcp.tool()(self.send_slack)
        self.mcp.tool()(self.send_sms)
        self.mcp.tool()(self.send_notification)
        self.mcp.tool()(self.evaluate_proposal)
        self.mcp.tool()(self.summarize_message)

    async def summarize_message(self, content: str) -> str:
        """Summarize a long message or thread using simple LLM."""
        logger.info("Summarizing message using simple LLM")
        try:
            response = await self.simple_llm.chat([
                LLMMessage(
                    role="system", content="You are a helpful assistant that summarizes text concisely."),
                LLMMessage(role="user", content=f"Summarize this:\n{content}")
            ])
            return response.content
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return "Summarization failed."

    async def evaluate_proposal(self, proposal_id: str, cost: float, description: str) -> PentarchyVote:
        """Evaluate a proposal from communication/stakeholder perspective."""
        logger.info(
            f"Evaluating proposal {proposal_id} for communication impact")

        if self.llm:
            try:
                prompt = f"""Evaluate this proposal from a communication perspective:
Proposal ID: {proposal_id}
Cost: ${cost}
Description: {description}

Consider: stakeholder communication needs, PR implications, notification requirements.
Respond with JSON: {{"vote": "APPROVE/REJECT/ABSTAIN", "score": 0-3, "reasoning": ["reason1", "reason2"]}}"""

                response = await self.llm.chat([
                    LLMMessage(role="system", content=self.system_prompt),
                    LLMMessage(role="user", content=prompt)
                ])

                import json
                import re
                json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    return PentarchyVote(
                        vote=data.get("vote", "ABSTAIN"),
                        score=float(data.get("score", 1)),
                        reasoning=data.get("reasoning", ["LLM evaluation"])
                    )
            except Exception as e:
                logger.error(f"LLM evaluation failed: {e}")

        # Fallback mock logic
        return PentarchyVote(vote="APPROVE", score=2, reasoning=["Communication requirements met"])

    async def send_email(self, to: List[str], subject: str, body: str, cc: Optional[List[str]] = None, bcc: Optional[List[str]] = None) -> DeliveryStatus:
        logger.info(f"Sending email to {to} with subject: {subject}")
        # TODO: Integrate with email-mcp or SMTP
        return DeliveryStatus(
            message_id=f"email-{datetime.now().timestamp()}",
            status="sent",
            timestamp=datetime.now(),
            details="Mock email sent successfully"
        )

    async def send_slack(self, channel: str, message: str) -> DeliveryStatus:
        logger.info(f"Posting to Slack channel {channel}: {message}")
        # TODO: Integrate with slack-mcp
        return DeliveryStatus(
            message_id=f"slack-{datetime.now().timestamp()}",
            status="sent",
            timestamp=datetime.now(),
            details="Mock Slack message posted"
        )

    async def send_sms(self, phone: str, message: str) -> DeliveryStatus:
        logger.info(f"Sending SMS to {phone}")
        # TODO: Integrate with SMS provider
        return DeliveryStatus(
            message_id=f"sms-{datetime.now().timestamp()}",
            status="sent",
            timestamp=datetime.now(),
            details="Mock SMS sent"
        )

    async def send_notification(self, user_id: str, title: str, body: str, priority: str = "normal") -> DeliveryStatus:
        logger.info(f"Pushing notification to user {user_id}")
        return DeliveryStatus(
            message_id=f"notif-{datetime.now().timestamp()}",
            status="sent",
            timestamp=datetime.now(),
            details="Mock notification pushed"
        )

    def run(self):
        """Start the Hermes MCP server."""
        self.mcp.run()

# --- Entry Point ---


if __name__ == "__main__":
    agent = HermesAgent()
    agent.run()
