# 🚀 Production Deployment Checklist
## Domain: `nuvanta-holding.com`
## Infrastructure: Alibaba Cloud (ACK, RDS, Redis) + Cloudflare (DNS/WAF)

### 1. Data Layer Connectivity (Alibaba Cloud)
- [ ] **PostgreSQL (RDS)**
    - Endpoint: `[PENDING INPUT]`
    - Port: `5432`
    - User: `[PENDING INPUT]`
    - Password: `[SECURE INPUT]`
- [ ] **Redis (Tair/Redis)**
    - Endpoint: `[PENDING INPUT]`
    - Port: `6379`
    - Password: `[SECURE INPUT]`

### 2. Application Configuration
- [ ] **Secrets Management**
    - Run the setup script: `python3 scripts/setup_secrets.py`
    - This generates `k8s/secrets.yaml` and `.env`.
    - Apply secrets: `kubectl apply -f k8s/secrets.yaml`
    - API Keys (OpenAI, Anthropic, Hugging Face) configured.

### 3. Networking & DNS (Cloudflare)
- [ ] **Ingress Controller**
    - Deploy Alibaba ALB Ingress Controller.
    - Obtain External IP/DNS of the Load Balancer.
- [ ] **DNS Records**
    - Create `A` or `CNAME` record for `nuvanta-holding.com` pointing to ALB.
    - Proxy Status: `Proxied` (Orange Cloud) for WAF protection.

### 4. Verification
- [ ] Frontend loads at `https://nuvanta-holding.com`
- [ ] API responds at `https://nuvanta-holding.com/api/health`
- [ ] WebSocket connection established for Chat.
