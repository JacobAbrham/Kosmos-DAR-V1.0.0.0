# ADR-XXX: [Short Title of Decision]

**Status:** Proposed | Accepted | Deprecated | Superseded  
**Date:** YYYY-MM-DD  
**Decision Makers:** [Names or Roles]  
**Consulted:** [Names or Roles]  
**Informed:** [Names or Roles]  

---

## Context

### Problem Statement
What is the architectural problem or decision we need to address? Describe the issue clearly and concisely.

### Background
What is the context surrounding this decision? What factors led to this decision point?

- **Business Drivers:** What business needs drive this decision?
- **Technical Constraints:** What technical limitations or requirements exist?
- **Timeline:** Are there time-sensitive factors?
- **Stakeholders:** Who is impacted by this decision?

### Current State
What is the current situation? What exists today?

---

## Decision

### Chosen Solution
What did we decide to do? State the decision clearly and unambiguously.

**We will [action verb] [solution description].**

### Key Components
What are the main elements of this decision?

1. **Component 1:** Description
2. **Component 2:** Description
3. **Component 3:** Description

### Implementation Approach
How will this decision be implemented?

- **Phase 1:** Initial steps
- **Phase 2:** Follow-up actions
- **Phase 3:** Completion

---

## Consequences

### Positive Consequences
What becomes **easier** or **better** as a result of this decision?

✅ **Benefit 1:** Description  
✅ **Benefit 2:** Description  
✅ **Benefit 3:** Description  

### Negative Consequences
What becomes **harder** or requires **trade-offs**?

❌ **Trade-off 1:** Description and mitigation strategy  
❌ **Trade-off 2:** Description and mitigation strategy  
❌ **Trade-off 3:** Description and mitigation strategy  

### Risks & Mitigation
What risks does this decision introduce and how will we address them?

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Risk 1 | High/Med/Low | High/Med/Low | Mitigation strategy |
| Risk 2 | High/Med/Low | High/Med/Low | Mitigation strategy |

---

## Alternatives Considered

### Alternative 1: [Name]
**Description:** What was this alternative?

**Pros:**
- Advantage 1
- Advantage 2

**Cons:**
- Disadvantage 1
- Disadvantage 2

**Reason for Rejection:** Why didn't we choose this?

---

### Alternative 2: [Name]
**Description:** What was this alternative?

**Pros:**
- Advantage 1
- Advantage 2

**Cons:**
- Disadvantage 1
- Disadvantage 2

**Reason for Rejection:** Why didn't we choose this?

---

### Alternative 3: Do Nothing
**Description:** Maintain the status quo

**Pros:**
- No change risk
- No implementation cost

**Cons:**
- Problems persist
- Opportunity cost

**Reason for Rejection:** Why isn't this viable?

---

## Related Decisions

### Dependencies
- **ADR-XXX** - Decision that this depends on *(replace with actual link)*
- **ADR-YYY** - Related decision *(replace with actual link)*

### Supersedes
- **ADR-ZZZ** - This decision replaces (if applicable) *(replace with actual link)*

### Related Documentation
- **[System Topology](../topology)** - Architecture implementation
- **[Volume I: Governance](../../01-governance/index)** - Strategic alignment
- **[Technical RFC]()** - Link to technical RFC if applicable

---

## Implementation Timeline

| Phase | Activities | Timeline | Owner |
|-------|-----------|----------|-------|
| **Planning** | Design, resource allocation | Week 1-2 | Team Lead |
| **Implementation** | Development, testing | Week 3-6 | Dev Team |
| **Rollout** | Deployment, monitoring | Week 7-8 | DevOps |
| **Review** | Evaluation, lessons learned | Week 9 | All |

---

## Success Metrics

How will we measure if this decision was successful?

### Quantitative Metrics
- **Metric 1:** Target value (e.g., "95% uptime")
- **Metric 2:** Target value (e.g., "< 200ms latency")
- **Metric 3:** Target value (e.g., "50% cost reduction")

### Qualitative Metrics
- Developer satisfaction improves
- System maintainability increases
- Compliance requirements met

### Review Criteria
When and how will we review this decision?

- **Short-term Review:** 3 months after implementation
- **Long-term Review:** 12 months after implementation
- **Triggers for Re-evaluation:**
  - Technology landscape changes
  - Business requirements shift
  - Performance metrics not met

---

## Notes

### Open Questions
- [ ] Question 1 that needs resolution
- [ ] Question 2 that needs resolution

### Assumptions
- Assumption 1 underlying this decision
- Assumption 2 underlying this decision

### Future Considerations
- What might we need to revisit later?
- What follow-up decisions might be needed?

---

## Approval

| Role | Name | Date | Signature |
|------|------|------|-----------|
| **Chief Architect** | [Name] | YYYY-MM-DD | ✓ |
| **Tech Lead** | [Name] | YYYY-MM-DD | ✓ |
| **Security Architect** | [Name] | YYYY-MM-DD | ✓ |
| **Product Owner** | [Name] | YYYY-MM-DD | ✓ |

---

## Change Log

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| YYYY-MM-DD | 1.0 | [Name] | Initial draft |
| YYYY-MM-DD | 2.0 | [Name] | Updated after review |

---

## References

### Internal Documents
- [Document 1 Title](link)
- [Document 2 Title](link)

### External Resources
- [Article/Book Title](URL)
- [Standard/Specification](URL)

### Research & Analysis
- [Proof of Concept](link)
- [Benchmark Results](link)

---

**Last Updated:** YYYY-MM-DD  
**Document Owner:** [Role/Name]  
**Next Review:** YYYY-MM-DD

---

[← Back to ADR Index](index) | [Volume II: Architecture →](../index)

---

## Template Usage Instructions

1. **Copy this template** to create a new ADR:
   ```bash
   cp docs/02-architecture/adr/template.md \
      docs/02-architecture/adr/ADR-XXX-title.md
   ```

2. **Replace XXX** with the next sequential ADR number (e.g., ADR-004)

3. **Use kebab-case** for the filename (e.g., `ADR-004-api-gateway-selection.md`)

4. **Fill in all sections** - Delete sections that don't apply but keep the structure

5. **Update the status** as the ADR moves through the lifecycle

6. **Update the ADR index** in [index.md](index) when status changes

7. **Link generously** to related documentation

8. **Keep it concise** but complete - aim for 2-3 pages

---

*This template is based on Michael Nygard's ADR format with enhancements for KOSMOS documentation standards.*
