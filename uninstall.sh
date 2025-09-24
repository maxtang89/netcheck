#!/bin/bash

# Ensure the script is run as root
if [[ $EUID -ne 0 ]]; then
   echo "Please run this script as root (sudo ./uninstall.sh)"
   exit 1
fi

SERVICE_FILE="/etc/systemd/system/netcheck.service"
VENV_DIR="./venv"

echo "Stopping NetCheck service if running..."
systemctl stop netcheck 2>/dev/null

echo "Disabling NetCheck service..."
systemctl disable netcheck 2>/dev/null

if [ -f "$SERVICE_FILE" ]; then
    echo "Removing systemd service file..."
    rm -f "$SERVICE_FILE"
fi

echo "Reloading systemd..."
systemctl daemon-reload

if [ -d "$VENV_DIR" ]; then
    echo "Removing Python virtual environment..."
    rm -rf "$VENV_DIR"
fi

echo "Uninstallation complete!"
