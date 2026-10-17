#!/usr/bin/env python3
"""
Linux Infrastructure Monitoring & Self-Healing Engine
Author: Aditya
Description: Gathers system vitals, detects service failures, and attempts
             automated remediation (restarts) before logging structured events.
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime
import psutil

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOG_FILE = os.path.join(BASE_DIR, "logs", "monitor_events.json")
MOCK_APP = os.path.join(BASE_DIR, "tests", "mock_app.sh")

# Safety Thresholds
DISK_THRESHOLD = 80.0
MEM_THRESHOLD = 85.0

def get_system_metrics():
    """Collects CPU, memory, and disk usage."""
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cpu_usage_pct": psutil.cpu_percent(interval=1),
        "memory_usage_pct": psutil.virtual_memory().percent,
        "disk_usage_pct": psutil.disk_usage("/").percent,
    }

def check_service(name, check_cmd):
    """Executes a status command and returns True if healthy."""
    res = subprocess.run(check_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return res.returncode == 0

def restart_service(restart_cmd):
    """Attempts to restart a failed service."""
    res = subprocess.run(restart_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return res.returncode == 0

def log_event(data):
    """Appends structured JSON logs."""
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(data) + "\n")

def main():
    metrics = get_system_metrics()
    incidents = []
    recovery_events = []

    # Monitored services configuration: name -> (status_check_cmd, restart_cmd)
    services_config = {
        "systemd-timesyncd": (["systemctl", "is-active", "--quiet", "systemd-timesyncd"], None),
        "cron": (["systemctl", "is-active", "--quiet", "cron"], None),
        "mock_app": ([MOCK_APP, "status"], [MOCK_APP, "start"])
    }

    print("==========================================")
    print(f" SELF-HEALING MONITOR - {metrics['timestamp']}")
    print("==========================================")
    print(f"CPU Utilization:    {metrics['cpu_usage_pct']}%")
    print(f"Memory Utilization: {metrics['memory_usage_pct']}%")
    print(f"Root Disk Space:    {metrics['disk_usage_pct']}%")
    print("------------------------------------------")
    print("SERVICE CHECKS & RECOVERY:")

    service_states = {}

    for service, (check_cmd, restart_cmd) in services_config.items():
        is_up = check_service(service, check_cmd)

        if is_up:
            service_states[service] = "active"
            print(f"  [OK]       {service} is healthy.")
        else:
            print(f"  [CRITICAL] {service} is DOWN!")
            service_states[service] = "down"

            # Auto-healing trigger
            if restart_cmd:
                print(f"  [ACTION]   Attempting automatic restart for {service}...")
                restart_service(restart_cmd)
                time.sleep(1)  # Allow process initialization

                # Verification check post-restart
                if check_service(service, check_cmd):
                    print(f"  [RESOLVED] {service} successfully recovered!")
                    service_states[service] = "recovered"
                    recovery_events.append({"service": service, "action": "restart", "status": "success"})
                else:
                    print(f"  [FAILED]   {service} auto-recovery failed. Manual escalation required.")
                    incidents.append(f"Service {service} failed to recover.")
                    recovery_events.append({"service": service, "action": "restart", "status": "failed"})
            else:
                incidents.append(f"Service {service} is down (no auto-recovery configured).")

    if metrics["disk_usage_pct"] >= DISK_THRESHOLD:
        incidents.append(f"Disk space exceeded: {metrics['disk_usage_pct']}%")
    if metrics["memory_usage_pct"] >= MEM_THRESHOLD:
        incidents.append(f"Memory usage exceeded: {metrics['memory_usage_pct']}%")

    log_payload = {
        "metrics": metrics,
        "services": service_states,
        "recoveries": recovery_events,
        "status": "ALERT" if incidents else ("RECOVERED" if recovery_events else "HEALTHY"),
        "unresolved_incidents": incidents
    }
    log_event(log_payload)

    print("------------------------------------------")
    if incidents:
        print(f"Final State: UNRESOLVED INCIDENTS ({len(incidents)} issue(s))")
        sys.exit(1)
    elif recovery_events:
        print("Final State: ALL ISSUES AUTO-RESOLVED")
        sys.exit(0)
    else:
        print("Final State: HEALTHY")
        sys.exit(0)

if __name__ == "__main__":
    main()