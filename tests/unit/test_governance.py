"""
Unit tests for the governance module.
Tests voting thresholds, outcomes, and risk level calculations.
"""
import pytest
from src.core.governance import (
    RiskLevel,
    VoteType,
    THRESHOLDS,
    AUTO_APPROVE_LIMIT,
    HUMAN_REVIEW_LIMIT,
    PENTARCHY_AGENTS,
    get_risk_level,
    calculate_vote_outcome,
)


class TestRiskLevelCalculation:
    """Tests for get_risk_level function."""

    def test_low_risk_below_auto_approve(self):
        """Costs below $50 should be LOW risk."""
        assert get_risk_level(0) == RiskLevel.LOW
        assert get_risk_level(25) == RiskLevel.LOW
        assert get_risk_level(49.99) == RiskLevel.LOW

    def test_medium_risk_pentarchy_range(self):
        """Costs $50-$100 should be MEDIUM risk (Pentarchy voting)."""
        assert get_risk_level(50) == RiskLevel.MEDIUM
        assert get_risk_level(75) == RiskLevel.MEDIUM
        assert get_risk_level(99.99) == RiskLevel.MEDIUM

    def test_high_risk_human_review(self):
        """Costs $100-$1000 should be HIGH risk (human review)."""
        assert get_risk_level(100) == RiskLevel.HIGH
        assert get_risk_level(500) == RiskLevel.HIGH
        assert get_risk_level(999.99) == RiskLevel.HIGH

    def test_critical_risk_large_amounts(self):
        """Costs over $1000 should be CRITICAL."""
        assert get_risk_level(1000) == RiskLevel.CRITICAL
        assert get_risk_level(10000) == RiskLevel.CRITICAL
        assert get_risk_level(1000000) == RiskLevel.CRITICAL


class TestVoteOutcomeCalculation:
    """Tests for calculate_vote_outcome function."""

    def test_unanimous_approve_low_risk(self):
        """5 approve votes should APPROVE for low risk."""
        votes = {
            "athena": "APPROVE",
            "hephaestus": "APPROVE",
            "hermes": "APPROVE",
            "nur_prometheus": "APPROVE",
            "aegis": "APPROVE",
        }
        assert calculate_vote_outcome(votes, RiskLevel.LOW) == "APPROVED"

    def test_unanimous_approve_medium_risk(self):
        """5 approve votes should APPROVE for medium risk."""
        votes = {
            "athena": "APPROVE",
            "hephaestus": "APPROVE",
            "hermes": "APPROVE",
            "nur_prometheus": "APPROVE",
            "aegis": "APPROVE",
        }
        assert calculate_vote_outcome(votes, RiskLevel.MEDIUM) == "APPROVED"

    def test_unanimous_reject(self):
        """5 reject votes should REJECT."""
        votes = {
            "athena": "REJECT",
            "hephaestus": "REJECT",
            "hermes": "REJECT",
            "nur_prometheus": "REJECT",
            "aegis": "REJECT",
        }
        assert calculate_vote_outcome(votes, RiskLevel.MEDIUM) == "REJECTED"

    def test_mixed_votes_majority_approve(self):
        """Majority approve should pass for low risk."""
        votes = {
            "athena": "APPROVE",
            "hephaestus": "APPROVE",
            "hermes": "APPROVE",
            "nur_prometheus": "REJECT",
            "aegis": "ABSTAIN",
        }
        assert calculate_vote_outcome(votes, RiskLevel.LOW) == "APPROVED"

    def test_mixed_votes_with_abstain(self):
        """Votes with abstentions should handle correctly."""
        votes = {
            "athena": "APPROVE",
            "hephaestus": "APPROVE",
            "hermes": "ABSTAIN",
            "nur_prometheus": "ABSTAIN",
            "aegis": "ABSTAIN",
        }
        result = calculate_vote_outcome(votes, RiskLevel.MEDIUM)
        # 2 approves = score 2, threshold for medium is 2.0
        assert result == "APPROVED"

    def test_high_risk_requires_near_consensus(self):
        """High risk requires near consensus (threshold 2.5)."""
        votes = {
            "athena": "APPROVE",
            "hephaestus": "APPROVE",
            "hermes": "APPROVE",
            "nur_prometheus": "ABSTAIN",
            "aegis": "ABSTAIN",
        }
        result = calculate_vote_outcome(votes, RiskLevel.HIGH)
        # 3 approves = score 3, threshold is 2.5 -> APPROVED
        assert result == "APPROVED"

    def test_critical_risk_needs_unanimous(self):
        """Critical risk requires near unanimous (threshold 2.8)."""
        votes = {
            "athena": "APPROVE",
            "hephaestus": "APPROVE",
            "hermes": "APPROVE",
            "nur_prometheus": "APPROVE",
            "aegis": "REJECT",
        }
        result = calculate_vote_outcome(votes, RiskLevel.CRITICAL)
        # 4 approve, 1 reject = score 3, threshold 2.8 -> APPROVED
        assert result == "APPROVED"

    def test_empty_votes(self):
        """Empty votes should REJECT."""
        votes = {}
        result = calculate_vote_outcome(votes, RiskLevel.MEDIUM)
        assert result == "REJECTED"

    def test_approved_with_review_marginal_case(self):
        """Marginal cases should return APPROVED_WITH_REVIEW."""
        votes = {
            "athena": "APPROVE",
            "hephaestus": "APPROVE",
            "hermes": "APPROVE",
            "nur_prometheus": "ABSTAIN",
            "aegis": "REJECT",
        }
        result = calculate_vote_outcome(votes, RiskLevel.MEDIUM)
        # 3 approve, 1 reject = score 2, threshold 2.0
        # score >= threshold (2 >= 2.0) -> APPROVED
        # But let's test a closer marginal case for LOW risk
        votes_marginal = {
            "athena": "APPROVE",
            "hephaestus": "ABSTAIN",
            "hermes": "ABSTAIN",
            "nur_prometheus": "ABSTAIN",
            "aegis": "ABSTAIN",
        }
        result_marginal = calculate_vote_outcome(votes_marginal, RiskLevel.LOW)
        # 1 approve = score 1, LOW threshold is 1.5
        # score >= (1.5 - 0.5) and score > 0 -> 1 >= 1.0 and 1 > 0 -> APPROVED_WITH_REVIEW
        assert result_marginal == "APPROVED_WITH_REVIEW"


class TestThresholdConfiguration:
    """Tests for threshold configuration."""

    def test_thresholds_exist_for_all_risk_levels(self):
        """All risk levels should have defined thresholds."""
        for risk in RiskLevel:
            assert risk in THRESHOLDS
            assert THRESHOLDS[risk] > 0

    def test_thresholds_increase_with_risk(self):
        """Higher risk levels should have higher thresholds."""
        assert THRESHOLDS[RiskLevel.LOW] < THRESHOLDS[RiskLevel.MEDIUM]
        assert THRESHOLDS[RiskLevel.MEDIUM] < THRESHOLDS[RiskLevel.HIGH]
        assert THRESHOLDS[RiskLevel.HIGH] < THRESHOLDS[RiskLevel.CRITICAL]

    def test_pentarchy_agents_defined(self):
        """All 5 Pentarchy agents should be defined."""
        assert len(PENTARCHY_AGENTS) == 5
        assert "athena" in PENTARCHY_AGENTS
        assert "aegis" in PENTARCHY_AGENTS
        assert "hermes" in PENTARCHY_AGENTS
        assert "hephaestus" in PENTARCHY_AGENTS
        assert "nur_prometheus" in PENTARCHY_AGENTS

    def test_cost_limits(self):
        """Cost limits should be properly defined."""
        assert AUTO_APPROVE_LIMIT == 50.0
        assert HUMAN_REVIEW_LIMIT == 100.0
        assert AUTO_APPROVE_LIMIT < HUMAN_REVIEW_LIMIT


class TestVoteTypeEnum:
    """Tests for VoteType enum."""

    def test_vote_type_values(self):
        """VoteType should have correct values."""
        assert VoteType.APPROVE.value == "APPROVE"
        assert VoteType.REJECT.value == "REJECT"
        assert VoteType.ABSTAIN.value == "ABSTAIN"

    def test_vote_type_comparison(self):
        """VoteType should compare correctly with strings."""
        assert VoteType.APPROVE.value == "APPROVE"
        assert VoteType.REJECT.value == "REJECT"
