import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.agents.zeus.main import ZeusAgent

@pytest.mark.asyncio
async def test_pentarchy_split_vote():
    """Test scenario where Pentarchy vote is split (3 Approve, 2 Reject)."""
    zeus = ZeusAgent()
    
    # Mock the delegate_task method to simulate split votes
    async def mock_delegate(agent_name, tool_name, arguments):
        if agent_name in ["nur_prometheus", "hephaestus"]:
            return {"vote": "APPROVE", "score": 2.0, "reasoning": ["Good"]}
        elif agent_name in ["athena", "hermes"]:
            return {"vote": "REJECT", "score": 0.0, "reasoning": ["Bad"]}
        return None

    with patch.object(zeus, 'delegate_task', side_effect=mock_delegate):
        # Zeus itself votes APPROVE in the code logic
        # So: Zeus(Approve) + Nur(Approve) + Heph(Approve) = 3 Approves
        # Athena(Reject) + Hermes(Reject) = 2 Rejects
        # Total: 3/5 Approves -> Should be APPROVED_WITH_REVIEW
        
        result = await zeus.conduct_pentarchy_vote(
            proposal_id="split-vote-001",
            cost=75.0,
            description="Controversial proposal"
        )
        
        assert result["outcome"] == "APPROVED_WITH_REVIEW"
        assert result["votes"]["zeus"] == "APPROVE"
        assert result["votes"]["nur_prometheus"] == "APPROVE"
        assert result["votes"]["athena"] == "REJECT"

@pytest.mark.asyncio
async def test_pentarchy_partial_failure():
    """Test scenario where one agent fails to vote."""
    zeus = ZeusAgent()
    
    async def mock_delegate(agent_name, tool_name, arguments):
        if agent_name == "nur_prometheus":
            raise Exception("Connection timeout")
        return {"vote": "APPROVE", "score": 2.0, "reasoning": ["Good"]}

    with patch.object(zeus, 'delegate_task', side_effect=mock_delegate):
        # Zeus(Approve) + Heph(Approve) + Athena(Approve) + Hermes(Approve) = 4 Approves
        # Nur(Error)
        # Total: 4/5 Approves -> APPROVED
        
        result = await zeus.conduct_pentarchy_vote(
            proposal_id="partial-fail-001",
            cost=75.0,
            description="Resilient proposal"
        )
        
        assert result["outcome"] == "APPROVED"
        assert result["votes"]["nur_prometheus"] == "ERROR"
        assert result["votes"]["hephaestus"] == "APPROVE"
