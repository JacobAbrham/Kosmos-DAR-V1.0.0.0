# Ares Security Agent (DEPRECATED)

:::warning Deprecated Agent
    This agent has been deprecated in KOSMOS V1.0.0. Its responsibilities have been transferred to:
    
    - **AEGIS** - Guardian Security & Compliance Agent
    
    AEGIS provides enhanced security capabilities including runtime security (Falco), policy enforcement (Kyverno), and vulnerability scanning (Trivy).
    
    See [AEGIS Security Agent](../../02-architecture/agents/aegis-security) for the replacement.

---

**Domain:** Security, Access Control & Threat Response  
**Greek Deity:** Ares - God of War  
**Status:** ~~Active~~ **DEPRECATED**  
**Version:** 1.0.0  
**Deprecated In:** V1.0.0  
**Replaced By:** AEGIS

---

## Overview

Ares is the **security** agent, responsible for access control, threat detection, and security operations. Named after the god of war, Ares defends KOSMOS against threats and ensures security compliance.

### Key Capabilities

- **Access Control** - Manage permissions and roles
- **Threat Detection** - Identify security threats
- **Vulnerability Scanning** - Scan for vulnerabilities
- **Audit Logging** - Track security events
- **Incident Response** - Coordinate security incidents

### Supported Actions

| Action | Description | Required Params |
|--------|-------------|-----------------|
| `check_access` | Verify user permissions | `user_id`, `resource`, `action` |
| `scan_vulnerabilities` | Run security scan | `target`, `scan_type` |
| `get_audit_log` | Retrieve audit events | `filters`, `time_range` |
| `report_incident` | Create security incident | `incident_details` |
| `rotate_secrets` | Rotate credentials | `secret_name` |

### MCP Connections

| MCP Server | Purpose |
|------------|---------|
| security-scanner-mcp | Vulnerability scanning |

### Security Note

Ares requires human-in-the-loop approval for sensitive actions such as secret rotation and permission changes.

---

## Deprecation Rationale

Ares was renamed and enhanced to AEGIS in V1.0.0 to:

1. **Integrate runtime security** - Direct integration with Falco for real-time threat detection
2. **Policy enforcement** - Integration with Kyverno for Kubernetes-native policies
3. **Enhanced scanning** - Integration with Trivy for comprehensive vulnerability scanning
4. **Kill-switch implementation** - AEGIS implements the kill-switch protocol
5. **Compliance focus** - Multi-jurisdiction compliance (GDPR, CCPA, UAE PDPL)

The name change reflects the shift from "war" (reactive) to "protection" (proactive).

---

**Last Updated:** 2025-12-12  
**Archived:** 2025-12-13
