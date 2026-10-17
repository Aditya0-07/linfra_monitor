#!/usr/bin/env bash

# ========================================================
# Linux Infrastructure Health Check
# Author: Aditya
# Description: Collects core system metrics, checks thresholds,
#              writes persistent logs, and emits status exit codes.
# ========================================================

set -e

# Base directories
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_FILE="${PROJECT_DIR}/logs/system_health.log"

# Metric Collection
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
UPTIME=$(uptime -p)
LOAD_1MIN=$(awk '{print $1}' /proc/loadavg)
MEM_USAGE=$(free -m | awk '/Mem:/ {printf "%.1f", ($2-$7)/$2 * 100}')
DISK_USAGE=$(df / --output=pcent | tail -n 1 | tr -dc '0-9')

# Thresholds
DISK_THRESHOLD=80
MEM_THRESHOLD=85

STATUS_EXIT=0

# Console Report
echo "=========================================="
echo " SYSTEM HEALTH REPORT - ${TIMESTAMP}"
echo "=========================================="
echo "Uptime:        ${UPTIME}"
echo "1-Min Load:    ${LOAD_1MIN}"
echo "Memory Used:   ${MEM_USAGE}%"
echo "Root Disk:     ${DISK_USAGE}%"
echo "------------------------------------------"

# Disk Check
if [ "${DISK_USAGE}" -ge "${DISK_THRESHOLD}" ]; then
    echo "[ALERT] Root disk space is critically high: ${DISK_USAGE}% (Threshold: ${DISK_THRESHOLD}%)"
    echo "${TIMESTAMP} [ALERT] Disk usage: ${DISK_USAGE}%" >> "${LOG_FILE}"
    STATUS_EXIT=1
else
    echo "[OK] Root disk space is healthy."
fi

# Memory Check
MEM_ALERT=$(awk -v mem="${MEM_USAGE}" -v thresh="${MEM_THRESHOLD}" 'BEGIN {if (mem >= thresh) print "ALERT"; else print "OK"}')

if [ "${MEM_ALERT}" = "ALERT" ]; then
    echo "[ALERT] Memory usage is critically high: ${MEM_USAGE}% (Threshold: ${MEM_THRESHOLD}%)"
    echo "${TIMESTAMP} [ALERT] Memory usage: ${MEM_USAGE}%" >> "${LOG_FILE}"
    STATUS_EXIT=1
else
    echo "[OK] Memory usage is healthy."
fi

# Append an informational entry to the log file on every run
echo "${TIMESTAMP} [INFO] Metrics: load=${LOAD_1MIN}, mem=${MEM_USAGE}%, disk=${DISK_USAGE}%" >> "${LOG_FILE}"

echo "=========================================="

exit ${STATUS_EXIT}