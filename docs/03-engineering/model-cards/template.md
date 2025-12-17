# Model Card: [Model Name]

**Model ID:** MC-XXX  
**Version:** vX.Y.Z  
**Status:** Draft | Under Review | Approved | Published | Deprecated  
**Last Updated:** YYYY-MM-DD  

---

## Model Details

### Basic Information

| Field | Value |
|-------|-------|
| **Model Name** | [Full model name] |
| **Model ID** | MC-XXX |
| **Version** | vX.Y.Z |
| **Model Type** | [Classification / Regression / Generation / etc.] |
| **Architecture** | [e.g., Transformer, GPT-4, Custom CNN, etc.] |
| **Framework** | [PyTorch, TensorFlow, JAX, etc.] |
| **Model Size** | [Parameters count, e.g., 175B parameters] |
| **License** | [Apache 2.0, Proprietary, MIT, etc.] |

### Development Information

| Field | Value |
|-------|-------|
| **Developer** | [Team/Organization name] |
| **Model Owner** | [Name and contact] |
| **Training Date** | YYYY-MM-DD |
| **Release Date** | YYYY-MM-DD |
| **Model Repository** | [Link to model storage] |
| **Documentation** | [Link to additional docs] |

### Version History

| Version | Date | Changes | Status |
|---------|------|---------|--------|
| v1.0.0 | YYYY-MM-DD | Initial release | Deprecated |
| v2.0.0 | YYYY-MM-DD | Major architecture update | Active |

---

## Intended Use

### Primary Use Cases

Describe the primary intended uses of this model:

1. **Use Case 1:** [Detailed description]
   - **Scenario:** [When and where this applies]
   - **Users:** [Who should use this]
   - **Expected Output:** [What the model produces]

2. **Use Case 2:** [Detailed description]
   - **Scenario:** [When and where this applies]
   - **Users:** [Who should use this]
   - **Expected Output:** [What the model produces]

### Out-of-Scope Use Cases

❌ **DO NOT use this model for:**

1. **[Prohibited Use 1]** - [Why this is inappropriate]
2. **[Prohibited Use 2]** - [Why this is inappropriate]
3. **[Prohibited Use 3]** - [Why this is inappropriate]

### Target Users

- **Primary Users:** [Technical level, role, expertise required]
- **Secondary Users:** [Other potential users]
- **Expertise Required:** [Minimal, Moderate, Expert]

### Deployment Environment

- **Production Environment:** [Cloud, On-premise, Edge]
- **Compute Requirements:** [CPU/GPU specs, memory]
- **Dependencies:** [Libraries, services, APIs]
- **Latency Requirements:** [Response time expectations]

---

## Training Data

### Dataset Description

**Dataset Name:** [Name of primary training dataset]  
**Dataset Size:** [Number of examples, tokens, images, etc.]  
**Data Sources:** [Where the data came from]  
**Collection Period:** [Time range of data collection]  
**Languages:** [For text models]  
**Geographic Coverage:** [If relevant]

### Data Composition

| Category | Count | Percentage |
|----------|-------|------------|
| Category 1 | X,XXX | XX% |
| Category 2 | X,XXX | XX% |
| Category 3 | X,XXX | XX% |

### Data Collection & Preprocessing

**Collection Method:**
- [How data was collected]
- [Data sources and APIs]
- [Consent and privacy considerations]

**Preprocessing Steps:**
1. [Preprocessing step 1]
2. [Preprocessing step 2]
3. [Preprocessing step 3]

**Data Cleaning:**
- [Deduplication methods]
- [Quality filters applied]
- [Removed content types]

**Data Augmentation:**
- [Augmentation techniques if used]
- [Synthetic data generation if applicable]

### Known Biases in Training Data

⚠️ **Identified Biases:**

1. **Demographic Bias:** [Description and impact]
2. **Geographic Bias:** [Description and impact]
3. **Temporal Bias:** [Description and impact]
4. **Content Bias:** [Description and impact]

**Mitigation Strategies:**
- [How biases were addressed]
- [Remaining known limitations]

---

## Performance Metrics

### Evaluation Methodology

**Test Set:**
- **Size:** [Number of test examples]
- **Source:** [Where test data came from]
- **Split Strategy:** [How train/test split was done]

**Evaluation Metrics:**
- [Metric 1: Why it was chosen]
- [Metric 2: Why it was chosen]
- [Metric 3: Why it was chosen]

### Overall Performance

| Metric | Value | Confidence Interval | Baseline |
|--------|-------|---------------------|----------|
| Accuracy | XX.X% | [XX.X%, XX.X%] | XX.X% |
| Precision | XX.X% | [XX.X%, XX.X%] | XX.X% |
| Recall | XX.X% | [XX.X%, XX.X%] | XX.X% |
| F1 Score | XX.X% | [XX.X%, XX.X%] | XX.X% |

### Performance by Subgroup

#### Demographic Performance

| Subgroup | Accuracy | Precision | Recall | F1 Score |
|----------|----------|-----------|--------|----------|
| Group A | XX.X% | XX.X% | XX.X% | XX.X% |
| Group B | XX.X% | XX.X% | XX.X% | XX.X% |
| Group C | XX.X% | XX.X% | XX.X% | XX.X% |

**Fairness Analysis:**
- **Disparate Impact Ratio:** X.XX (threshold: >0.8)
- **Equal Opportunity Difference:** X.XX (threshold: <0.1)
- **Demographic Parity:** ✅/❌ Achieved/Not Achieved

### Benchmark Comparisons

| Model | Accuracy | Speed | Size | Cost |
|-------|----------|-------|------|------|
| Our Model | XX.X% | XXms | XGB | $X.XX |
| Baseline | XX.X% | XXms | XGB | $X.XX |
| SOTA | XX.X% | XXms | XGB | $X.XX |

---

## Ethical Considerations

### Bias Analysis

**Methodology:**
- [Tools used for bias detection]
- [Metrics calculated]
- [Evaluation criteria]

**Findings:**

| Bias Type | Severity | Description | Mitigation |
|-----------|----------|-------------|------------|
| Gender Bias | Low/Med/High | [Details] | [Actions taken] |
| Racial Bias | Low/Med/High | [Details] | [Actions taken] |
| Age Bias | Low/Med/High | [Details] | [Actions taken] |

### Fairness Metrics

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Demographic Parity | <0.1 diff | X.XX | ✅/❌ |
| Equal Opportunity | <0.1 diff | X.XX | ✅/❌ |
| Equalized Odds | <0.1 diff | X.XX | ✅/❌ |

### Privacy Considerations

**Data Privacy:**
- [PII handling procedures]
- [Data retention policies]
- [Anonymization methods]

**Model Privacy:**
- [Risk of memorization]
- [Differential privacy techniques]
- [Privacy budget if applicable]

### Environmental Impact

**Carbon Footprint:**
- **Training Emissions:** [X tons CO2e]
- **Inference Emissions:** [X kg CO2e per 1M requests]
- **Total Energy Consumption:** [X kWh]

**Compute Resources:**
- **Training Time:** [X hours on Y GPUs]
- **Hardware:** [GPU/TPU types used]
- **Cloud Region:** [Data center location]

---

## Limitations & Risks

### Known Limitations

1. **Limitation 1:** [Description]
   - **Impact:** [How this affects performance]
   - **Frequency:** [How often this occurs]
   - **Workaround:** [If available]

2. **Limitation 2:** [Description]
   - **Impact:** [How this affects performance]
   - **Frequency:** [How often this occurs]
   - **Workaround:** [If available]

### Failure Modes

| Failure Mode | Probability | Impact | Detection | Mitigation |
|--------------|-------------|--------|-----------|------------|
| Mode 1 | Low/Med/High | Low/Med/High | [How to detect] | [How to handle] |
| Mode 2 | Low/Med/High | Low/Med/High | [How to detect] | [How to handle] |

### Edge Cases

**Known Edge Cases:**
1. [Edge case 1 and behavior]
2. [Edge case 2 and behavior]
3. [Edge case 3 and behavior]

### Potential for Misuse

⚠️ **Misuse Scenarios:**

1. **Misuse Type 1:** [Description]
   - **Risk Level:** High/Medium/Low
   - **Prevention:** [Safeguards in place]

2. **Misuse Type 2:** [Description]
   - **Risk Level:** High/Medium/Low
   - **Prevention:** [Safeguards in place]

### Technical Limitations

- **Context Window:** [If applicable, e.g., 4096 tokens]
- **Language Support:** [Supported languages]
- **Input Formats:** [Accepted formats]
- **Output Constraints:** [Format limitations]

---

## Recommendations

### Best Practices

✅ **Do:**
1. [Recommended practice 1]
2. [Recommended practice 2]
3. [Recommended practice 3]

❌ **Don't:**
1. [Practice to avoid 1]
2. [Practice to avoid 2]
3. [Practice to avoid 3]

### Monitoring Requirements

**Required Monitoring:**
- **Performance Metrics:** [What to track]
- **Drift Detection:** [How to monitor]
- **Fairness Metrics:** [Ongoing evaluation]
- **Cost Tracking:** [Budget monitoring]

**Alert Thresholds:**
- **Accuracy Drop:** >5% decrease
- **Latency Increase:** >20% increase
- **Error Rate:** >1% of requests
- **Bias Metrics:** Disparity ratio <0.8

### Update Schedule

| Update Type | Frequency | Next Update | Owner |
|-------------|-----------|-------------|-------|
| Model Retraining | Quarterly | YYYY-MM-DD | [Name] |
| Performance Review | Monthly | YYYY-MM-DD | [Name] |
| Fairness Audit | Quarterly | YYYY-MM-DD | [Name] |
| Security Scan | Monthly | YYYY-MM-DD | [Name] |

### Integration Guidelines

**API Usage:**
```python
# Example integration code
from model_api import ModelClient

client = ModelClient(model_id="MC-XXX", version="vX.Y.Z")
response = client.predict(input_data)
```

**Error Handling:**
```python
try:
    result = client.predict(input_data)
except ValidationError:
    # Handle invalid input
except ModelUnavailable:
    # Handle service issues
```

---

## Approval & Review

### Review Status

| Review Type | Reviewer | Date | Status | Comments |
|-------------|----------|------|--------|----------|
| Technical | [Name] | YYYY-MM-DD | ✅/⏳ | [Notes] |
| Ethics | [Name] | YYYY-MM-DD | ✅/⏳ | [Notes] |
| Security | [Name] | YYYY-MM-DD | ✅/⏳ | [Notes] |
| Legal | [Name] | YYYY-MM-DD | ✅/⏳ | [Notes] |
| Final Approval | [Name] | YYYY-MM-DD | ✅/⏳ | [Notes] |

### Compliance

- [ ] NIST AI RMF requirements met
- [ ] EU AI Act requirements met (if applicable)
- [ ] ISO 42001 requirements met
- [ ] Internal governance requirements met
- [ ] Data protection requirements met
- [ ] Ethical review completed
- [ ] Security scan passed
- [ ] Performance benchmarks met

---

## Contact Information

| Role | Contact | Responsibility |
|------|---------|----------------|
| **Model Owner** | [name@email.com] | Overall accountability |
| **Technical Lead** | [name@email.com] | Technical questions |
| **Ethics Contact** | [name@email.com] | Ethical concerns |
| **Support Team** | [support@email.com] | User support |

---

## References

### Internal Documentation
- [AIBOM](../aibom.md)
- [Prompt Standards](../prompt-standards.md)
- [Ethics Scorecard](../../01-governance/ethics-scorecard.md)

### External Resources
- [Research Paper](URL)
- [Dataset Documentation](URL)
- [Benchmark Results](URL)

### Related Models
- `MC-XXX-name.md` - Related Model 1 *(replace with actual link)*
- `MC-XXX-name-v1.md` - Previous Version *(replace with actual link)*

---

## Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| v1.0.0 | YYYY-MM-DD | [Name] | Initial model card |
| v1.1.0 | YYYY-MM-DD | [Name] | Updated performance metrics |
| v2.0.0 | YYYY-MM-DD | [Name] | Major model update |

---

**Model Card Created:** YYYY-MM-DD  
**Last Reviewed:** YYYY-MM-DD  
**Next Review:** YYYY-MM-DD  
**Document Owner:** [Name/Role]

---

[← Back to Model Cards](README.md) | [Volume III: Engineering →](../index.md)
