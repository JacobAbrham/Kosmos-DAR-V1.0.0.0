# AWS Deployment

**KOSMOS Infrastructure on Amazon Web Services**

---

## Overview

This guide covers deploying and managing KOSMOS infrastructure on AWS, leveraging managed services for scalability, reliability, and compliance.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        AWS Cloud                            │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │    ALB      │───▶│    EKS      │───▶│  SageMaker  │     │
│  │ (Load Bal.) │    │ (Kubernetes)│    │ (AI/ML)     │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                  │                  │             │
│         ▼                  ▼                  ▼             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │    WAF      │    │     S3      │    │   Bedrock   │     │
│  │ (Security)  │    │  (Storage)  │    │ (Foundation)│     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

- AWS account with administrator access
- AWS CLI v2 installed and configured
- Terraform >= 1.5.0 with AWS provider
- kubectl for EKS management

### CLI Setup

```bash
# Configure AWS CLI
aws configure
# AWS Access Key ID: [your-access-key]
# AWS Secret Access Key: [your-secret-key]
# Default region name: us-east-1
# Default output format: json

# Verify configuration
aws sts get-caller-identity
```

---

## Core Services

### Compute: EKS

**Elastic Kubernetes Service** cluster setup:

```hcl
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name    = "kosmos-prod"
  cluster_version = "1.28"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  eks_managed_node_groups = {
    api = {
      instance_types = ["m6i.2xlarge"]
      min_size       = 3
      max_size       = 10
      desired_size   = 3

      labels = {
        workload = "api"
      }
    }

    inference = {
      instance_types = ["g5.2xlarge"]
      min_size       = 2
      max_size       = 8
      desired_size   = 2
      ami_type       = "AL2_x86_64_GPU"

      labels = {
        workload = "inference"
      }

      taints = [{
        key    = "nvidia.com/gpu"
        value  = "true"
        effect = "NO_SCHEDULE"
      }]
    }
  }
}
```

### AI/ML: SageMaker

**SageMaker endpoint** for model serving:

```hcl
resource "aws_sagemaker_model" "kosmos_summarizer" {
  name               = "kosmos-summarizer-v2"
  execution_role_arn = aws_iam_role.sagemaker.arn

  primary_container {
    image          = "${aws_ecr_repository.kosmos.repository_url}:latest"
    model_data_url = "s3://kosmos-models/MC-001/v2.1.0/model.tar.gz"
  }
}

resource "aws_sagemaker_endpoint_configuration" "kosmos" {
  name = "kosmos-summarizer-config"

  production_variants {
    variant_name           = "primary"
    model_name             = aws_sagemaker_model.kosmos_summarizer.name
    initial_instance_count = 2
    instance_type          = "ml.g5.2xlarge"
  }
}

resource "aws_sagemaker_endpoint" "kosmos" {
  name                 = "kosmos-summarizer"
  endpoint_config_name = aws_sagemaker_endpoint_configuration.kosmos.name
}
```

### Storage: S3

```hcl
resource "aws_s3_bucket" "kosmos_data" {
  bucket = "kosmos-production-data"
}

resource "aws_s3_bucket_versioning" "kosmos_data" {
  bucket = aws_s3_bucket.kosmos_data.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "kosmos_data" {
  bucket = aws_s3_bucket.kosmos_data.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.kosmos.arn
      sse_algorithm     = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "kosmos_data" {
  bucket = aws_s3_bucket.kosmos_data.id

  rule {
    id     = "logs-lifecycle"
    status = "Enabled"

    filter {
      prefix = "logs/"
    }

    transition {
      days          = 30
      storage_class = "INTELLIGENT_TIERING"
    }

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
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "kosmos-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway   = true
  single_nat_gateway   = false
  enable_dns_hostnames = true

  tags = {
    "kubernetes.io/cluster/kosmos-prod" = "shared"
  }
}
```

### Application Load Balancer

```hcl
resource "aws_lb" "kosmos" {
  name               = "kosmos-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = module.vpc.public_subnets

  enable_deletion_protection = true
}

resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.kosmos.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = aws_acm_certificate.kosmos.arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.kosmos.arn
  }
}
```

---

## Security

### IAM Policies

```hcl
resource "aws_iam_policy" "kosmos_api" {
  name = "kosmos-api-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Resource = "${aws_s3_bucket.kosmos_data.arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "sagemaker:InvokeEndpoint"
        ]
        Resource = aws_sagemaker_endpoint.kosmos.arn
      },
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel"
        ]
        Resource = "*"
      }
    ]
  })
}
```

### Security Groups

```hcl
resource "aws_security_group" "api" {
  name        = "kosmos-api-sg"
  description = "Security group for KOSMOS API"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

### WAF Rules

```hcl
resource "aws_wafv2_web_acl" "kosmos" {
  name  = "kosmos-waf"
  scope = "REGIONAL"

  default_action {
    allow {}
  }

  rule {
    name     = "rate-limit"
    priority = 1

    override_action {
      none {}
    }

    statement {
      rate_based_statement {
        limit              = 2000
        aggregate_key_type = "IP"
      }
    }

    visibility_config {
      sampled_requests_enabled   = true
      cloudwatch_metrics_enabled = true
      metric_name                = "RateLimitRule"
    }
  }

  rule {
    name     = "aws-managed-rules"
    priority = 2

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        vendor_name = "AWS"
        name        = "AWSManagedRulesCommonRuleSet"
      }
    }

    visibility_config {
      sampled_requests_enabled   = true
      cloudwatch_metrics_enabled = true
      metric_name                = "AWSManagedRules"
    }
  }

  visibility_config {
    sampled_requests_enabled   = true
    cloudwatch_metrics_enabled = true
    metric_name                = "KosmosWAF"
  }
}
```

---

## Monitoring

### CloudWatch

```hcl
resource "aws_cloudwatch_metric_alarm" "api_errors" {
  alarm_name          = "kosmos-api-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "5XXError"
  namespace           = "AWS/ApplicationELB"
  period              = 300
  statistic           = "Sum"
  threshold           = 10
  alarm_description   = "API error rate exceeded"

  dimensions = {
    LoadBalancer = aws_lb.kosmos.arn_suffix
  }

  alarm_actions = [aws_sns_topic.alerts.arn]
}

resource "aws_cloudwatch_dashboard" "kosmos" {
  dashboard_name = "KOSMOS-Operations"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/ApplicationELB", "RequestCount", "LoadBalancer", aws_lb.kosmos.arn_suffix]
          ]
          title = "Request Count"
        }
      }
    ]
  })
}
```

---

## Cost Optimization

### Savings Plans

```bash
# Purchase compute savings plan
aws savingsplans create-savings-plan \
  --savings-plan-offering-id offering-id \
  --commitment 100 \
  --savings-plan-type ComputeSavingsPlans
```

### Spot Instances

```hcl
resource "aws_eks_node_group" "spot" {
  cluster_name    = module.eks.cluster_name
  node_group_name = "kosmos-spot"
  node_role_arn   = aws_iam_role.node.arn
  subnet_ids      = module.vpc.private_subnets
  capacity_type   = "SPOT"

  instance_types = ["m6i.2xlarge", "m5.2xlarge", "m5a.2xlarge"]

  scaling_config {
    desired_size = 2
    max_size     = 10
    min_size     = 0
  }
}
```

---

## Regions

| Region | Code | Use Case |
|--------|------|----------|
| N. Virginia | us-east-1 | Primary |
| Oregon | us-west-2 | DR |
| Frankfurt | eu-central-1 | EU data residency |
| Singapore | ap-southeast-1 | APAC |

---

## Related Documentation

- [Alibaba Cloud Deployment](alibaba-cloud.md) - Alibaba infrastructure guide
- [GCP Deployment](gcp.md) - GCP infrastructure guide
- [FinOps Metrics](../finops-metrics.md) - Cost management

---

**Last Updated:** 2025-12-12
**Infrastructure Version:** 1.0.0
**Terraform Provider:** aws ~> 5.0
