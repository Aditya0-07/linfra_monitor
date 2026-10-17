#!/usr/bin/env python3
"""
Linux Infrastructure Monitoring - CLI Dashboard
Author: Aditya
Description: Reads structured telemetry and displays a high-level summary view.
"""

import os
import sys
import json

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOG_FILE = os.path.join(BASE_DIR, "logs", "monitor_events.json")

def load_events(limit=5):
    """Loads the last N JSON log events."""
    if not os.path.exists(LOG_FILE):
        return []
    
    events = []
    with open(LOG_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return events[-limit:]

def render_dashboard():
    events = load_events(limit=5)
    if not events:
        print("No telemetry data found. Run `scripts/monitor.py` first.")
        return

    latest = events[-1]
    metrics = latest.get("metrics", {})
    services = latest.get("services", {})
    status = latest.get("status", "UNKNOWN")
    unresolved = latest.get("unresolved_incidents", [])

    print("==================================================")
    print("        INFRASTRUCTURE TELEMETRY DASHBOARD        ")
    print("==================================================")
    print(f" Last Updated: {metrics.get('timestamp', 'N/A')}")
    print(f" Overall Status: [{status}]")
    print("--------------------------------------------------")
    print(" [SYSTEM VITALS]")
    print(f"  • CPU Utilization:    {metrics.get('cpu_usage_pct', 0.0)}%")
    print(f"  • Memory Utilization: {metrics.get('memory_usage_pct', 0.0)}%")
    print(f"  • Root Disk Space:    {metrics.get('disk_usage_pct', 0.0)}%")
    print("--------------------------------------------------")
    print(" [SERVICE REGISTRY]")
    for svc, state in services.items():
        marker = "🟢" if state in ["active", "recovered"] else "🔴"
        print(f"  {marker} {svc:<22}: {state.upper()}")
    print("--------------------------------------------------")
    print(" [RECENT EVENT HISTORY (Last 5 Runs)]")
    for idx, ev in enumerate(events, 1):
        ts = ev.get("metrics", {}).get("timestamp", "N/A")
        st = ev.get("status", "UNKNOWN")
        rec_count = len(ev.get("recoveries", []))
        print(f"  #{idx} | {ts} | Status: {st:<9} | Recoveries: {rec_count}")

    if unresolved:
        print("--------------------------------------------------")
        print(" ⚠️  ACTIVE UNRESOLVED INCIDENTS:")
        for inc in unresolved:
            print(f"  - {inc}")
    print("==================================================")

if __name__ == "__main__":
    render_dashboard()