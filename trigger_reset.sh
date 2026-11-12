#!/bin/bash
INSTANCE_ID=$(aws autoscaling describe-auto-scaling-groups \
  --auto-scaling-group-names self-healing-asg \
  --query "AutoScalingGroups[0].Instances[0].InstanceId" \
  --output text)

echo "Triggering reset on instance: $INSTANCE_ID"
aws ec2 terminate-instances --instance-ids "$INSTANCE_ID"