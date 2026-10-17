#!/usr/bin/env bash

# ========================================================
# Linux Service Health Monitor
# Author: Aditya
# Description: Checks the active status of critical services
#              and logs incidents when a service is down.
# ========================================================

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_FILE="${PROJECT_DIR}/logs/service_monitor.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# List of services to monitor
SERVICES=("systemd-timesyncd" "cron" "fake-service")

echo "=========================================="
echo " SERVICE HEALTH CHECK - ${TIMESTAMP}"
echo "=========================================="

FAILED_COUNT=0

for SERVICE in "${SERVICES[@]}"; do
    if systemctl is-active --quiet "${SERVICE}"; then
        echo "[OK]        ${SERVICE} is running."
    else
        echo "[FAILED]    ${SERVICE} is down or not found!"
        echo "${TIMESTAMP} [CRITICAL] Service '${SERVICE}' is down." >> "${LOG_FILE}"
        FAILED_COUNT=$((FAILED_COUNT + 1))
    fi
done

echo "------------------------------------------"
if [ "${FAILED_COUNT}" -eq 0 ]; then
    echo "Overall status: ALL SERVICES HEALTHY"
    exit 0
else
    echo "Overall status: ${FAILED_COUNT} SERVICE(S) FAILED"
    exit 1
fi