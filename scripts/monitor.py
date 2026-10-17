#!/usr/bin/env python3
"""
Linux Infrastructure Monitoring Engine
Author: Aditya
Description: Gathers system metrics and checks systemd services using Python,
             emitting structured JSON log entries.
"""

import os
import sys
import json
import subprocess
from datetime import datetime
import psutil

# Base directories
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOG_FILE = os.path.join(BASE_DIR, "logs", "monitor_events.json")

# Safety Thresholds
DISK_THRESHOLD = 80.0
MEM_THRESHOLD = 85.0

# Services to monitor
SERVICES_TO_CHECK = ["systemd-timesyncd", "cron", "fake-service"]

def get_system_metrics():
    """Collects CPU, virtual memory, and root filesystem metrics."""
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cpu_usage_pct": psutil.cpu_percent(interval=1),
        "memory_usage_pct": psutil.virtual_memory().percent,
        "disk_usage_pct": psutil.disk_usage("/").percent,
    }

def check_service_status(service_name):
    """Queries systemd using systemctl to inspect unit state."""
    result = subprocess.run(
        ["systemctl", "is-active", "--quiet", service_name],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return result.returncode == 0

def log_event(data):
    """Appends structured JSON logs to the incident log file."""
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(data) + "\n")

def main():
    metrics = get_system_metrics()
    incidents = []

    print("==========================================")
    print(f" PYTHON SYSTEM MONITOR - {metrics['timestamp']}")
    print("==========================================")
    print(f"CPU Utilization:    {metrics['cpu_usage_pct']}%")
    print(f"Memory Utilization: {metrics['memory_usage_pct']}%")
    print(f"Root Disk Space:    {metrics['disk_usage_pct']}%")
    print("------------------------------------------")
    print("SERVICE CHECKS:")

    service_results = {}
    for service in SERVICES_TO_CHECK:
        is_healthy = check_service_status(service)
        service_results[service] = "active" if is_healthy else "failed"
        
        if is_healthy:
            print(f"  [OK]     {service}")
        else:
            print(f"  [FAILED] {service}")
            incidents.append(f"Service '{service}' is down")

    if metrics["disk_usage_pct"] >= DISK_THRESHOLD:
        incidents.append(f"Disk space exceeded threshold: {metrics['disk_usage_pct']}%")

    if metrics["memory_usage_pct"] >= MEM_THRESHOLD:
        incidents.append(f"Memory usage exceeded threshold: {metrics['memory_usage_pct']}%")

    # Record structured event
    log_payload = {
        "metrics": metrics,
        "services": service_results,
        "status": "ALERT" if incidents else "HEALTHY",
        "incidents": incidents
    }
    log_event(log_payload)

    print("------------------------------------------")
    if incidents:
        print(f"Status: COMPROMISED ({len(incidents)} issue(s) detected)")
        sys.exit(1)
    else:
        print("Status: ALL SYSTEMS HEALTHY")
        sys.exit(0)

if __name__ == "__main__":
    main()