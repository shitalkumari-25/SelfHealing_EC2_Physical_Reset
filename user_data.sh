#!/bin/bash
dnf update -y
dnf install -y python3-pip
pip3 install flask boto3 requests
systemctl daemon-reload
systemctl enable business-portal
systemctl start business-portal