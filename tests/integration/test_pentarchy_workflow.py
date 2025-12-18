"""
Integration tests for Pentarchy voting workflow.

Tests the complete end-to-end Pentarchy governance system including
auto-approval, full voting, and outcome determination.
"""

import pytest
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from src.agents.zeus.main import ZeusAgent


@pytest.mark.asyncio
async def test_auto_approve_low_cost():
    """Test proposals under $50 are auto-approved."""
    zeus = ZeusAgent()
    
    try:
        result = await zeus.conduct_pentarchy_vote(
            proposal_id="auto-001",
            cost=25.00,
            description="Low cost infrastructure upgrade"
        )
        
        assert result["outcome"] == "approved"
        assert result["proposal_id"] == "auto-001"
        assert "auto_approved" in result.get("rationale", "").lower()
        
    finally:
        await zeus.shutdown()


@pytest.mark.asyncio
async def test_full_vote_medium_cost():
    """Test proposals $50-$100 trigger full Pentarchy vote."""
    zeus = ZeusAgent()
    
    try:
        result = await zeus.conduct_pentarchy_vote(
            proposal_id="medium-001",
            cost=75.00,
            description="Medium cost software license"
        )
        
        # Verify vote occurred
        assert "votes" in result
        assert len(result["votes"]) == 5  # Zeus, Nur, Hephaestus, Athena, Hermes
        
        # Verify all pentarchy members voted
        expected_voters = {"zeus", "nur_prometheus", "hephaestus", "athena", "hermes"}
        actual_voters = set(result["votes"].keys())
        assert expected_voters == actual_voters
        
        # Verify outcome is determined
        assert result["outcome"] in ["approved", "rejected"]
        
        # Verify reasoning provided
        assert "reasoning" in result
        assert len(result["reasoning"]) == 5
        
    finally:
        await zeus.shutdown()


@pytest.mark.asyncio
async def test_auto_reject_high_cost():
    """Test proposals over $100 are auto-rejected."""
    zeus = ZeusAgent()
    
    try:
        result = await zeus.conduct_pentarchy_vote(
            proposal_id="high-001",
            cost=150.00,
            description="High cost enterprise software"
        )
        
        assert result["outcome"] == "rejected"
        assert "exceeds" in result.get("rationale", "").lower()
        
    finally:
        await zeus.shutdown()


@pytest.mark.asyncio
async def test_vote_majority_approval():
    """Test vote with 3+ approvals results in approval."""
    zeus = ZeusAgent()
    
    try:
        result = await zeus.conduct_pentarchy_vote(
            proposal_id="majority-001",
            cost=60.00,
            description="Cloud infrastructure upgrade"
        )
        
        # Count approvals
        approvals = sum(1 for vote in result["votes"].values() if vote == "approve")
        rejections = sum(1 for vote in result["votes"].values() if vote == "reject")
        
        # If majority approved, outcome should be approved
        if approvals >= 3:
            assert result["outcome"] == "approved"
        else:
            assert result["outcome"] == "rejected"
        
        # Total votes should be 5
        assert approvals + rejections == 5
        
    finally:
        await zeus.shutdown()


@pytest.mark.asyncio
async def test_vote_reasoning_quality():
    """Test that all voting agents provide reasoning."""
    zeus = ZeusAgent()
    
    try:
        result = await zeus.conduct_pentarchy_vote(
            proposal_id="reasoning-001",
            cost=80.00,
            description="Security audit service subscription"
        )
        
        # Verify reasoning exists
        assert "reasoning" in result
        reasoning_list = result["reasoning"]
        
        # All 5 agents should provide reasoning
        assert len(reasoning_list) == 5
        
        # Each reasoning should be non-empty string
        for reason in reasoning_list:
            assert isinstance(reason, str)
            assert len(reason) > 10  # Meaningful reasoning
            
    finally:
        await zeus.shutdown()


@pytest.mark.asyncio
async def test_vote_persistence():
    """Test vote results are consistent across calls."""
    zeus = ZeusAgent()
    
    try:
        # First vote
        result1 = await zeus.conduct_pentarchy_vote(
            proposal_id="persist-001",
            cost=55.00,
            description="Documentation tool subscription"
        )
        
        # Second vote with same proposal ID should have same outcome
        result2 = await zeus.conduct_pentarchy_vote(
            proposal_id="persist-001",
            cost=55.00,
            description="Documentation tool subscription"
        )
        
        # Outcomes should match (deterministic for same input)
        assert result1["outcome"] == result2["outcome"]
        
    finally:
        await zeus.shutdown()


@pytest.mark.asyncio
async def test_vote_boundary_conditions():
    """Test voting at exact boundary values ($50 and $100)."""
    zeus = ZeusAgent()
    
    try:
        # Exactly $50 - should trigger vote
        result_50 = await zeus.conduct_pentarchy_vote(
            proposal_id="boundary-50",
            cost=50.00,
            description="Exactly $50 proposal"
        )
        assert "votes" in result_50
        
        # Exactly $100 - should trigger vote
        result_100 = await zeus.conduct_pentarchy_vote(
            proposal_id="boundary-100",
            cost=100.00,
            description="Exactly $100 proposal"
        )
        assert "votes" in result_100
        
        # Just under $50 - auto-approve
        result_49 = await zeus.conduct_pentarchy_vote(
            proposal_id="boundary-49",
            cost=49.99,
            description="Just under $50 proposal"
        )
        assert result_49["outcome"] == "approved"
        
        # Just over $100 - auto-reject
        result_101 = await zeus.conduct_pentarchy_vote(
            proposal_id="boundary-101",
            cost=100.01,
            description="Just over $100 proposal"
        )
        assert result_101["outcome"] == "rejected"
        
    finally:
        await zeus.shutdown()


@pytest.mark.asyncio
async def test_concurrent_votes():
    """Test system handles concurrent voting requests."""
    import asyncio
    
    zeus = ZeusAgent()
    
    try:
        async def vote(prop_id: str, cost: float):
            return await zeus.conduct_pentarchy_vote(
                proposal_id=prop_id,
                cost=cost,
                description=f"Concurrent test proposal {prop_id}"
            )
        
        # Submit 3 concurrent votes
        tasks = [
            vote("concurrent-1", 60.00),
            vote("concurrent-2", 70.00),
            vote("concurrent-3", 80.00)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # All should complete successfully
        assert len(results) == 3
        for result in results:
            assert "outcome" in result
            assert "votes" in result
            
    finally:
        await zeus.shutdown()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
