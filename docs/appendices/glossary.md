# Glossary

**Key Terms and Definitions for KOSMOS**

---

## A

**ADR (Architectural Decision Record)** - Document capturing an architectural decision, its context, rationale, and consequences. KOSMOS uses ADRs to track major technical decisions.

**Agent** - An autonomous AI component within KOSMOS that performs specific tasks. KOSMOS has 11 specialized agents orchestrated by Zeus.

**AIBOM (AI Bill of Materials)** - Comprehensive inventory of all components, dependencies, models, and data sources used in an AI system. Required for transparency and compliance.

**AlertManager** - Prometheus ecosystem component that handles alert routing, deduplication, grouping, and notification to receivers (Slack, PagerDuty, email).

**Amnesia Protocol** - KOSMOS procedure for complete data deletion per GDPR Article 17 (Right to Erasure). Includes removing user data from all systems including backups.

**Apollo** - KOSMOS monitoring agent responsible for system health tracking, resource utilization, and operational metrics collection.

**Ares** - KOSMOS security agent handling threat detection, access control enforcement, and security incident response.

**Athena** - KOSMOS knowledge agent managing RAG (Retrieval-Augmented Generation), document search, and knowledge base operations.

---

## B

**BaseAgent** - Abstract base class that all KOSMOS agents inherit from, providing common functionality like state management, tool registration, and metrics.

**Burn Rate** - Rate at which error budget is being consumed. A burn rate of 1.0 means you'll exhaust your error budget exactly at the end of the period.

---

## C

**Canary Deployment** - Progressive rollout strategy that tests new versions with a small percentage of traffic before full deployment. KOSMOS uses Argo Rollouts for canary releases.

**Chronos** - KOSMOS scheduling agent responsible for calendar management, meeting coordination, and time-based task orchestration.

**Concept Drift** - Change in the relationship between model inputs and outputs over time, requiring model retraining or adjustment.

**Context Window** - Maximum number of tokens an LLM can process in a single request. Critical for RAG chunk sizing and conversation history management.

---

## D

**Data Drift** - Statistical change in the distribution of input data compared to training data, which may degrade model performance.

**Demeter** - KOSMOS data agent handling data pipelines, ETL operations, data quality monitoring, and data governance.

**Differential Privacy** - Mathematical framework for quantifying privacy guarantees when releasing statistical information. KOSMOS uses epsilon=1.0 for training data anonymization.

**Dionysus** - KOSMOS creative agent specializing in content generation, writing assistance, and creative tasks.

**DPIA (Data Protection Impact Assessment)** - Analysis of data processing risks required by GDPR Article 35 for high-risk processing activities.

**Dragonfly** - Redis-compatible in-memory data store used by KOSMOS for caching, session management, and rate limiting. More memory-efficient than Redis.

---

## E

**Embedding** - Dense vector representation of text, images, or other data. KOSMOS uses 384-dimensional embeddings for semantic search.

**Error Budget** - Allowed amount of downtime or errors before violating an SLO. Calculated as 1 - SLO target.

**EU AI Act** - European Union regulation establishing requirements for AI systems based on risk levels. KOSMOS is designed for compliance with high-risk system requirements.

---

## F

### Fairness Metrics {#fairness-metrics}

Quantitative measures assessing whether an AI model treats different demographic groups equitably. Common metrics include demographic parity, equalized odds, and calibration across groups.

**FinOps** - Practice of bringing financial accountability to cloud spending and AI costs. KOSMOS tracks per-request costs and token usage.

---

## G

**Grafana** - Open-source visualization platform used by KOSMOS for dashboards, alerting, and metric exploration.

**gRPC** - High-performance RPC framework used for inter-service communication within KOSMOS.

---

## H

**Hephaestus** - KOSMOS tooling agent responsible for MCP server management, tool execution, and external system integration.

**Hermes** - KOSMOS communications agent handling email, notifications, Slack, and other messaging channels.

**HuggingFace Inference Endpoints** - Managed service for deploying ML models. KOSMOS uses this for Mistral-7B-Instruct deployment.

---

## I

**Infisical** - Open-source secrets management platform used by KOSMOS for storing API keys, credentials, and sensitive configuration.

**Iris** - KOSMOS interface agent managing user interactions, response formatting, and UI/UX concerns.

**ISO 42001** - International standard for AI Management Systems, providing a framework for responsible AI development and deployment.

**IVFFlat** - Inverted File with Flat quantization, a vector index type used by pgvector for approximate nearest neighbor search.

---

## J

**Jaeger** - Distributed tracing platform used by KOSMOS for end-to-end request tracing and latency analysis.

---

## K

**K-Anonymity** - Privacy model ensuring each record is indistinguishable from at least k-1 other records. KOSMOS uses k=5 for anonymization.

**K3s** - Lightweight Kubernetes distribution used for KOSMOS staging and production deployments on Alibaba Cloud.

**KOSMOS** - Knowledge-Oriented System for Multi-agent Orchestrated Solutions. The AI-native enterprise operating system being developed.

---

## L

**LangGraph** - Framework for building stateful, multi-actor applications with LLMs. KOSMOS uses LangGraph for agent orchestration and workflow management.

**Langfuse** - Open-source LLM observability platform used by KOSMOS for prompt tracing, evaluation, and cost tracking.

**LLM (Large Language Model)** - AI model trained on large text corpora for natural language understanding and generation. KOSMOS supports multiple LLM providers.

**Loki** - Log aggregation system from Grafana Labs used by KOSMOS for centralized logging with LogQL query language.

---

## M

**MCP (Model Context Protocol)** - Open protocol for connecting AI systems to external data sources and tools. KOSMOS uses MCP for all external integrations.

**Model Card** - Standardized documentation for AI models including intended use, performance metrics, limitations, and ethical considerations.

**MTTR (Mean Time To Recovery)** - Average time to restore service after an incident. KOSMOS targets 15-minute MTTR for P1 incidents.

**Multi-tenancy** - Architecture pattern allowing single application instance to serve multiple isolated tenants. KOSMOS implements tenant isolation at database and API levels.

---

## N

**NATS** - High-performance messaging system used by KOSMOS for event-driven communication and pub/sub patterns.

---

## O

**OpenLineage** - Open standard for data lineage collection. KOSMOS emits lineage events for all data transformations.

**OpenTelemetry** - Observability framework providing APIs, libraries, and agents for telemetry data collection. KOSMOS uses OTLP for traces.

**OTLP (OpenTelemetry Protocol)** - Wire protocol for telemetry data. KOSMOS exports traces via OTLP to Jaeger.

---

## P

**P99 Latency** - 99th percentile response time, meaning 99% of requests complete faster than this value.

**pgvector** - PostgreSQL extension for vector similarity search. KOSMOS uses pgvector for RAG document retrieval.

**PII (Personally Identifiable Information)** - Data that can identify an individual. KOSMOS implements PII detection and redaction in logging and storage.

**Prometheus** - KOSMOS agent responsible for metrics collection, recording rules, and alerting. Also the name of the metrics system it uses.

**Prompt Injection** - Attack where malicious input manipulates AI model behavior. KOSMOS implements input sanitization and output filtering to mitigate.

**PromQL** - Prometheus Query Language used for metrics queries and alert rules.

**PSI (Population Stability Index)** - Metric for measuring distribution changes between datasets. Values >0.25 indicate significant drift.

---

## R

**RACI Matrix** - Responsibility assignment chart defining who is Responsible, Accountable, Consulted, and Informed for each task.

**RAG (Retrieval-Augmented Generation)** - Pattern combining document retrieval with LLM generation. KOSMOS uses RAG for knowledge-grounded responses.

**Recording Rule** - Prometheus rule that pre-computes frequently needed queries. KOSMOS uses recording rules for SLO calculations.

**Red Herring** - Deliberate anomaly injected into AI outputs to test human vigilance and attention. Part of KOSMOS oversight mechanisms.

**RTO (Recovery Time Objective)** - Maximum acceptable time to restore service after a disaster. KOSMOS has 4-hour RTO for critical systems.

**RPO (Recovery Point Objective)** - Maximum acceptable data loss measured in time. KOSMOS has 1-hour RPO for transactional data.

---

## S

**Semantic Cache** - Cache that stores LLM responses indexed by query embedding similarity, enabling reuse of similar queries.

**SLA (Service Level Agreement)** - Contractual commitment to service quality with financial penalties for violations.

**SLI (Service Level Indicator)** - Quantitative measure of service level, such as error rate or latency percentile.

**SLO (Service Level Objective)** - Target level of service quality expressed as a range of acceptable SLI values.

**SOC 2** - Service Organization Control 2, audit framework for service providers covering security, availability, and confidentiality.

**Span** - Single unit of work in a distributed trace, representing an operation with start time, duration, and metadata.

**State** - In LangGraph, the shared data structure that agents read from and write to during execution.

**structlog** - Python logging library used by KOSMOS for structured JSON logging.

---

## T

**Tenant** - Isolated customer organization within multi-tenant KOSMOS deployment. Each tenant has separate data and configuration.

**TOGAF** - The Open Group Architecture Framework, enterprise architecture methodology used for KOSMOS architecture governance.

**Token** - Basic unit of text for LLMs. One token ≈ 4 characters in English. KOSMOS tracks token usage for cost allocation.

**Trace** - Complete path of a request through distributed systems, composed of multiple spans.

---

## V

**Vector Database** - Database optimized for storing and querying high-dimensional vectors. KOSMOS uses PostgreSQL with pgvector.

---

## W

**W3C Trace Context** - Standard for propagating trace identifiers across services. KOSMOS uses traceparent and tracestate headers.

**Watermarking** - Embedding identifiable information in AI-generated content for attribution and detection. KOSMOS implements watermarking per EU AI Act requirements.

---

## Z

**Zeus** - Primary orchestrator agent in KOSMOS responsible for request routing, agent coordination, and workflow execution.

---

**Last Updated:** 2025-12-13

[← Back to Home](../index.md)
