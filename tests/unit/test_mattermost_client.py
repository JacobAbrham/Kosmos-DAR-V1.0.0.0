"""
Unit tests for Mattermost client.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
import httpx

from src.integrations.notifications.mattermost_client import (
    MattermostClient,
    MattermostMessage,
    MattermostAttachment
)


@pytest.fixture
def mattermost_client():
    """Create Mattermost client for testing."""
    return MattermostClient(webhook_url="http://test.mattermost.local/hooks/test123")


@pytest.mark.asyncio
async def test_send_simple_message(mattermost_client):
    """Test sending a simple message."""
    message = MattermostMessage(text="Test message")
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
        
        result = await mattermost_client.send_message(message)
        
        assert result is True


@pytest.mark.asyncio
async def test_send_message_with_attachment(mattermost_client):
    """Test sending message with attachment."""
    attachment = MattermostAttachment(
        color="#36a64f",
        text="Test attachment",
        fields=[{"title": "Field1", "value": "Value1", "short": True}]
    )
    
    message = MattermostMessage(
        text="Test with attachment",
        attachments=[attachment]
    )
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
        
        result = await mattermost_client.send_message(message)
        
        assert result is True


@pytest.mark.asyncio
async def test_send_deployment_notification_success(mattermost_client):
    """Test deployment notification for success."""
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
        
        result = await mattermost_client.send_deployment_notification(
            environment="staging",
            status="success",
            repository="kosmos/test",
            branch="master",
            commit="abc123def456",
            author="test-user"
        )
        
        assert result is True


@pytest.mark.asyncio
async def test_send_deployment_notification_failure(mattermost_client):
    """Test deployment notification for failure."""
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
        
        result = await mattermost_client.send_deployment_notification(
            environment="production",
            status="failure",
            repository="kosmos/test",
            branch="master",
            commit="abc123def456",
            author="test-user",
            logs_url="https://github.com/test/actions/runs/123"
        )
        
        assert result is True


@pytest.mark.asyncio
async def test_send_agent_notification(mattermost_client):
    """Test agent activity notification."""
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
        
        result = await mattermost_client.send_agent_notification(
            agent_name="Zeus",
            event_type="task_completed",
            message_text="Successfully completed orchestration task",
            metadata={"duration": "5.2s", "success_rate": "100%"}
        )
        
        assert result is True


@pytest.mark.asyncio
async def test_send_message_http_error(mattermost_client):
    """Test handling HTTP errors."""
    message = MattermostMessage(text="Test message")
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            side_effect=httpx.HTTPStatusError("Error", request=Mock(), response=Mock(status_code=500))
        )
        
        result = await mattermost_client.send_message(message)
        
        assert result is False


@pytest.mark.asyncio
async def test_send_message_no_webhook_url():
    """Test sending message without webhook URL."""
    client = MattermostClient(webhook_url=None)
    message = MattermostMessage(text="Test message")
    
    result = await client.send_message(message)
    
    assert result is False
