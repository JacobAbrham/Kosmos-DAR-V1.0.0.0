# Legal Framework

**Document Type:** Governance & Legal Compliance  
**Owner:** Chief Legal Officer  
**Reviewers:** General Counsel, Data Protection Officer, Compliance Team  
**Review Cadence:** Quarterly (or upon regulatory changes)  
**Last Updated:** 2025-12-11  
**Status:** 🟢 Active

---

## Purpose

The Legal Framework establishes KOSMOS's approach to compliance with applicable AI and data protection regulations across all operational jurisdictions. This document provides guidance on legal requirements, liability management, contractual obligations, and regulatory reporting.

---

## Regulatory Landscape

### Applicable Regulations by Jurisdiction

#### European Union

##### 1. **EU AI Act (Regulation 2024/1689)**
**Status:** Applicable from August 2026  
**Classification:** High-Risk AI System

**KOSMOS Classification Rationale:**
- Automated decision-making affecting individuals
- Processing of personal data
- Potential for bias and discrimination
- Critical business applications

**Key Obligations:**
- [ ] Risk management system (Article 9)
- [x] Data governance (Article 10)
- [x] Technical documentation (Article 11)
- [x] Record-keeping (Article 12)
- [x] Transparency and information provision (Article 13)
- [x] Human oversight (Article 14)
- [x] Accuracy, robustness, cybersecurity (Article 15)
- [ ] Conformity assessment (Article 43)
- [ ] CE marking (Article 49)
- [ ] Post-market monitoring (Article 72)

**Compliance Status:** 85% compliant (in preparation phase)  
**Gap Remediation Deadline:** February 2026

---

##### 2. **GDPR (General Data Protection Regulation)**
**Status:** Fully applicable  
**Regulation:** 2016/679

**Lawful Basis for Processing:**
- **Article 6(1)(b):** Processing necessary for contract performance
- **Article 6(1)(c):** Legal obligation compliance
- **Article 6(1)(f):** Legitimate interests (with balancing test)

**Special Category Data:**
- KOSMOS does NOT process Article 9 data (race, health, etc.) by design
- If future processing needed: Explicit consent required (Article 9(2)(a))

**Data Subject Rights Implementation:**

| Right | Article | Implementation | Response Time |
|-------|---------|----------------|---------------|
| Right to be informed | 13-14 | Privacy notices | Immediate |
| Right of access | 15 | Self-service portal | ≤30 days |
| Right to rectification | 16 | Update mechanisms | ≤30 days |
| Right to erasure | 17 | [Amnesia Protocol](../05-human-factors/amnesia-protocol.md) | ≤30 days |
| Right to restrict processing | 18 | Processing flags | ≤30 days |
| Right to data portability | 20 | Export functionality | ≤30 days |
| Right to object | 21 | Opt-out mechanisms | Immediate |
| Automated decision-making | 22 | Human review | Case-by-case |

**DPIA Requirement:**
- ✅ Data Protection Impact Assessment completed
- See: [DPIA Template](../appendices/templates/dpia-template.md)
- Review: Annually or upon material changes

---

#### United States

##### 3. **California Consumer Privacy Act (CCPA) / CPRA**
**Status:** Applicable  
**Regulation:** California Civil Code §1798.100 et seq.

**Consumer Rights:**
- Right to know what personal information is collected
- Right to delete personal information
- Right to opt-out of sale/sharing
- Right to correct inaccurate information
- Right to limit use of sensitive personal information

**KOSMOS Compliance:**
- ✅ Privacy policy with CCPA disclosures
- ✅ "Do Not Sell or Share My Personal Information" link
- ✅ Data deletion workflow
- ✅ Authorized agent mechanism
- ⚠️ No sale/sharing of personal information (confirmed)

**Response Timeline:** 45 days (with 45-day extension if needed)

---

##### 4. **Federal Trade Commission (FTC) Act**
**Status:** Applicable  
**Focus:** Section 5 - Unfair or deceptive practices

**Compliance Requirements:**
- No deceptive claims about AI capabilities
- Transparent disclosure of AI use
- Reasonable data security measures
- Truth in advertising for AI products

**Recent FTC Guidance:**
- [FTC Blog: Aiming for truth, fairness, and equity in your company's use of AI](https://www.ftc.gov/business-guidance/blog/2021/04/aiming-truth-fairness-equity-your-companys-use-ai)

---

#### International

##### 5. **Other Jurisdictions**
| Jurisdiction | Regulation | Status | Notes |
|--------------|------------|--------|-------|
| United Kingdom | UK GDPR + Data Protection Act 2018 | Compliant | Similar to EU GDPR |
| Canada | PIPEDA | Applicable | Privacy obligations |
| Australia | Privacy Act 1988 | Applicable | APPs compliance |
| Brazil | LGPD | Applicable | Similar to GDPR |
| China | PIPL | Not applicable | No operations in China |
| Japan | APPI | Applicable | Adequacy decision with EU |

---

## Liability Framework

### Allocation of Responsibility

#### 1. **Product Liability**

**Legal Theory:** Strict liability for defective products

**KOSMOS Position:**
- AI outputs are considered "products" in some jurisdictions
- Quality assurance measures to minimize defects
- Insurance coverage for product liability claims

**Mitigation:**
- Comprehensive testing ([Model Cards](../03-engineering/model-cards/README.md))
- Clear terms of service with liability limitations
- Disclaimers for AI-generated content
- Professional liability insurance ($10M coverage)

---

#### 2. **Negligence**

**Elements:**
- Duty of care
- Breach of duty
- Causation
- Damages

**KOSMOS Duty of Care:**
- Reasonable skill and care in AI development
- Industry best practices
- Regular updates and maintenance
- Prompt incident response

**Standard of Care:**
- ISO/IEC 42001 (AI Management System)
- NIST AI Risk Management Framework
- IEEE ethical AI standards

---

#### 3. **Contract Liability**

**Key Contractual Terms:**

**Service Level Agreements (SLAs):**
- Availability: 99.9% uptime
- Response time: <200ms (p95)
- See [SLA/SLO](../04-operations/sla-slo.md)

**Warranties:**
- Limited warranty on service availability
- No warranty on AI output accuracy (express disclaimer)
- Warranty on data security measures

**Limitations of Liability:**
- Cap: 12 months of fees paid
- Exclusions: Indirect, consequential, punitive damages
- Carve-outs: Gross negligence, willful misconduct, data breaches

**Indemnification:**
- Customer indemnifies for their input data
- KOSMOS indemnifies for IP infringement claims
- Mutual indemnification for regulatory violations

---

#### 4. **Intellectual Property**

**Training Data:**
- Licensed or public domain data only
- Fair use analysis for copyrighted materials
- Opt-out mechanisms for content creators

**Model Weights:**
- Proprietary to KOSMOS (or licensed from providers)
- Trade secret protection
- No customer ownership claims

**Outputs:**
- Customer owns outputs (subject to license terms)
- KOSMOS retains right to use for improvement
- Watermarking for attribution ([Watermarking Standard](../03-engineering/watermarking-standard.md))

**Third-Party IP Claims:**
- Monitoring for copyright complaints
- DMCA takedown procedures
- Legal review of training data sources

---

## Data Protection Governance

### Data Processing Roles

#### KOSMOS as Data Controller

**Scope:**
- Customer account information
- Usage analytics
- Billing data
- Marketing communications

**Obligations:**
- Determine purposes and means of processing
- Ensure lawful basis for processing
- Implement appropriate technical measures
- Appoint Data Protection Officer (if required)

**DPO Contact:** dpo@nuvanta-holding.com

---

#### KOSMOS as Data Processor

**Scope:**
- Customer input data for AI processing
- Temporary storage during request handling

**Obligations:**
- Process only on documented instructions
- Ensure confidentiality of processing
- Implement security measures (Article 32 GDPR)
- Assist with data subject rights requests
- Notify of data breaches within 72 hours
- Delete/return data upon contract termination

**Data Processing Agreements (DPA):**
- Standard clauses for all customers
- EU Standard Contractual Clauses (SCCs) for international transfers
- UK International Data Transfer Agreement (IDTA) where applicable

---

### Cross-Border Data Transfers

#### Transfer Mechanisms

**EU to Non-EU:**
1. **Adequacy Decision** (preferred)
   - Countries: UK, Japan, Canada, Israel, etc.
   - No additional safeguards needed

2. **Standard Contractual Clauses (SCCs)**
   - EC Decision 2021/914
   - Transfer Impact Assessment (TIA) required
   - Supplementary measures where needed

3. **Binding Corporate Rules (BCRs)**
   - Not currently implemented
   - Under consideration for 2026

**Current Transfer Inventory:**

| From | To | Data Type | Mechanism | TIA Status |
|------|-----|-----------|-----------|------------|
| EU | US | Customer data | SCCs | ✅ Completed |
| EU | UK | All data | Adequacy | N/A |
| EU | UAE | Metadata | SCCs | ✅ Completed |

---

### Data Retention

**Retention Schedule:**

| Data Category | Retention Period | Legal Basis | Deletion Method |
|---------------|------------------|-------------|-----------------|
| User accounts | Active + 30 days after deletion | Contract | Crypto-shredding |
| Conversation logs | 90 days | Legitimate interest | Automated purge |
| Billing records | 7 years | Legal obligation | Secure deletion |
| Audit logs | 3 years | Legal obligation | Automated purge |
| Training data | Permanent (anonymized) | Legitimate interest | N/A |
| Model backups | 1 year | Legitimate interest | Secure deletion |

**Deletion Procedures:**
- See [Amnesia Protocol](../05-human-factors/amnesia-protocol.md)
- NIST 800-88 media sanitization guidelines
- Verification of deletion completion

---

## Contractual Framework

### Master Services Agreement (MSA)

**Key Terms:**

**1. Scope of Services**
- AI model access via API
- Documentation and support
- Updates and maintenance

**2. Customer Obligations**
- Comply with Acceptable Use Policy
- Provide accurate account information
- Pay fees on time
- Indemnify for their content

**3. Intellectual Property**
- KOSMOS retains all IP in the service
- Customer retains IP in their input/output
- Limited license to KOSMOS for service provision

**4. Confidentiality**
- Mutual confidentiality obligations
- 5-year term post-termination
- Standard exceptions (public domain, etc.)

**5. Term and Termination**
- Annual term with auto-renewal
- 30-day termination notice
- Post-termination data deletion

**6. Limitation of Liability**
- Cap: 12 months fees
- No consequential damages
- Carve-outs for willful misconduct

**7. Dispute Resolution**
- Good faith negotiation (30 days)
- Mediation (if negotiation fails)
- Arbitration (binding, individual claims only)
- Governing law: United Arab Emirates (DIFC Courts)

---

### Data Processing Agreement (DPA)

**Purpose:** GDPR Article 28 compliance

**Key Clauses:**
1. Subject matter and duration
2. Nature and purpose of processing
3. Type of personal data
4. Categories of data subjects
5. Processor obligations (security, confidentiality, etc.)
6. Sub-processor authorization and list
7. Data subject rights assistance
8. Security measures (Article 32)
9. Breach notification (72 hours)
10. Deletion/return of data
11. Audit rights
12. International data transfers (SCCs attached)

**Standard Form:** Available at [contracts.nuvanta-holding.com/dpa]

---

### Acceptable Use Policy (AUP)

**Prohibited Uses:**
- Illegal activities
- Harassment, abuse, or harm
- Misinformation campaigns
- Spam or phishing
- Malware distribution
- Unauthorized access attempts
- Bypassing security measures
- Generating child sexual abuse material (CSAM)
- Extreme violence or gore
- Non-consensual intimate imagery

**Consequences:**
- Warning for first minor violation
- Temporary suspension for repeated violations
- Permanent termination for severe violations
- Law enforcement notification where required

**Enforcement:**
- Automated content filtering
- User reporting mechanisms
- Manual review for edge cases

---

## Regulatory Reporting

### Mandatory Notifications

#### 1. **Data Breaches**

**GDPR Article 33/34:**
- Notify supervisory authority within 72 hours
- Notify affected individuals if high risk
- Document all breaches (including non-notifiable)

**Notification Template:**
- Nature of breach
- Categories and number of data subjects affected
- Likely consequences
- Measures taken or proposed
- Contact details of DPO

**Process:**
1. Detection (automated monitoring)
2. Assessment (severity, scope)
3. Containment (incident response)
4. Notification (if required)
5. Remediation
6. Documentation

---

#### 2. **AI Incidents (EU AI Act)**

**Article 73 - Serious Incidents:**
- Death or serious health damage
- Serious and irreversible disruption of management of critical infrastructure
- Breach of obligations under Union law protecting fundamental rights
- Serious harm to property or environment

**Notification Timeline:** Without undue delay, no later than 15 days

**Reporting to:** National competent authority

---

#### 3. **Other Regulatory Notifications**

| Regulation | Trigger | Timeline | Authority |
|------------|---------|----------|-----------|
| FTC Act | Material changes to privacy practices | 30 days before | FTC (if investigation) |
| CCPA | Data breach affecting >500 residents | Without undue delay | California AG |
| SEC (if public) | Material cybersecurity incident | 4 business days | SEC |

---

## Compliance Monitoring

### Internal Audit Program

**Audit Schedule:**

| Area | Frequency | Last Audit | Next Audit |
|------|-----------|------------|------------|
| GDPR compliance | Annual | 2024-09-15 | 2025-09-15 |
| Data security | Semi-annual | 2024-11-20 | 2025-05-20 |
| Contract compliance | Annual | 2024-10-10 | 2025-10-10 |
| Training records | Quarterly | 2024-12-01 | 2025-03-01 |
| DPA compliance | Annual | 2024-08-30 | 2025-08-30 |

**Audit Scope:**
- Policy adherence
- Technical controls effectiveness
- Documentation completeness
- Training completion rates
- Incident response procedures

**Audit Findings:**
- Categorized by severity (Critical/High/Medium/Low)
- Remediation timelines assigned
- Tracking to closure
- Escalation for overdue items

---

### External Audits

**SOC 2 Type II:**
- Frequency: Annual
- Auditor: [Big 4 Firm]
- Scope: Security, Availability, Confidentiality
- Last Report: 2024-10-01
- Next Audit: 2025-10-01

**ISO 27001 Certification:**
- Status: Pursuing certification
- Target: Q2 2026
- Scope: Information security management

**ISO 42001 (AI Management):**
- Status: Gap assessment completed
- Target: Q4 2026

---

## Training and Awareness

### Mandatory Training

**All Employees:**
- [ ] Data Protection Basics (annual)
- [ ] Information Security (annual)
- [ ] Code of Conduct (annual)

**AI/ML Team:**
- [ ] Ethical AI Development (semi-annual)
- [ ] Bias Detection and Mitigation (annual)
- [ ] Model Documentation ([Model Cards](../03-engineering/model-cards/README.md))

**Legal/Compliance Team:**
- [ ] Advanced GDPR (annual)
- [ ] EU AI Act Updates (as needed)
- [ ] Contract Management (annual)

**Leadership:**
- [ ] AI Governance (annual)
- [ ] Risk Management (annual)
- [ ] Regulatory Landscape (quarterly briefings)

**Training Tracking:**
- LMS completion records
- Certificates of completion
- Remedial training for non-completion

---

## Incident Response

### Legal Incident Types

1. **Regulatory Inquiry**
   - Response: Legal counsel review
   - Timeline: Per regulator requirements
   - Escalation: General Counsel, CEO

2. **Data Breach**
   - Response: [Amnesia Protocol](../05-human-factors/amnesia-protocol.md)
   - Notification: Per regulatory requirements
   - Documentation: Breach register

3. **Subpoena/Legal Process**
   - Response: Legal review, scope limitation
   - Timeline: Court-ordered
   - Notification: Affected customers (if allowed)

4. **IP Infringement Claim**
   - Response: Legal assessment, removal if valid
   - Timeline: DMCA 24-48 hours, other as negotiated
   - Counter-notification: If claim invalid

5. **Contract Dispute**
   - Response: Contract review, negotiation
   - Escalation: Dispute resolution clause
   - Documentation: All communications

---

## Future Regulatory Developments

### Monitoring List

**2025-2026:**
- [ ] EU AI Act full enforcement (August 2026)
- [ ] US federal AI regulation proposals
- [ ] California AI transparency laws
- [ ] Updated FTC AI guidance
- [ ] UK AI regulation updates
- [ ] International AI standards (ISO, IEEE)

**Process:**
- Quarterly regulatory landscape reviews
- Legal counsel engagement
- Industry association participation
- Proactive compliance gap assessments

---

## Governance Structure

### Legal & Compliance Committee

**Composition:**
- Chief Legal Officer (Chair)
- Data Protection Officer
- Chief Information Security Officer
- Chief Compliance Officer
- External legal counsel (as needed)

**Meeting Cadence:**
- Monthly: Routine compliance review
- Quarterly: Deep-dive on specific regulations
- Ad-hoc: Regulatory changes or incidents

**Responsibilities:**
- Interpret regulatory requirements
- Approve policy updates
- Oversee compliance programs
- Review audit findings
- Escalate material issues to Board

---

## Key Contacts

<!-- Contact details are confidential - update in internal system -->

### Internal

| Role | Contact | Phone | Email |
|------|---------|-------|-------|
| Chief Legal Officer | *See internal directory* | *Internal* | legal@nuvanta-holding.com |
| Data Protection Officer | *See internal directory* | *Internal* | dpo@nuvanta-holding.com |
| General Counsel | *See internal directory* | *Internal* | counsel@nuvanta-holding.com |
| Compliance Officer | *See internal directory* | *Internal* | compliance@nuvanta-holding.com |

### External

| Type | Firm | Contact | Email |
|------|------|---------|-------|
| Outside Counsel | *Vendor selection pending* | - | - |
| EU GDPR Counsel | *Vendor selection pending* | - | - |
| Privacy Consultant | *Vendor selection pending* | - | - |
| Insurance Broker | *Vendor selection pending* | - | - |

---

## References

### Internal Documents
- [Risk Registry](risk-registry.md)
- [Ethics Scorecard](ethics-scorecard.md)
- [RACI Matrix](raci-matrix.md)
- [Amnesia Protocol](../05-human-factors/amnesia-protocol.md)
- [DPIA Template](../appendices/templates/dpia-template.md)

### External Resources

**EU Regulations:**
- [EU AI Act](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689)
- [GDPR](https://gdpr-info.eu/)
- [EDPB Guidelines](https://edpb.europa.eu/our-work-tools/general-guidance/guidelines-recommendations-best-practices_en)

**US Regulations:**
- [CCPA/CPRA Text](https://oag.ca.gov/privacy/ccpa)
- [FTC AI Guidance](https://www.ftc.gov/business-guidance/blog/2021/04/aiming-truth-fairness-equity-your-companys-use-ai)
- [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework)

**Standards:**
- [ISO/IEC 42001](https://www.iso.org/standard/81230.html) - AI Management System
- [ISO 27001](https://www.iso.org/isoiec-27001-information-security.html) - Information Security
- [IEEE 7000 Series](https://standards.ieee.org/industry-connections/ec/autonomous-systems.html) - Ethical AI

---

## Appendices

### Appendix A: Regulatory Change Log

| Date | Regulation | Change | Impact | Action Taken |
|------|------------|--------|--------|--------------|
| 2024-08-01 | EU AI Act | Official publication | Prepare for 2026 | Gap assessment initiated |
| 2024-01-01 | CPRA | Full enforcement | Consumer rights expansion | Updated privacy policy |

### Appendix B: Legal Opinions Log

Confidential legal opinions maintained separately in legal department files.

### Appendix C: Litigation Register

Confidential litigation tracking maintained separately by legal counsel.

---

**Next Review:** March 2026 (Quarterly)  
**Document Owner:** legal@nuvanta-holding.com  
**Compliance Hotline:** +971-4-345-6789 (24/7, anonymous reporting available)

---

**ATTORNEY-CLIENT PRIVILEGE NOTICE:**  
This document may contain information protected by attorney-client privilege. Legal advice should be sought from qualified counsel for specific situations.
