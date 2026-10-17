#!/usr/bin/env bash
# A mock app that writes a PID file and runs in the background

PID_FILE="/tmp/mock_app.pid"

case "$1" in
    start)
        if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
            echo "mock_app is already running."
            exit 0
        fi
        echo "Starting mock_app..."
        python3 -m http.server 9999 --bind 127.0.0.1 > /dev/null 2>&1 &
        echo $! > "$PID_FILE"
        echo "mock_app started (PID: $(cat "$PID_FILE"))."
        ;;
    stop)
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            echo "Stopping mock_app (PID: ${PID})..."
            kill "$PID" 2>/dev/null || true
            rm -f "$PID_FILE"
            echo "mock_app stopped."
        else
            echo "mock_app is not running."
        fi
        ;;
    status)
        if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
            echo "active"
            exit 0
        else
            echo "inactive"
            exit 3
        fi
        ;;
    restart)
        "$0" stop
        sleep 1
        "$0" start
        ;;
    *)
        echo "Usage: $0 {start|stop|status|restart}"
        exit 1
        ;;
esac