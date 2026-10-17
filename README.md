# Linux Infrastructure Monitoring & Self-Healing Engine (`linfra_monitor`)

A lightweight, production-grade Linux telemetry collector and self-healing engine built for Debian/Ubuntu systems. It monitors core host vitals, inspects `systemd` unit availability, executes automated self-recovery upon service failure, and ships structured JSON event streams for downstream observability platforms.

---

## Architecture Overview

[ Host Machine ]
                                   │
            ┌──────────────────────┴──────────────────────┐
            ▼                                             ▼
    [ System Metrics ]                            [ Service State ]

(CPU, RAM, Disk via psutil)                  (systemctl & background units)
│                                             │
│                                     [ Down Detected? ]
│                                             │
│                                    ┌────────┴────────┐
│                                   Yes               No
│                                    │                 │
│                             [ Auto-Restart ]         │
│                             (re-verify check)        │
│                                    │                 │
└──────────────────────┬─────────────┴─────────────────┘
▼
[ Structured JSON Event Stream ]
│
┌────────────────┴────────────────┐
▼                                 ▼
logs/monitor_events.json        CLI Telemetry Dashboard
(ELK / CloudWatch ingest)        (scripts/dashboard.py)


---

## Features

- **System Telemetry:** Real-time collection of CPU utilization, virtual memory consumption, and root filesystem usage via `psutil`.
- **Automated Remediation:** Detects service failures and executes configurable restart triggers with health re-verification.
- **Structured JSON Logging:** Emits machine-readable JSON logs for auditing and ingestion into tools like Datadog, ELK, or AWS CloudWatch.
- **Alert Dispatch Engine:** Outbound webhook dispatch for critical unresolved incidents (Slack/Discord/HTTP integration).
- **CLI Telemetry Dashboard:** Standalone terminal UI displaying vitals, service status markers, and event history trends.
- **Zero-Pollution Git Config:** Configured `.gitignore` preventing log and runtime artifact contamination.

---

## Directory Structure

linfra_monitor/
├── logs/                   # Ignored runtime logs & incident audits
├── scripts/
│   ├── health_check.sh     # Lightweight POSIX Bash host checker
│   ├── service_monitor.sh  # Systemd service audit script
│   ├── monitor.py          # Unified Python telemetry & self-healing engine
│   └── dashboard.py        # Interactive CLI telemetry dashboard
├── tests/
│   └── mock_app.sh         # Managed background test service for chaos testing
├── .gitignore
├── requirements.txt        # Pinned Python dependencies
└── README.md


---

## Quick Start

### 1. Prerequisites
- Ubuntu 24.04 LTS (or Debian-based distribution)
- Python 3.12+ with `python3-venv`

### 2. Installation
```bash
# Clone the repository
git clone [https://github.com/](https://github.com/)<your-username>/linfra_monitor.git
cd linfra_monitor

# Set up isolated virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

3. Running Telemetry & Self-Healing
Bash

# Execute monitoring and recovery loop
python3 scripts/monitor.py

# Launch the CLI dashboard
python3 scripts/dashboard.py

4. Simulating a Chaos Failure
Bash

# Start and immediately terminate the mock service
./tests/mock_app.sh start
./tests/mock_app.sh stop

# Trigger monitor: witness automated detection and recovery
python3 scripts/monitor.py

Telemetry Log Schema

Events in logs/monitor_events.json follow this JSON format:
JSON

{
  "metrics": {
    "timestamp": "2026-10-17 15:38:48",
    "cpu_usage_pct": 22.4,
    "memory_usage_pct": 46.0,
    "disk_usage_pct": 36.0
  },
  "services": {
    "systemd-timesyncd": "active",
    "cron": "active",
    "mock_app": "recovered"
  },
  "recoveries": [
    {
      "service": "mock_app",
      "action": "restart",
      "status": "success"
    }
  ],
  "status": "RECOVERED",
  "unresolved_incidents": []
}

License

MIT License. Created by Aditya.
