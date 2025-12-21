# 🚀 Kosmos Production Deployment Action Plan

**Target Environment:** Alibaba Cloud ECS (`i-eb3ce85peqozeocmrwtd`)  
**Region:** `me-east-1` (Dubai)  
**OS:** Ubuntu 24.04  
**Orchestration:** K3s (Single-Node Kubernetes)

---

## 📋 Phase 1: Instance Preparation (✅ Complete)
- [x] **SSH Access Verification** (Verified via Cloud Assistant)
- [x] **K3s Installation** (Installed & Ready)
- [x] **Tooling Setup** (Kubectl verified)

## 🐳 Phase 2: Image Management (✅ Complete - Manual Transfer)
- [x] **Build Images** (Built locally)
- [x] **Transfer to Instance** (Used OSS as intermediate storage)
- [x] **Import to K3s** (Imported via `k3s ctr`)

## 🏗️ Phase 3: Deployment (✅ Complete)
- [x] **Backend Deployment** (Deployed on port 8000, NodePort 30001)
- [x] **Frontend Deployment** (Deployed on port 3000, NodePort 30000)
- [x] **Security Group Config** (Opened ports 30000-30001)

## ☸️ Phase 4: Configuration & Persistence (✅ Complete)
- [x] **Database Setup**
    - [x] Current: PostgreSQL (In-Cluster).
    - [x] Target: PostgreSQL (In-Cluster or RDS).
- [x] **Environment Variables**
    - [x] Configure LLM Providers (OpenAI/Anthropic/HF).

## 🚀 Phase 5: Hybrid AI Integration (✅ Complete)
- [x] **LLM Provider Update**
    - [x] Update `src/integrations/llm/providers.py` to support Hugging Face Inference Endpoints.
    - [x] Configure `HUGGINGFACE_API_KEY` and `HUGGINGFACE_ENDPOINT_URL` in secrets.
- [x] **Model Routing Configuration**
    - [x] Configure Zeus (Pentarchy) to route complex tasks to OpenAI/Anthropic.
    - [x] Configure Hermes/Summarization tasks to route to Hugging Face Endpoints.

## 🖥️ Phase 6: Frontend Integration (✅ Complete - Local Verification)
- [x] **Configuration Update**
    - [x] Update `k8s/frontend.yaml` for local testing (optional) or verify `NEXT_PUBLIC_API_URL`.
- [x] **Functional Testing**
    - [x] Verify Chat Interface works with new DB persistence.
    - [x] Verify History/Sidebar loads conversations from DB.

## 🚀 Phase 7: Production Rollout (Alibaba Cloud)
- [x] **Artifact Transfer**
    - [x] Export `kosmos-backend:v1.0.0` and `kosmos-frontend:v1.0.0` and transfer to ECS.
    - [x] Transfer updated K8s manifests (`k8s/database.yaml`, `k8s/backend.yaml`, `k8s/secrets.yaml`).
- [x] **Cluster Update**
    - [x] Apply Secrets & Database manifests.
    - [x] Update Backend Deployment.
    - [x] Verify Production Connectivity.
- [x] **Domain & DNS (Cloudflare)**
    - [x] Configure `nuvanta-holding.com` A record -> `47.91.123.78`.
    - [x] Configure `www.nuvanta-holding.com` CNAME -> `nuvanta-holding.com`.
    - [x] (Optional) Configure Ingress for clean URLs (port 80/443).

## 🔍 Phase 8: Post-Deployment Verification (⚠️ Partial Success)
- [x] **Automated Inspection (Playwright)**
    - [x] Update test selectors for Production UI.
    - [x] Execute E2E Test Suite against `https://nuvanta-holding.com`.
    - [x] Generate Test Report (`TEST_REPORT.md`).
- [ ] **Issue Resolution**
    - [ ] Fix Voting System (Pentarchy UI not appearing).
    - [ ] Fix Agent Memory (Context loss).
    - [ ] Optimize Performance (Timeouts).

---

## 📝 Access Info
*   **Frontend:** `https://nuvanta-holding.com`
*   **Backend API:** `https://nuvanta-holding.com/api`
