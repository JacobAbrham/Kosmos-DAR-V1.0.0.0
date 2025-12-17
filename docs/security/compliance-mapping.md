# Compliance Mapping

**Document Type:** Compliance & Governance  
**Owner:** Security & Compliance Team  
**Reviewers:** CISO, Legal, External Auditors  
**Review Cadence:** Annual (or after framework updates)  
**Last Updated:** 2025-12-13  
**Status:** 🟢 Active  
**Classification:** Internal - Confidential

---

## Executive Summary

This document maps KOSMOS security controls to major compliance frameworks including SOC 2 Type II, ISO 27001:2022, GDPR, and AI-specific regulations. It serves as a reference for audit preparation, gap analysis, and continuous compliance monitoring.

---

## Framework Coverage

| Framework | Scope | Status | Last Audit | Next Audit |
|-----------|-------|--------|------------|------------|
| SOC 2 Type II | Trust Services Criteria | 🟡 In Progress | N/A | Q2 2026 |
| ISO 27001:2022 | ISMS | 🟡 Planned | N/A | Q4 2026 |
| GDPR | EU Data Protection | 🟢 Implemented | N/A | Ongoing |
| EU AI Act | AI Systems | 🟡 Assessment | N/A | 2026 |
| NIST AI RMF | AI Risk Management | 🟢 Aligned | N/A | Ongoing |

---

## SOC 2 Type II Mapping

### Trust Services Criteria Coverage

```
┌─────────────────────────────────────────────────────────────────┐
│                    SOC 2 Trust Services Criteria                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│   │  Security   │  │Availability │  │ Processing  │            │
│   │   (CC)      │  │    (A)      │  │ Integrity   │            │
│   │             │  │             │  │    (PI)     │            │
│   │  ✅ 100%    │  │  ✅ 95%     │  │  ✅ 90%     │            │
│   └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                 │
│   ┌─────────────┐  ┌─────────────┐                             │
│   │Confidential │  │   Privacy   │                             │
│   │    (C)      │  │    (P)      │                             │
│   │             │  │             │                             │
│   │  ✅ 95%     │  │  ✅ 90%     │                             │
│   └─────────────┘  └─────────────┘                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Security (Common Criteria) Controls

| Control ID | Control Description | KOSMOS Implementation | Evidence |
|------------|--------------------|-----------------------|----------|
| **CC1.1** | Entity demonstrates commitment to integrity and ethical values | Code of conduct, Ethics policy, [AI Ethics Scorecard](../01-governance/ethics-scorecard.md) | Policy docs, training records |
| **CC1.2** | Board exercises oversight responsibility | Quarterly architecture reviews, [RACI Matrix](../01-governance/raci-matrix.md) | Meeting minutes, RACI |
| **CC1.3** | Management establishes structure and reporting lines | Documented org structure, [Kill Switch Protocol](../01-governance/kill-switch-protocol.md) | Org charts, escalation procedures |
| **CC2.1** | Entity obtains relevant information | [Risk Registry](../01-governance/risk-registry.md), audit logging | Risk assessments, logs |
| **CC2.2** | Entity internally communicates information | Incident response procedures, Slack channels | Runbooks, communication logs |
| **CC2.3** | Entity communicates externally | Status page, customer notifications | Status page, email templates |
| **CC3.1** | Entity specifies objectives | SLAs/SLOs defined, [SLA/SLO doc](../04-operations/sla-slo.md) | Service agreements |
| **CC3.2** | Entity identifies and analyzes risks | [Threat Model](threat-model.md), [Risk Registry](../01-governance/risk-registry.md) | Threat assessments |
| **CC3.3** | Entity considers potential for fraud | Audit logging, access controls | Audit logs, RBAC policies |
| **CC3.4** | Entity identifies and assesses changes | Change management, [ADR process](../02-architecture/adr/index.md) | ADRs, PRs |
| **CC4.1** | Entity selects ongoing evaluations | Automated testing, monitoring | Test results, dashboards |
| **CC4.2** | Entity evaluates and communicates deficiencies | Vulnerability management, incident reviews | Vuln reports, PIRs |
| **CC5.1** | Entity selects and develops control activities | Security architecture, [IAM](iam.md) | Architecture docs |
| **CC5.2** | Entity selects general controls over technology | Infrastructure security, [K8s RBAC](kubernetes.md) | K8s policies |
| **CC5.3** | Entity deploys through policies and procedures | Documented procedures, runbooks | Operations docs |
| **CC6.1** | Entity implements logical access security | [IAM](iam.md), RBAC, MFA | Auth configs |
| **CC6.2** | Entity registers and authorizes users | User provisioning, access reviews | User records |
| **CC6.3** | Entity removes access when appropriate | Offboarding procedures, access revocation | Audit logs |
| **CC6.4** | Entity restricts and manages privileged access | Admin access controls, break-glass procedures | Access policies |
| **CC6.5** | Entity restricts logical access to system components | Network policies, segmentation | Network configs |
| **CC6.6** | Entity manages points of entry | API gateway, WAF, [Security Architecture](architecture.md) | Gateway configs |
| **CC6.7** | Entity restricts transmission of data | TLS everywhere, mTLS for internal | TLS configs |
| **CC6.8** | Entity prevents unauthorized software | Container scanning, admission control | Scan reports |
| **CC7.1** | Entity detects and monitors for security events | Prometheus, Grafana, alerting | Dashboards, alerts |
| **CC7.2** | Entity monitors for anomalies | Anomaly detection, Langfuse | Monitoring configs |
| **CC7.3** | Entity evaluates security events | [Incident Response](../04-operations/incident-response/README.md) playbooks | IR procedures |
| **CC7.4** | Entity responds to identified security incidents | Incident response, [DR Plan](disaster-recovery.md) | IR logs, DR tests |
| **CC7.5** | Entity identifies and recovers from incidents | Recovery procedures, backups | Recovery logs |
| **CC8.1** | Entity authorizes and manages changes | CI/CD pipelines, approval gates | Deployment logs |
| **CC9.1** | Entity identifies and manages risk from vendors | Vendor assessments, [AIBOM](../03-engineering/aibom.md) | Vendor reviews |
| **CC9.2** | Entity assesses and manages risks from vendors | LLM provider evaluation, contracts | Contracts, SLAs |

### Availability Controls

| Control ID | Control Description | KOSMOS Implementation | Evidence |
|------------|--------------------|-----------------------|----------|
| **A1.1** | Entity maintains current capacity | HPA, resource monitoring | K8s metrics |
| **A1.2** | Entity authorizes and manages changes | [Deployment procedures](deployment.md) | Deployment logs |
| **A1.3** | Entity designs for recovery | [DR Plan](disaster-recovery.md), backup strategy | DR tests, backups |

### Processing Integrity Controls

| Control ID | Control Description | KOSMOS Implementation | Evidence |
|------------|--------------------|-----------------------|----------|
| **PI1.1** | Entity obtains data from reliable sources | Input validation, data quality checks | Validation logs |
| **PI1.2** | Entity protects processing integrity | Data validation, checksums | Processing logs |
| **PI1.3** | Entity addresses processing errors | Error handling, retry logic | Error logs |
| **PI1.4** | Entity produces accurate output | Output validation, model monitoring | Output logs |
| **PI1.5** | Entity stores data properly | Encrypted storage, backups | Storage configs |

### Confidentiality Controls

| Control ID | Control Description | KOSMOS Implementation | Evidence |
|------------|--------------------|-----------------------|----------|
| **C1.1** | Entity identifies confidential data | Data classification, [Threat Model](threat-model.md) | Classification docs |
| **C1.2** | Entity disposes of confidential data | Retention policies, secure deletion | Retention configs |

### Privacy Controls

| Control ID | Control Description | KOSMOS Implementation | Evidence |
|------------|--------------------|-----------------------|----------|
| **P1.1** | Entity provides notice | Privacy policy, consent mechanisms | Privacy policy |
| **P2.1** | Entity communicates choices | User preferences, opt-out | UI controls |
| **P3.1** | Entity collects data per consent | Consent management | Consent logs |
| **P4.1** | Entity uses data as disclosed | Purpose limitation controls | Processing records |
| **P5.1** | Entity retains data appropriately | Retention policies | Retention configs |
| **P6.1** | Entity discloses data as authorized | Access controls, audit logs | Disclosure logs |
| **P7.1** | Entity provides access to data subjects | Export functionality | API endpoints |
| **P8.1** | Entity corrects data upon request | Update mechanisms | Update logs |

---

## ISO 27001:2022 Mapping

### Annex A Control Mapping

| Control | Description | KOSMOS Implementation | Status |
|---------|-------------|----------------------|--------|
| **A.5.1** | Policies for information security | Security policies, [Governance docs](../01-governance/index.md) | ✅ |
| **A.5.2** | Information security roles | RACI matrix, security team | ✅ |
| **A.5.3** | Segregation of duties | RBAC, approval workflows | ✅ |
| **A.5.4** | Management responsibilities | Training, awareness | ✅ |
| **A.5.5** | Contact with authorities | Incident reporting procedures | ✅ |
| **A.5.6** | Contact with special interest groups | Security community engagement | ✅ |
| **A.5.7** | Threat intelligence | Vulnerability feeds, CVE monitoring | ✅ |
| **A.5.8** | Information security in project mgmt | Security reviews in SDLC | ✅ |
| **A.5.9** | Inventory of information assets | [AIBOM](../03-engineering/aibom.md), asset register | ✅ |
| **A.5.10** | Acceptable use | Acceptable use policy | ✅ |
| **A.5.11** | Return of assets | Offboarding procedures | ✅ |
| **A.5.12** | Classification of information | Data classification scheme | ✅ |
| **A.5.13** | Labelling of information | Classification labels | ✅ |
| **A.5.14** | Information transfer | TLS, encryption policies | ✅ |
| **A.5.15** | Access control | [IAM](iam.md), RBAC | ✅ |
| **A.5.16** | Identity management | Keycloak, user lifecycle | ✅ |
| **A.5.17** | Authentication information | Password policies, MFA | ✅ |
| **A.5.18** | Access rights | Least privilege, access reviews | ✅ |
| **A.5.19** | Info security in supplier relations | Vendor assessments | ✅ |
| **A.5.20** | Addressing security in agreements | Contract security clauses | ✅ |
| **A.5.21** | Managing security in ICT supply chain | SBOM, dependency scanning | ✅ |
| **A.5.22** | Monitoring supplier services | SLA monitoring | ✅ |
| **A.5.23** | Info security for cloud services | Cloud security configs | ✅ |
| **A.5.24** | Incident management planning | [Incident Response](../04-operations/incident-response/README.md) | ✅ |
| **A.5.25** | Assessment and decision on events | Incident triage procedures | ✅ |
| **A.5.26** | Response to incidents | IR playbooks | ✅ |
| **A.5.27** | Learning from incidents | Post-incident reviews | ✅ |
| **A.5.28** | Collection of evidence | Audit logging, forensics | ✅ |
| **A.5.29** | Info security during disruption | [Business Continuity](../05-human-factors/business-continuity.md) | ✅ |
| **A.5.30** | ICT readiness for business continuity | [DR Plan](disaster-recovery.md) | ✅ |
| **A.5.31** | Legal requirements | Legal framework compliance | ✅ |
| **A.5.32** | Intellectual property rights | License management | ✅ |
| **A.5.33** | Protection of records | Data retention, backups | ✅ |
| **A.5.34** | Privacy and PII protection | GDPR compliance | ✅ |
| **A.5.35** | Independent review | Annual audits | 🟡 |
| **A.5.36** | Compliance with policies | Compliance monitoring | ✅ |
| **A.5.37** | Documented operating procedures | Runbooks, SOPs | ✅ |
| **A.6.1** | Screening | Background checks | ✅ |
| **A.6.2** | Terms of employment | Security agreements | ✅ |
| **A.6.3** | Security awareness | Training programs | ✅ |
| **A.6.4** | Disciplinary process | HR policies | ✅ |
| **A.6.5** | Responsibilities after termination | Offboarding procedures | ✅ |
| **A.6.6** | Confidentiality agreements | NDAs | ✅ |
| **A.6.7** | Remote working | Remote access policies | ✅ |
| **A.6.8** | Security event reporting | Incident reporting | ✅ |
| **A.7.1** | Physical security perimeters | Cloud provider controls | ✅ |
| **A.7.2** | Physical entry | Cloud provider controls | ✅ |
| **A.7.3** | Securing offices/facilities | Cloud provider controls | ✅ |
| **A.7.4** | Physical security monitoring | Cloud provider controls | ✅ |
| **A.7.5** | Protecting against threats | Environmental controls | ✅ |
| **A.7.6** | Working in secure areas | Cloud provider controls | ✅ |
| **A.7.7** | Clear desk and screen | Policy enforcement | ✅ |
| **A.7.8** | Equipment siting | Cloud architecture | ✅ |
| **A.7.9** | Security of assets off-premises | Device management | ✅ |
| **A.7.10** | Storage media | Encryption, secure disposal | ✅ |
| **A.7.11** | Supporting utilities | Cloud provider controls | ✅ |
| **A.7.12** | Cabling security | Cloud provider controls | ✅ |
| **A.7.13** | Equipment maintenance | Managed services | ✅ |
| **A.7.14** | Secure disposal | Secure deletion procedures | ✅ |
| **A.8.1** | User endpoint devices | Endpoint security | ✅ |
| **A.8.2** | Privileged access rights | Admin controls, break-glass | ✅ |
| **A.8.3** | Information access restriction | RBAC, data classification | ✅ |
| **A.8.4** | Access to source code | Repository access controls | ✅ |
| **A.8.5** | Secure authentication | MFA, strong passwords | ✅ |
| **A.8.6** | Capacity management | Autoscaling, monitoring | ✅ |
| **A.8.7** | Protection against malware | Container scanning | ✅ |
| **A.8.8** | Management of vulnerabilities | Vulnerability management | ✅ |
| **A.8.9** | Configuration management | IaC, GitOps | ✅ |
| **A.8.10** | Information deletion | Retention, secure delete | ✅ |
| **A.8.11** | Data masking | PII masking in logs | ✅ |
| **A.8.12** | Data leakage prevention | DLP controls | 🟡 |
| **A.8.13** | Information backup | Backup procedures | ✅ |
| **A.8.14** | Redundancy | Multi-AZ, HA | ✅ |
| **A.8.15** | Logging | Centralized logging | ✅ |
| **A.8.16** | Monitoring activities | Observability stack | ✅ |
| **A.8.17** | Clock synchronization | NTP, cloud provider | ✅ |
| **A.8.18** | Use of privileged utilities | Restricted admin tools | ✅ |
| **A.8.19** | Installation of software | Admission control | ✅ |
| **A.8.20** | Network security | Network policies, segmentation | ✅ |
| **A.8.21** | Security of network services | TLS, mTLS | ✅ |
| **A.8.22** | Segregation of networks | Namespace isolation | ✅ |
| **A.8.23** | Web filtering | WAF, content filtering | ✅ |
| **A.8.24** | Use of cryptography | Encryption standards | ✅ |
| **A.8.25** | Secure development lifecycle | SDLC, security reviews | ✅ |
| **A.8.26** | Application security requirements | Security requirements | ✅ |
| **A.8.27** | Secure system architecture | [Security Architecture](architecture.md) | ✅ |
| **A.8.28** | Secure coding | Code review, SAST | ✅ |
| **A.8.29** | Security testing | Penetration testing | 🟡 |
| **A.8.30** | Outsourced development | Vendor security reviews | ✅ |
| **A.8.31** | Separation of environments | Dev/Staging/Prod separation | ✅ |
| **A.8.32** | Change management | [Deployment procedures](deployment.md) | ✅ |
| **A.8.33** | Test information | Test data management | ✅ |
| **A.8.34** | Protection during audit testing | Audit controls | ✅ |

---

## GDPR Compliance

### Article Mapping

| Article | Requirement | KOSMOS Implementation |
|---------|-------------|----------------------|
| **Art. 5** | Principles relating to processing | Data minimization, purpose limitation |
| **Art. 6** | Lawful basis for processing | Consent management, legitimate interest |
| **Art. 7** | Conditions for consent | Explicit consent, withdrawal mechanisms |
| **Art. 12** | Transparent information | Privacy policy, data subject notices |
| **Art. 13/14** | Information to be provided | Privacy notices, collection disclosures |
| **Art. 15** | Right of access | Data export API |
| **Art. 16** | Right to rectification | Data update mechanisms |
| **Art. 17** | Right to erasure | Data deletion procedures |
| **Art. 18** | Right to restriction | Processing restriction controls |
| **Art. 20** | Right to data portability | Export in standard formats |
| **Art. 21** | Right to object | Opt-out mechanisms |
| **Art. 22** | Automated decision-making | Human oversight, explainability |
| **Art. 25** | Data protection by design | Privacy-first architecture |
| **Art. 30** | Records of processing | Processing activity register |
| **Art. 32** | Security of processing | Technical/organizational measures |
| **Art. 33** | Breach notification (authority) | 72-hour notification procedure |
| **Art. 34** | Breach notification (subjects) | Communication procedures |
| **Art. 35** | DPIA | [DPIA Template](../appendices/templates/dpia-template.md) |
| **Art. 37-39** | DPO | DPO appointed, contact info |
| **Art. 44-49** | International transfers | SCCs, adequacy decisions |

### Data Subject Request Procedures

```python
# Data subject request handling
class DSRHandler:
    """Handle GDPR data subject requests."""
    
    async def handle_access_request(self, subject_id: str) -> dict:
        """Art. 15 - Right of access."""
        data = await self.collect_all_personal_data(subject_id)
        return {
            "processing_purposes": self.get_purposes(),
            "categories": self.get_data_categories(data),
            "recipients": self.get_recipients(),
            "retention_period": self.get_retention_periods(),
            "source": self.get_data_sources(),
            "data": data
        }
    
    async def handle_erasure_request(self, subject_id: str) -> dict:
        """Art. 17 - Right to erasure."""
        # Verify no legal hold
        if await self.has_legal_hold(subject_id):
            return {"status": "denied", "reason": "legal_obligation"}
        
        # Delete from all systems
        await self.delete_from_primary_db(subject_id)
        await self.delete_from_backups(subject_id)
        await self.delete_from_caches(subject_id)
        await self.delete_from_logs(subject_id)
        
        return {"status": "completed", "timestamp": datetime.utcnow()}
    
    async def handle_portability_request(self, subject_id: str) -> bytes:
        """Art. 20 - Right to data portability."""
        data = await self.collect_all_personal_data(subject_id)
        return json.dumps(data, indent=2).encode('utf-8')
```

---

## EU AI Act Compliance

### Risk Classification

| Category | Description | KOSMOS Status |
|----------|-------------|---------------|
| **Unacceptable Risk** | Prohibited AI systems | N/A - Not applicable |
| **High Risk** | AI in regulated domains | 🟡 Assessment needed |
| **Limited Risk** | Transparency obligations | ✅ Implemented |
| **Minimal Risk** | No specific obligations | ✅ Compliant |

### High-Risk AI Requirements (if applicable)

| Requirement | Article | Implementation |
|-------------|---------|----------------|
| Risk management system | Art. 9 | [Risk Registry](../01-governance/risk-registry.md) |
| Data governance | Art. 10 | Data quality controls |
| Technical documentation | Art. 11 | [Model Cards](../03-engineering/model-cards/README.md) |
| Record-keeping | Art. 12 | Audit logging |
| Transparency | Art. 13 | User disclosures |
| Human oversight | Art. 14 | [Kill Switch](../01-governance/kill-switch-protocol.md) |
| Accuracy, robustness, security | Art. 15 | Testing, monitoring |

### Transparency Requirements

```python
# AI transparency disclosure
class AIDisclosure:
    """EU AI Act transparency compliance."""
    
    def get_disclosure(self) -> dict:
        return {
            "system_name": "KOSMOS AI Operating System",
            "provider": "Nuvanta Holding",
            "ai_generated": True,
            "capabilities": [
                "Natural language understanding",
                "Document summarization",
                "Task orchestration"
            ],
            "limitations": [
                "May produce inaccurate information",
                "Limited knowledge cutoff",
                "Cannot access real-time data"
            ],
            "human_oversight": True,
            "contact": "ai-governance@nuvanta-holding.com"
        }
```

---

## NIST AI RMF Alignment

### Core Functions Mapping

| Function | Category | KOSMOS Implementation |
|----------|----------|----------------------|
| **GOVERN** | Policies & Accountability | [Governance Volume](../01-governance/index.md) |
| **MAP** | Context & Risk Framing | [Risk Registry](../01-governance/risk-registry.md) |
| **MEASURE** | Risk Assessment | [Threat Model](threat-model.md), monitoring |
| **MANAGE** | Risk Mitigation | Controls, [Kill Switch](../01-governance/kill-switch-protocol.md) |

### Trustworthy AI Characteristics

| Characteristic | Implementation | Evidence |
|----------------|----------------|----------|
| **Valid and Reliable** | Testing, validation, [Model Cards](../03-engineering/model-cards/README.md) | Test results |
| **Safe** | Safety controls, guardrails | Safety logs |
| **Secure and Resilient** | [Security Architecture](architecture.md) | Security assessments |
| **Accountable and Transparent** | Audit logs, explainability | Audit trails |
| **Explainable and Interpretable** | Model explanations | Explanation outputs |
| **Privacy-Enhanced** | GDPR compliance, PETs | Privacy assessments |
| **Fair** | Bias testing, fairness metrics | Fairness reports |

---

## Audit Preparation

### Evidence Collection

| Control Area | Evidence Type | Location | Retention |
|--------------|--------------|----------|-----------|
| Access Control | Access logs, RBAC configs | SIEM, K8s | 1 year |
| Change Management | Deployment logs, PRs | GitHub, CI/CD | 1 year |
| Incident Response | IR tickets, post-mortems | Jira, Wiki | 3 years |
| Security Testing | Scan reports, pen test results | Security tools | 1 year |
| Training | Training records, certificates | HR system | Employment + 3 years |
| Risk Management | Risk assessments, reviews | GRC platform | 5 years |

### Audit Schedule

| Audit Type | Frequency | Scope | Responsible |
|------------|-----------|-------|-------------|
| Internal Security Audit | Quarterly | All controls | Security Team |
| External Penetration Test | Annual | Production | Third-party |
| SOC 2 Type II | Annual | Trust Services Criteria | External auditor |
| ISO 27001 Surveillance | Annual | ISMS | External auditor |
| AI Ethics Review | Semi-annual | AI systems | Ethics Board |

---

## Related Documentation

- [Threat Model](threat-model.md)
- [Security Architecture](architecture.md)
- [Risk Registry](../01-governance/risk-registry.md)
- [AI Ethics Scorecard](../01-governance/ethics-scorecard.md)
- [Model Cards](../03-engineering/model-cards/README.md)

---

**Document Owner:** compliance@nuvanta-holding.com  
**DPO Contact:** dpo@nuvanta-holding.com  
**External Auditor:** [To be assigned]
