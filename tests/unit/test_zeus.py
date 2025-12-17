import pytest
from src.agents.zeus.main import ZeusAgent, ZeusInput

@pytest.mark.asyncio
async def test_zeus_initialization():
    agent = ZeusAgent()
    assert agent.name == "zeus"
    assert agent.version == "2.0.0"

@pytest.mark.asyncio
async def test_zeus_pentarchy_logic_auto_approve():
    agent = ZeusAgent()
    result = await agent.conduct_pentarchy_vote("test-prop", 10.0, "Cheap item")
    assert result["outcome"] == "APPROVED"
    assert result["votes"]["system"] == "AUTO_APPROVE"

@pytest.mark.asyncio
async def test_zeus_pentarchy_logic_human_review():
    agent = ZeusAgent()
    result = await agent.conduct_pentarchy_vote("test-prop", 200.0, "Expensive item")
    assert result["outcome"] == "HUMAN_REVIEW_REQUIRED"
