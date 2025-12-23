# Pentarchy Governance Model

:::info Multi-Agent Decision Framework
    The Pentarchy is KOSMOS's multi-agent decision-making system for actions that exceed auto-approval thresholds, ensuring both AI intelligence and human oversight in critical decisions.

## Overview

The Pentarchy Governance Model provides a structured approach to autonomous decision-making that balances efficiency with accountability.

```
                    ┌─────────────────────────┐
                    │      PROPOSAL           │
                    │   (Cost > $50)          │
                    └───────────┬─────────────┘
                                │
                                ▼
              ┌─────────────────────────────────────┐
              │         PENTARCHY VOTE              │
              │                                     │
              │  ┌─────────┐ ┌─────────┐ ┌─────────┐│
              │  │   Nur   │ │Hephaest-│ │ Athena  ││
              │  │PROMETHEUS│ │  us     │ │         ││
              │  │Financial│ │Technical│ │Compliance││
              │  └────┬────┘ └────┬────┘ └────┬────┘│
              │       │          │           │      │
              │       └──────────┼───────────┘      │
              │                  │                  │
              └──────────────────┼──────────────────┘
                                 │
                    ┌────────────┼────────────┐
                    │            │            │
                    ▼            ▼            ▼
              ┌─────────┐  ┌─────────┐  ┌─────────┐
              │3/3 VOTES│  │2/3 VOTES│  │&lt;2 VOTES │
              │Cost<$100│  │Cost<$100│  │OR >$100 │
              └────┬────┘  └────┬────┘  └────┬────┘
                   │            │            │
                   ▼            ▼            ▼
              AUTO_APPROVE  HUMAN_REVIEW  HUMAN_REQUIRED
```

## Decision Thresholds

| Cost Range | AI Votes Required | Human Approval |
|------------|-------------------|----------------|
| < $50 | None (auto-approve) | Not required |
| $50 - $100 | 3/3 unanimous | Not required |
| $50 - $100 | 2/3 majority | Review recommended |
| > $100 | Any | Always required |
| Security/Legal | Any | Always required |

## Pentarchy Voters

### 1. Nur PROMETHEUS (Financial Viability)

**Evaluation Criteria:**
- Budget impact assessment
- Cost-benefit ratio analysis
- Resource allocation efficiency
- Long-term financial implications

**Vote Logic:**
```python
def evaluate_financial_viability(proposal):
    score = 0
    
    # Budget check
    if proposal.cost < budget_remaining * 0.1:
        score += 1
    
    # ROI analysis
    if proposal.expected_roi > 1.5:
        score += 1
    
    # Historical pattern
    if similar_proposals_succeeded_rate > 0.8:
        score += 1
    
    return score >= 2  # Approve if 2+ criteria met
```

### 2. Hephaestus (Technical Feasibility)

**Evaluation Criteria:**
- Infrastructure readiness
- Resource availability
- Technical dependencies
- Implementation risk

**Vote Logic:**
```python
def evaluate_technical_feasibility(proposal):
    checks = [
        check_resource_availability(proposal),
        check_dependency_status(proposal),
        check_infrastructure_capacity(proposal),
        assess_implementation_risk(proposal)
    ]
    
    return sum(checks) >= 3  # Approve if 3+ checks pass
```

### 3. Athena (Compliance Verification)

**Evaluation Criteria:**
- Regulatory compliance
- Policy adherence
- Ethical considerations
- Audit requirements

**Vote Logic:**
```python
def evaluate_compliance(proposal):
    violations = []
    
    # Check against all active policies
    for policy in active_policies:
        if policy.check(proposal) == VIOLATION:
            violations.append(policy)
    
    # Check against ethical guidelines
    ethical_score = ethics_model.evaluate(proposal)
    
    return len(violations) == 0 and ethical_score > 0.8
```

## Implementation

### Zeus Integration

The Pentarchy logic is hard-coded into Zeus as a LangGraph decorator:

```typescript
// Pentarchy Governance Logic (Hard-coded into Zeus)
async function pentarchyVote(proposal: Proposal): Promise<Decision> {
  // 1. Gather AI Votes (parallel execution)
  const votes = await Promise.all([
    NurPROMETHEUS.evaluate(proposal, "financial_viability"),
    Hephaestus.evaluate(proposal, "technical_feasibility"),
    Athena.evaluate(proposal, "compliance_check")
  ]);

  // 2. Calculate AI Consensus
  const aiScore = votes.filter(v => v.approved).length;

  // 3. Determine Outcome
  if (proposal.cost < 100 && aiScore === 3) {
    // Fully autonomous if cost is low and all 3 AI agents approve
    return "AUTO_APPROVE";
  } else if (proposal.cost < 100 && aiScore >= 2) {
    // Recommend human review for split votes
    return "HUMAN_REVIEW";
  } else {
    // Escalate to Human (Operator Alpha/Beta)
    return requestHumanApproval(proposal, votes);
  }
}
```

### Vote Record Schema

```sql
CREATE TABLE pentarchy_votes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    proposal_id UUID NOT NULL REFERENCES proposals(id),
    voter_agent VARCHAR(50) NOT NULL,
    evaluation_type VARCHAR(50) NOT NULL,
    approved BOOLEAN NOT NULL,
    reasoning JSONB NOT NULL,
    confidence DECIMAL(3,2) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT valid_voter CHECK (
        voter_agent IN ('nur_prometheus', 'hephaestus', 'athena')
    )
);

CREATE INDEX idx_pentarchy_proposal ON pentarchy_votes(proposal_id);
CREATE INDEX idx_pentarchy_created ON pentarchy_votes(created_at);
```

## Human Escalation

### Escalation Triggers

| Trigger | Escalation Level |
|---------|------------------|
| Cost > $100 | Operator Alpha |
| Split AI vote (2/3) | Operator Alpha (optional) |
| Security-related | Operator Alpha + AEGIS review |
| Legal implications | Operator Alpha + Legal team |
| Irreversible action | Operator Alpha confirmation |

## Audit Trail

Every Pentarchy decision is logged:

```json
{
  "decision_id": "dec_abc123",
  "proposal_id": "prop_xyz789",
  "timestamp": "2025-01-15T14:32:00Z",
  "votes": [
    {
      "agent": "nur_prometheus",
      "approved": true,
      "reasoning": "Within budget allocation",
      "confidence": 0.87
    },
    {
      "agent": "hephaestus", 
      "approved": true,
      "reasoning": "Infrastructure ready",
      "confidence": 0.92
    },
    {
      "agent": "athena",
      "approved": true,
      "reasoning": "No policy violations",
      "confidence": 0.95
    }
  ],
  "outcome": "AUTO_APPROVE",
  "human_override": null,
  "execution_status": "completed",
  "trace_id": "trace_def456"
}
```

## Configuration

### Threshold Configuration

```yaml
# pentarchy-config.yaml
thresholds:
  auto_approve_max: 50        # USD
  pentarchy_vote_max: 100     # USD
  human_required_above: 100   # USD
  
voting:
  required_voters: 3
  unanimous_for_auto: true
  majority_threshold: 2
  
escalation:
  always_escalate:
    - security_operations
    - legal_actions
    - irreversible_operations
    - pii_data_access
    
timeouts:
  vote_timeout: 30s
  human_response_timeout: 24h
  auto_reject_on_timeout: false
```

## Monitoring

### Key Metrics

| Metric | Alert Threshold |
|--------|-----------------|
| Vote latency | > 5s |
| Human response time | > 4h |
| Auto-approve rate | < 60% or > 95% |
| Rejection rate | > 20% |

---

## See Also

- [Cost Governance](cost-governance) — Pre-flight cost control
- [Kill Switch Protocol](kill-switch-protocol) — Emergency intervention
- [Zeus Supervisor](../02-architecture/agents/zeus-orchestrator) — Pentarchy host

---

**Source:** Section 5.5 of [Digital Agentic Realm](../00-executive/digital-agentic-realm)
