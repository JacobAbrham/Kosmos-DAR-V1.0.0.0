# GCP Deployment

**KOSMOS Infrastructure on Google Cloud Platform**

---

## Overview

This guide covers deploying and managing KOSMOS infrastructure on Google Cloud Platform, leveraging Vertex AI and GKE for scalable AI workloads.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Google Cloud                             │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │ Cloud Load  │───▶│    GKE      │───▶│  Vertex AI  │     │
│  │  Balancing  │    │ (Kubernetes)│    │ (AI/ML)     │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                  │                  │             │
│         ▼                  ▼                  ▼             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │ Cloud Armor │    │    GCS      │    │  BigQuery   │     │
│  │ (Security)  │    │  (Storage)  │    │ (Analytics) │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

- GCP project with billing enabled
- gcloud CLI installed and configured
- Terraform >= 1.5.0 with Google provider
- kubectl for GKE management

### CLI Setup

```bash
# Initialize gcloud
gcloud init

# Set default project
gcloud config set project kosmos-prod

# Enable required APIs
gcloud services enable \
  container.googleapis.com \
  aiplatform.googleapis.com \
  compute.googleapis.com \
  storage.googleapis.com \
  cloudbuild.googleapis.com

# Configure application default credentials
gcloud auth application-default login
```

---

## Core Services

### Compute: GKE

**Google Kubernetes Engine** cluster setup:

```hcl
resource "google_container_cluster" "kosmos" {
  name     = "kosmos-prod"
  location = "us-central1"

  # Use separately managed node pools
  remove_default_node_pool = true
  initial_node_count       = 1

  network    = google_compute_network.kosmos.name
  subnetwork = google_compute_subnetwork.kosmos.name

  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  release_channel {
    channel = "REGULAR"
  }

  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = "172.16.0.0/28"
  }
}

resource "google_container_node_pool" "api" {
  name       = "api-pool"
  cluster    = google_container_cluster.kosmos.name
  location   = "us-central1"
  node_count = 3

  node_config {
    machine_type = "n2-standard-8"
    disk_size_gb = 100
    disk_type    = "pd-ssd"

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    labels = {
      workload = "api"
    }

    workload_metadata_config {
      mode = "GKE_METADATA"
    }
  }

  autoscaling {
    min_node_count = 3
    max_node_count = 10
  }
}

resource "google_container_node_pool" "gpu" {
  name     = "gpu-pool"
  cluster  = google_container_cluster.kosmos.name
  location = "us-central1"

  node_config {
    machine_type = "n1-standard-8"

    guest_accelerator {
      type  = "nvidia-tesla-t4"
      count = 1
      gpu_driver_installation_config {
        gpu_driver_version = "LATEST"
      }
    }

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    labels = {
      workload = "inference"
    }

    taint {
      key    = "nvidia.com/gpu"
      value  = "present"
      effect = "NO_SCHEDULE"
    }
  }

  autoscaling {
    min_node_count = 2
    max_node_count = 8
  }
}
```

### AI/ML: Vertex AI

**Vertex AI endpoint** for model serving:

```hcl
resource "google_vertex_ai_endpoint" "kosmos" {
  name         = "kosmos-summarizer"
  display_name = "KOSMOS Document Summarizer"
  location     = "us-central1"
}

# Deploy model using gcloud (Terraform support limited)
# gcloud ai endpoints deploy-model kosmos-summarizer \
#   --region=us-central1 \
#   --model=MC-001 \
#   --display-name=summarizer-v2 \
#   --machine-type=n1-standard-4 \
#   --accelerator=type=nvidia-tesla-t4,count=1 \
#   --min-replica-count=2 \
#   --max-replica-count=10
```

Python deployment script:

```python
from google.cloud import aiplatform

aiplatform.init(project="kosmos-prod", location="us-central1")

# Upload model
model = aiplatform.Model.upload(
    display_name="kosmos-summarizer-v2",
    artifact_uri="gs://kosmos-models/MC-001/v2.1.0/",
    serving_container_image_uri="us-docker.pkg.dev/vertex-ai/prediction/tf2-gpu.2-12:latest",
)

# Deploy to endpoint
endpoint = aiplatform.Endpoint.create(display_name="kosmos-summarizer")

endpoint.deploy(
    model=model,
    deployed_model_display_name="summarizer-v2",
    machine_type="n1-standard-4",
    accelerator_type="NVIDIA_TESLA_T4",
    accelerator_count=1,
    min_replica_count=2,
    max_replica_count=10,
)
```

### Storage: Cloud Storage

```hcl
resource "google_storage_bucket" "kosmos_data" {
  name          = "kosmos-production-data"
  location      = "US"
  storage_class = "STANDARD"

  versioning {
    enabled = true
  }

  encryption {
    default_kms_key_name = google_kms_crypto_key.kosmos.id
  }

  lifecycle_rule {
    condition {
      age        = 30
      with_state = "ANY"
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }

  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type = "Delete"
    }
  }

  uniform_bucket_level_access = true
}
```

---

## Networking

### VPC Setup

```hcl
resource "google_compute_network" "kosmos" {
  name                    = "kosmos-vpc"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "kosmos" {
  name          = "kosmos-subnet"
  ip_cidr_range = "10.0.0.0/20"
  region        = "us-central1"
  network       = google_compute_network.kosmos.id

  secondary_ip_range {
    range_name    = "pods"
    ip_cidr_range = "10.1.0.0/16"
  }

  secondary_ip_range {
    range_name    = "services"
    ip_cidr_range = "10.2.0.0/20"
  }

  private_ip_google_access = true
}

resource "google_compute_router" "kosmos" {
  name    = "kosmos-router"
  region  = "us-central1"
  network = google_compute_network.kosmos.id
}

resource "google_compute_router_nat" "kosmos" {
  name                               = "kosmos-nat"
  router                             = google_compute_router.kosmos.name
  region                             = "us-central1"
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
}
```

### Load Balancing

```hcl
resource "google_compute_global_address" "kosmos" {
  name = "kosmos-ip"
}

resource "google_compute_managed_ssl_certificate" "kosmos" {
  name = "kosmos-cert"

  managed {
    domains = ["api.kosmos.nuvanta.com"]
  }
}

resource "google_compute_url_map" "kosmos" {
  name            = "kosmos-lb"
  default_service = google_compute_backend_service.kosmos.id
}

resource "google_compute_target_https_proxy" "kosmos" {
  name             = "kosmos-https-proxy"
  url_map          = google_compute_url_map.kosmos.id
  ssl_certificates = [google_compute_managed_ssl_certificate.kosmos.id]
}

resource "google_compute_global_forwarding_rule" "kosmos" {
  name       = "kosmos-forwarding-rule"
  target     = google_compute_target_https_proxy.kosmos.id
  port_range = "443"
  ip_address = google_compute_global_address.kosmos.address
}
```

---

## Security

### IAM

```hcl
resource "google_service_account" "kosmos_api" {
  account_id   = "kosmos-api"
  display_name = "KOSMOS API Service Account"
}

resource "google_project_iam_member" "kosmos_api_storage" {
  project = var.project_id
  role    = "roles/storage.objectUser"
  member  = "serviceAccount:${google_service_account.kosmos_api.email}"
}

resource "google_project_iam_member" "kosmos_api_vertex" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.kosmos_api.email}"
}

# Workload Identity binding
resource "google_service_account_iam_member" "workload_identity" {
  service_account_id = google_service_account.kosmos_api.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.project_id}.svc.id.goog[kosmos/api]"
}
```

### Cloud Armor

```hcl
resource "google_compute_security_policy" "kosmos" {
  name = "kosmos-security-policy"

  rule {
    action   = "deny(403)"
    priority = "1000"
    match {
      expr {
        expression = "evaluatePreconfiguredExpr('xss-stable')"
      }
    }
    description = "Block XSS attacks"
  }

  rule {
    action   = "deny(403)"
    priority = "1001"
    match {
      expr {
        expression = "evaluatePreconfiguredExpr('sqli-stable')"
      }
    }
    description = "Block SQL injection"
  }

  rule {
    action   = "throttle"
    priority = "2000"
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
    rate_limit_options {
      conform_action = "allow"
      exceed_action  = "deny(429)"
      rate_limit_threshold {
        count        = 1000
        interval_sec = 60
      }
    }
    description = "Rate limiting"
  }

  rule {
    action   = "allow"
    priority = "2147483647"
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
    description = "Default allow"
  }
}
```

---

## Monitoring

### Cloud Monitoring

```hcl
resource "google_monitoring_alert_policy" "api_errors" {
  display_name = "KOSMOS API Error Rate"
  combiner     = "OR"

  conditions {
    display_name = "Error rate > 1%"
    condition_threshold {
      filter          = "resource.type=\"k8s_container\" AND metric.type=\"logging.googleapis.com/log_entry_count\" AND metric.labels.severity=\"ERROR\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 100

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.oncall.id]
}

resource "google_monitoring_dashboard" "kosmos" {
  dashboard_json = jsonencode({
    displayName = "KOSMOS Operations"
    gridLayout = {
      widgets = [
        {
          title = "Request Count"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "resource.type=\"k8s_container\""
                }
              }
            }]
          }
        }
      ]
    }
  })
}
```

---

## Cost Optimization

### Committed Use Discounts

```bash
# Purchase committed use discount
gcloud compute commitments create kosmos-commitment \
  --region=us-central1 \
  --resources=vcpu=100,memory=400GB \
  --plan=12-month
```

### Preemptible VMs

```hcl
resource "google_container_node_pool" "preemptible" {
  name     = "preemptible-pool"
  cluster  = google_container_cluster.kosmos.name
  location = "us-central1"

  node_config {
    preemptible  = true
    machine_type = "n2-standard-8"

    labels = {
      workload = "batch"
    }

    taint {
      key    = "preemptible"
      value  = "true"
      effect = "NO_SCHEDULE"
    }
  }

  autoscaling {
    min_node_count = 0
    max_node_count = 20
  }
}
```

---

## Regions

| Region | Code | Use Case |
|--------|------|----------|
| Iowa | us-central1 | Primary |
| Oregon | us-west1 | DR |
| Netherlands | europe-west4 | EU data residency |
| Singapore | asia-southeast1 | APAC |

---

## Related Documentation

- [AWS Deployment](aws) - AWS infrastructure guide
- [Alibaba Cloud Deployment](alibaba-cloud) - Alibaba infrastructure guide
- [FinOps Metrics](../finops-metrics) - Cost management

---

**Last Updated:** 2025-12-12
**Infrastructure Version:** 1.0.0
**Terraform Provider:** google ~> 5.0
