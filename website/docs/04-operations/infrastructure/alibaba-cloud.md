# Alibaba Cloud Deployment

**KOSMOS Infrastructure on Alibaba Cloud**

---

## Overview

This guide covers deploying and managing KOSMOS infrastructure on Alibaba Cloud, optimized for Asia-Pacific regions with compliance requirements for data residency.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Alibaba Cloud                           │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   SLB       │───▶│    ECS      │───▶│   PAI-EAS   │     │
│  │ (Load Bal.) │    │ (Compute)   │    │ (AI Serving)│     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                  │                  │             │
│         ▼                  ▼                  ▼             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │    WAF      │    │    OSS      │    │  MaxCompute │     │
│  │ (Security)  │    │  (Storage)  │    │ (Analytics) │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

- Alibaba Cloud account with RAM administrator access
- Aliyun CLI installed and configured
- Terraform >= 1.5.0 with Alibaba provider

### CLI Setup

```bash
# Install Aliyun CLI
pip install aliyun-cli

# Configure credentials
aliyun configure
# Access Key ID: [your-access-key-id]
# Access Key Secret: [your-access-key-secret]
# Region ID: cn-shanghai
```

---

## Core Services

### Compute: ECS + ACK

**Elastic Compute Service (ECS)** for general workloads:

```hcl
resource "alicloud_instance" "kosmos_api" {
  instance_name        = "kosmos-api-server"
  instance_type        = "ecs.g7.2xlarge"
  image_id             = "ubuntu_22_04_x64_20G_alibase_20231221.vhd"
  security_groups      = [alicloud_security_group.kosmos.id]
  vswitch_id           = alicloud_vswitch.kosmos.id

  system_disk_category = "cloud_essd"
  system_disk_size     = 100

  tags = {
    Environment = "production"
    Service     = "kosmos-api"
  }
}
```

**Alibaba Container Service (ACK)** for Kubernetes:

```bash
# Create managed Kubernetes cluster
aliyun cs CreateCluster \
  --name kosmos-prod \
  --cluster-type ManagedKubernetes \
  --region-id cn-shanghai \
  --vpcid vpc-xxxxxxxx \
  --container-cidr 172.20.0.0/16 \
  --service-cidr 172.21.0.0/20
```

### AI Platform: PAI-EAS

**Platform for AI - Elastic Algorithm Service** for model serving:

```bash
# Deploy model to PAI-EAS
eascmd create kosmos-summarizer \
  --model oss://kosmos-models/MC-001/v2.1.0/ \
  --processor tensorflow_gpu \
  --instance-type ecs.gn6v-c8g1.2xlarge \
  --replicas 3
```

Configuration file (`pai-service.yaml`):

```yaml
name: kosmos-summarizer
processor: tensorflow_gpu
model_path: oss://kosmos-models/MC-001/v2.1.0/
metadata:
  instance: ecs.gn6v-c8g1.2xlarge
  rpc.keepalive: 50000
scaling:
  min: 2
  max: 10
  target_qps: 100
```

### Storage: OSS

**Object Storage Service** configuration:

```hcl
resource "alicloud_oss_bucket" "kosmos_data" {
  bucket = "kosmos-production-data"
  acl    = "private"

  versioning {
    status = "Enabled"
  }

  server_side_encryption_rule {
    sse_algorithm = "KMS"
  }

  lifecycle_rule {
    enabled = true
    prefix  = "logs/"
    expiration {
      days = 90
    }
  }
}
```

---

## Networking

### VPC Setup

```hcl
resource "alicloud_vpc" "kosmos" {
  vpc_name   = "kosmos-vpc"
  cidr_block = "10.0.0.0/16"
}

resource "alicloud_vswitch" "kosmos_app" {
  vswitch_name = "kosmos-app-subnet"
  vpc_id       = alicloud_vpc.kosmos.id
  cidr_block   = "10.0.1.0/24"
  zone_id      = "cn-shanghai-b"
}

resource "alicloud_vswitch" "kosmos_db" {
  vswitch_name = "kosmos-db-subnet"
  vpc_id       = alicloud_vpc.kosmos.id
  cidr_block   = "10.0.2.0/24"
  zone_id      = "cn-shanghai-c"
}
```

### Load Balancing (SLB)

```hcl
resource "alicloud_slb_load_balancer" "kosmos" {
  load_balancer_name   = "kosmos-lb"
  load_balancer_spec   = "slb.s3.medium"
  address_type         = "internet"
  internet_charge_type = "PayByTraffic"
}

resource "alicloud_slb_listener" "https" {
  load_balancer_id          = alicloud_slb_load_balancer.kosmos.id
  frontend_port             = 443
  backend_port              = 8080
  protocol                  = "https"
  bandwidth                 = -1
  server_certificate_id     = alicloud_slb_server_certificate.kosmos.id
  health_check              = "on"
  health_check_connect_port = 8080
}
```

---

## Security

### RAM Policies

```json
{
  "Version": "1",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecs:Describe*",
        "oss:GetObject",
        "oss:PutObject",
        "pai:InvokeService"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "acs:SourceVpc": "vpc-kosmos-prod"
        }
      }
    }
  ]
}
```

### Security Groups

```hcl
resource "alicloud_security_group" "kosmos_api" {
  name   = "kosmos-api-sg"
  vpc_id = alicloud_vpc.kosmos.id
}

resource "alicloud_security_group_rule" "allow_https" {
  security_group_id = alicloud_security_group.kosmos_api.id
  type              = "ingress"
  ip_protocol       = "tcp"
  port_range        = "443/443"
  cidr_ip           = "0.0.0.0/0"
}

resource "alicloud_security_group_rule" "allow_internal" {
  security_group_id = alicloud_security_group.kosmos_api.id
  type              = "ingress"
  ip_protocol       = "all"
  port_range        = "-1/-1"
  cidr_ip           = "10.0.0.0/16"
}
```

---

## Monitoring

### CloudMonitor Integration

```bash
# Install CloudMonitor agent
wget http://cms-agent-cn-shanghai.oss-cn-shanghai.aliyuncs.com/cms-go-agent/cms_go_agent.tar.gz
tar -xzf cms_go_agent.tar.gz
./cms_go_agent install

# Configure custom metrics
aliyun cms PutCustomMetric \
  --MetricList '[{
    "groupId": "12345",
    "metricName": "kosmos_requests_total",
    "dimensions": {"service": "summarizer"},
    "type": 0,
    "values": {"value": 1500}
  }]'
```

### Alerts

```hcl
resource "alicloud_cms_alarm" "high_cpu" {
  name    = "kosmos-high-cpu"
  project = "acs_ecs_dashboard"
  metric  = "CPUUtilization"

  dimensions = {
    instanceId = alicloud_instance.kosmos_api.id
  }

  escalations_critical {
    statistics          = "Average"
    comparison_operator = ">="
    threshold           = "90"
    times               = 3
  }

  contact_groups = ["kosmos-oncall"]
}
```

---

## Cost Optimization

### Reserved Instances

```bash
# Purchase reserved instance for predictable workloads
aliyun ecs PurchaseReservedInstancesOffering \
  --RegionId cn-shanghai \
  --InstanceType ecs.g7.2xlarge \
  --InstanceAmount 3 \
  --Period 1 \
  --PeriodUnit Year \
  --OfferingType "All Upfront"
```

### Spot Instances for Batch

```hcl
resource "alicloud_instance" "kosmos_batch" {
  instance_name = "kosmos-batch-worker"
  instance_type = "ecs.g7.4xlarge"
  spot_strategy = "SpotWithPriceLimit"
  spot_price_limit = "0.5"

  user_data = base64encode(file("batch-worker-init.sh"))
}
```

---

## Regions

| Region | Code | Use Case |
|--------|------|----------|
| Shanghai | cn-shanghai | Primary (China) |
| Hangzhou | cn-hangzhou | DR (China) |
| Singapore | ap-southeast-1 | APAC |
| Hong Kong | cn-hongkong | Cross-border |

---

## Related Documentation

- [AWS Deployment](aws) - AWS infrastructure guide
- [GCP Deployment](gcp) - GCP infrastructure guide
- [FinOps Metrics](../finops-metrics) - Cost management

---

**Last Updated:** 2025-12-12
**Infrastructure Version:** 1.0.0
**Terraform Provider:** alicloud ~> 1.200.0
