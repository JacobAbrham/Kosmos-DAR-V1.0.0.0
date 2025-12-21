from typing import List, Dict, Any, Optional
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class VoteType(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    ABSTAIN = "ABSTAIN"

# Voting thresholds (Score required to pass)
# Assuming 5 agents, max score is 5.0 (if each vote is 1.0)
THRESHOLDS = {
    RiskLevel.LOW: 1.5,      # Simple majority (e.g. 2/5 if others abstain, or 3/5)
    RiskLevel.MEDIUM: 2.0,   # 2/3 majority
    RiskLevel.HIGH: 2.5,     # Near consensus
    RiskLevel.CRITICAL: 2.8,  # Almost unanimous
}

# Cost limits for auto-approval/escalation
AUTO_APPROVE_LIMIT = 50.0
HUMAN_REVIEW_LIMIT = 100.0

# The core Pentarchy members
PENTARCHY_AGENTS = ["athena", "hephaestus", "hermes", "nur_prometheus", "aegis"]

def get_risk_level(cost: float) -> RiskLevel:
    """Determine risk level based on cost."""
    if cost < AUTO_APPROVE_LIMIT:
        return RiskLevel.LOW
    elif cost < HUMAN_REVIEW_LIMIT:
        return RiskLevel.MEDIUM
    elif cost < 1000.0:
        return RiskLevel.HIGH
    else:
        return RiskLevel.CRITICAL

def calculate_vote_outcome(votes: Dict[str, str], risk_level: RiskLevel = RiskLevel.MEDIUM) -> str:
    """
    Calculate the outcome of a vote based on the risk level and thresholds.
    
    Args:
        votes: Dictionary mapping agent name to vote string (APPROVE, REJECT, ABSTAIN)
        risk_level: The risk level of the proposal
        
    Returns:
        "APPROVED", "REJECTED", or "APPROVED_WITH_REVIEW"
    """
    score = 0.0
    total_votes = 0
    
    for vote in votes.values():
        if vote == VoteType.APPROVE.value:
            score += 1.0
            total_votes += 1
        elif vote == VoteType.REJECT.value:
            score -= 1.0 # Rejections penalize the score
            total_votes += 1
        # Abstains do not contribute to score
            
    threshold = THRESHOLDS.get(risk_level, THRESHOLDS[RiskLevel.MEDIUM])
    
    if score >= threshold:
        return "APPROVED"
    elif score >= (threshold - 0.5) and score > 0:
        return "APPROVED_WITH_REVIEW"
    else:
        return "REJECTED"
