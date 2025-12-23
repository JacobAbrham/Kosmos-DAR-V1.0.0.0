#!/bin/bash
# Script to access and manage Alibaba Cloud ECS instance
# Usage: ./scripts/access_ecs.sh <command|ssh|info|console>

INSTANCE_ID="i-eb3ce85peqozeocmrwtd"
REGION_ID="me-east-1"
PUBLIC_IP="47.91.123.78"

case "$1" in
  ssh)
    echo "🔌 Connecting to ECS instance via SSH..."
    ssh root@$PUBLIC_IP
    ;;
  
  info)
    echo "📋 Getting instance information..."
    aliyun ecs DescribeInstances \
      --RegionId $REGION_ID \
      --InstanceIds "['$INSTANCE_ID']" \
      --output cols=InstanceId,InstanceName,Status,OSName,Memory,Cpu,PublicIpAddress.IpAddress
    ;;
  
  console)
    echo "🖥️ Getting VNC console URL..."
    aliyun ecs DescribeInstanceVncUrl \
      --RegionId $REGION_ID \
      --InstanceId $INSTANCE_ID
    ;;
  
  status)
    echo "📊 Checking instance status..."
    aliyun ecs DescribeInstanceStatus \
      --RegionId $REGION_ID \
      --InstanceIds "['$INSTANCE_ID']"
    ;;
  
  run)
    if [ -z "$2" ]; then
      echo "❌ Please provide a command to run"
      echo "Usage: $0 run '<command>'"
      exit 1
    fi
    echo "🚀 Running command on instance..."
    aliyun ecs RunCommand \
      --RegionId $REGION_ID \
      --InstanceId.1 $INSTANCE_ID \
      --Type RunShellScript \
      --CommandContent "$2" \
      --Timeout 60
    ;;
  
  monitor)
    echo "📈 Getting monitoring data..."
    aliyun cms DescribeMetricList \
      --Namespace acs_ecs_dashboard \
      --MetricName CPUUtilization \
      --Dimensions "{'instanceId':'$INSTANCE_ID'}"
    ;;
  
  list-disks)
    echo "💾 Listing attached disks..."
    aliyun ecs DescribeDisks \
      --RegionId $REGION_ID \
      --InstanceId $INSTANCE_ID \
      --output cols=DiskId,DiskName,Size,Device,Status
    ;;
  
  list-security)
    echo "🔒 Listing security groups..."
    aliyun ecs DescribeInstanceAttribute \
      --InstanceId $INSTANCE_ID \
      --output json | jq '.SecurityGroupIds.SecurityGroupId[]'
    ;;
  
  *)
    echo "🔧 Alibaba Cloud ECS Access Helper"
    echo "=================================="
    echo ""
    echo "Instance: $INSTANCE_ID"
    echo "Region:   $REGION_ID"
    echo "IP:       $PUBLIC_IP"
    echo ""
    echo "Usage: $0 <command>"
    echo ""
    echo "Commands:"
    echo "  ssh            - Connect via SSH"
    echo "  info           - Show instance details"
    echo "  console        - Get VNC console URL"
    echo "  status         - Check instance status"
    echo "  run '<cmd>'    - Execute command remotely"
    echo "  monitor        - View monitoring metrics"
    echo "  list-disks     - List attached disks"
    echo "  list-security  - List security groups"
    echo ""
    echo "Examples:"
    echo "  $0 ssh"
    echo "  $0 info"
    echo "  $0 run 'kubectl get pods -A'"
    ;;
esac
