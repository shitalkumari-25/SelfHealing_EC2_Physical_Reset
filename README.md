# AegisCloud: Enterprise Self-Healing EC2 & Business Continuity Portal

An autonomous, cloud-native self-healing compute infrastructure deployed on Amazon Web Services (AWS) featuring an interactive **Business Continuity & Chaos Engineering Control Portal**.

## 📌 Business & Architecture Highlights
- **Enterprise Business Portal (Python Flask + Boto3):** Real-time web dashboard tracking **99.99% SLA**, **Recovery Time Objective (RTO < 2s)**, and **$4,500/hr Downtime Loss Saved**.
- **Interactive Chaos Engineering Controls:**
  - **Simulate Hardware Crash (Terminate Node):** Web button invoking `ec2:TerminateInstances` via `LabInstanceProfile` IAM permissions to test live failover.
  - **Simulate Traffic Spike (CPU Load Test):** Injects a 5-second high-CPU burst to validate workload resilience.
  - **Refresh Node Telemetry:** Queries IMDSv2 session tokens for live Instance ID and Availability Zone placement.
- **Self-Healing Engine:** AWS Auto Scaling Group (`self-healing-asg`) spanning `us-east-1a` and `us-east-1b` (`Desired=1, Min=1, Max=1`).
- **Audit Telemetry:** Amazon EventBridge rule (`ec2-healing-event-rule`) streaming state changes (`shutting-down` -> `terminated` -> `running`) into CloudWatch Log Group (`/aws/events/self-healing-ec2`).

## 🚀 Repository Structure
- `app.py`: Python Flask backend API and dark-mode Business Continuity Dashboard UI.
- `user_data.sh`: Automated EC2 Launch Template bootstrap script (`v4`).
- `trigger_reset.sh`: CLI chaos failure injection utility.
- `README.md`: System architecture and business impact documentation.

---
*Developed by Shital Kumari (2503a520r2, Batch 67) for Course 25CAI102PC205 - Cloud Computing, SR University.*