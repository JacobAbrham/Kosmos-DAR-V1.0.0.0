"""
Mattermost notification client for KOSMOS.
Provides notification capabilities with tracing and error handling.
"""
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import httpx
from pydantic import BaseModel, Field, HttpUrl

logger = logging.getLogger(__name__)


class MattermostAttachment(BaseModel):
    """Mattermost message attachment."""
    
    color: str = Field(default="#36a64f", description="Attachment color")
    pretext: Optional[str] = Field(default=None, description="Text before attachment")
    text: Optional[str] = Field(default=None, description="Main text")
    title: Optional[str] = Field(default=None, description="Attachment title")
    title_link: Optional[str] = Field(default=None, description="Title link URL")
    fields: List[Dict[str, Any]] = Field(default_factory=list, description="Attachment fields")
    footer: Optional[str] = Field(default=None, description="Footer text")
    footer_icon: Optional[str] = Field(default=None, description="Footer icon URL")


class MattermostMessage(BaseModel):
    """Mattermost message model."""
    
    text: str = Field(..., description="Message text")
    channel: Optional[str] = Field(default=None, description="Channel to post to")
    username: Optional[str] = Field(default="KOSMOS Bot", description="Bot username")
    icon_url: Optional[str] = Field(default=None, description="Bot icon URL")
    icon_emoji: Optional[str] = Field(default=":robot:", description="Bot emoji icon")
    attachments: List[MattermostAttachment] = Field(default_factory=list, description="Message attachments")


class MattermostClient:
    """
    Mattermost client for sending notifications.
    
    Features:
    - Webhook-based notifications
    - Rich message formatting
    - Attachment support
    - Error handling and retries
    - OpenTelemetry tracing
    """
    
    def __init__(
        self,
        webhook_url: Optional[str] = None,
        timeout: int = 10,
        max_retries: int = 3
    ):
        """
        Initialize Mattermost client.
        
        Args:
            webhook_url: Mattermost incoming webhook URL
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.webhook_url = webhook_url
        self.timeout = timeout
        self.max_retries = max_retries
        
        if not self.webhook_url:
            logger.warning("Mattermost webhook URL not configured")
    
    async def send_message(
        self,
        message: MattermostMessage,
        **trace_attributes
    ) -> bool:
        """
        Send message to Mattermost.
        
        Args:
            message: Message to send
            trace_attributes: Additional tracing attributes
            
        Returns:
            True if successful, False otherwise
        """
        if not self.webhook_url:
            logger.error("Cannot send message: webhook URL not configured")
            return False
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = message.model_dump(exclude_none=True)
                
                logger.debug(f"Sending Mattermost message: {payload}")
                
                response = await client.post(
                    self.webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                response.raise_for_status()
                
                logger.info(f"Mattermost message sent successfully to {message.channel or 'default channel'}")
                return True
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error sending Mattermost message: {e.response.status_code} - {e.response.text}")
            return False
        except httpx.RequestError as e:
            logger.error(f"Request error sending Mattermost message: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending Mattermost message: {str(e)}", exc_info=True)
            return False
    
    async def send_deployment_notification(
        self,
        environment: str,
        status: str,
        repository: str,
        branch: str,
        commit: str,
        author: str,
        logs_url: Optional[str] = None,
        **trace_attributes
    ) -> bool:
        """
        Send deployment notification.
        
        Args:
            environment: Deployment environment (dev/staging/production)
            status: Deployment status (success/failure/rollback)
            repository: Repository name
            branch: Git branch
            commit: Git commit SHA
            author: Deployment author
            logs_url: URL to deployment logs
            trace_attributes: Additional tracing attributes
            
        Returns:
            True if successful, False otherwise
        """
        # Determine color and emoji based on status
        color_map = {
            "success": "#36a64f",  # Green
            "failure": "#ff0000",  # Red
            "rollback": "#ffa500",  # Orange
            "pending": "#ffff00"   # Yellow
        }
        
        emoji_map = {
            "success": "✅",
            "failure": "❌",
            "rollback": "⚠️",
            "pending": "⏳"
        }
        
        color = color_map.get(status.lower(), "#808080")
        emoji = emoji_map.get(status.lower(), "ℹ️")
        
        # Build message
        title = f"{emoji} **{environment.upper()} Deployment {status.title()}**"
        
        fields = [
            {"title": "Repository", "value": repository, "short": True},
            {"title": "Branch", "value": branch, "short": True},
            {"title": "Commit", "value": commit[:8], "short": True},
            {"title": "Author", "value": author, "short": True},
        ]
        
        if logs_url:
            fields.append({
                "title": "Logs",
                "value": f"[View Deployment Logs]({logs_url})",
                "short": False
            })
        
        attachment = MattermostAttachment(
            color=color,
            fields=fields,
            footer="KOSMOS Deployment System",
            footer_icon="https://github.com/identicons/kosmos.png"
        )
        
        message = MattermostMessage(
            text=title,
            channel="deployments",
            attachments=[attachment]
        )
        
        return await self.send_message(message, **trace_attributes)
    
    async def send_agent_notification(
        self,
        agent_name: str,
        event_type: str,
        message_text: str,
        metadata: Optional[Dict[str, Any]] = None,
        **trace_attributes
    ) -> bool:
        """
        Send agent activity notification.
        
        Args:
            agent_name: Name of the agent
            event_type: Type of event (task_started, task_completed, error, etc.)
            message_text: Main message text
            metadata: Additional metadata
            trace_attributes: Additional tracing attributes
            
        Returns:
            True if successful, False otherwise
        """
        emoji_map = {
            "task_started": "🚀",
            "task_completed": "✅",
            "task_failed": "❌",
            "warning": "⚠️",
            "info": "ℹ️"
        }
        
        emoji = emoji_map.get(event_type, "📢")
        title = f"{emoji} **Agent: {agent_name}** - {event_type.replace('_', ' ').title()}"
        
        fields = []
        if metadata:
            for key, value in metadata.items():
                fields.append({
                    "title": key.replace('_', ' ').title(),
                    "value": str(value),
                    "short": True
                })
        
        attachment = MattermostAttachment(
            color="#4A90E2",
            text=message_text,
            fields=fields,
            footer=f"KOSMOS Agent System • {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
        )
        
        message = MattermostMessage(
            text=title,
            channel="agent-activity",
            attachments=[attachment]
        )
        
        return await self.send_message(message, **trace_attributes)


# Singleton instance
_mattermost_client: Optional[MattermostClient] = None


def get_mattermost_client(webhook_url: Optional[str] = None) -> MattermostClient:
    """Get or create Mattermost client singleton."""
    global _mattermost_client
    if _mattermost_client is None:
        _mattermost_client = MattermostClient(webhook_url=webhook_url)
    return _mattermost_client
