#!/bin/bash
set -e

VPC_ID=$(aws ec2 describe-vpcs --filters "Name=is-default,Values=true" --query "Vpcs[0].VpcId" --output text)
SG_ID=$(aws ec2 describe-security-groups --group-names self-healing-business-sg --query "SecurityGroups[0].GroupId" --output text 2>/dev/null || aws ec2 create-security-group --group-name self-healing-business-sg --description "Allow HTTP Port 80" --vpc-id "$VPC_ID" --query "GroupId" --output text)
aws ec2 authorize-security-group-ingress --group-id "$SG_ID" --protocol tcp --port 80 --cidr 0.0.0.0/0 2>/dev/null || true

cat << 'SCRIPT' > /tmp/bootstrap_portal.sh
#!/bin/bash
mkdir -p /opt/self_healing_portal
SCRIPT

cat << 'EOF_WRAP' >> /tmp/bootstrap_portal.sh
cat << 'WORKER' > /opt/self_healing_portal/order_engine.py
EOF_WRAP
cat order_engine.py >> /tmp/bootstrap_portal.sh
echo "WORKER" >> /tmp/bootstrap_portal.sh

cat << 'EOF_WRAP' >> /tmp/bootstrap_portal.sh
cat << 'WEB' > /opt/self_healing_portal/web_portal.py
EOF_WRAP
cat web_portal.py >> /tmp/bootstrap_portal.sh
echo "WEB" >> /tmp/bootstrap_portal.sh

cat << 'SERVICE' >> /tmp/bootstrap_portal.sh
cat << 'UNIT' > /etc/systemd/system/business-portal.service
[Unit]
Description=Self-Healing EC2 Physical Reset Software Portal
After=network.target
[Service]
ExecStart=/usr/bin/python3 /opt/self_healing_portal/web_portal.py
Restart=always
[Install]
WantedBy=multi-user.target
UNIT

systemctl daemon-reload
systemctl enable business-portal
systemctl restart business-portal
SERVICE

GZ_PAYLOAD=$(gzip -c /tmp/bootstrap_portal.sh | base64 -w 0)
WRAPPER=$(printf '#!/bin/bash\necho "%s" | base64 -d | gunzip > /tmp/run.sh && bash /tmp/run.sh\n' "$GZ_PAYLOAD")
ENCODED=$(echo "$WRAPPER" | base64 -w 0)

AMI_ID=$(aws ssm get-parameters --names /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 --query "Parameters[0].Value" --output text)
aws ec2 create-launch-template --launch-template-name self-healing-template --version-description "v3-business-edition" --launch-template-data "{\"ImageId\":\"$AMI_ID\",\"InstanceType\":\"t3.micro\",\"SecurityGroupIds\":[\"$SG_ID\"],\"IamInstanceProfile\":{\"Name\":\"LabInstanceProfile\"},\"UserData\":\"$ENCODED\"}" 2>/dev/null || aws ec2 create-launch-template-version --launch-template-name self-healing-template --version-description "v3-business-edition" --launch-template-data "{\"ImageId\":\"$AMI_ID\",\"InstanceType\":\"t3.micro\",\"SecurityGroupIds\":[\"$SG_ID\"],\"IamInstanceProfile\":{\"Name\":\"LabInstanceProfile\"},\"UserData\":\"$ENCODED\"}" > /dev/null

SUBNETS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query "Subnets[*].SubnetId" --output text | tr '\t' ',')
aws autoscaling create-auto-scaling-group --auto-scaling-group-name self-healing-asg --launch-template "LaunchTemplateName=self-healing-template,Version=\$Latest" --min-size 1 --max-size 2 --desired-capacity 1 --vpc-zone-identifier "$SUBNETS" 2>/dev/null || aws autoscaling update-auto-scaling-group --auto-scaling-group-name self-healing-asg --launch-template "LaunchTemplateName=self-healing-template,Version=\$Latest" --min-size 1 --max-size 2 --desired-capacity 1

OLD_ID=$(aws autoscaling describe-auto-scaling-groups --auto-scaling-group-names self-healing-asg --query "AutoScalingGroups[0].Instances[0].InstanceId" --output text)
if [ -n "$OLD_ID" ] && [ "$OLD_ID" != "None" ]; then
  aws ec2 terminate-instances --instance-ids "$OLD_ID" > /dev/null
fi
sleep 45
IP=$(aws ec2 describe-instances --filters "Name=tag:aws:autoscaling:groupName,Values=self-healing-asg" "Name=instance-state-name,Values=running" --query "Reservations[0].Instances[0].PublicIpAddress" --output text)
echo "Live Storefront URL: http://$IP"