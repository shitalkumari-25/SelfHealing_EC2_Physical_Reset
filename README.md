# Self-Healing EC2 Physical Reset (Cloud Software Edition)

A zero-downtime B2B business continuity and automated infrastructure recovery platform built on AWS EC2, Auto Scaling Groups, and Linux `systemd`.

## Overview
Replaces physical hardware reset buttons (ESP32/LED) with a pure cloud-native, two-layer self-healing architecture:
- **Storefront & Virtual Reset Console (`web_portal.py`, Port 80):** Decoupled B2B checkout portal with light/dark mode, revenue protection KPIs, live transaction ledger, and IMDSv2 EC2 metadata lookup.
- **Payment Settlement Microservice (`order_engine.py`, Port 8080):** Isolated backend worker settling customer transactions independently of the web tier.
- **Layer 1 Virtual Reset (~0.05s MTTR):** Detects `SIGKILL` process crashes, pauses checkouts safely without dropping the storefront, and spawns a fresh worker PID on click.
- **Layer 2 AWS Auto Scaling Failover (~45s):** Terminates unhealthy EC2 hosts via AWS CLI while `self-healing-asg` automatically provisions and bootstraps a replacement instance.

## Deployment
Upload `order_engine.py`, `web_portal.py`, and `deploy_all.sh` to AWS CloudShell (`us-east-1`) and run `bash deploy_all.sh`.