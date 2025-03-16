#!/bin/bash

# Ensure the script is run as root (Uvicorn binding to port 80 requires root)
if [[ $EUID -ne 0 ]]; then
   echo "Please run this script as root (sudo ./install_run.sh)"
   exit 1
fi

# Load configurations from YAML without Python
CONFIG_PATH="./config.yaml"
if [ ! -f "$CONFIG_PATH" ]; then
    echo "Error: Configuration file config.yaml not found!"
    exit 1
fi

VENV_DIR="./venv"
PORT=$(grep '^port:' $CONFIG_PATH | awk '{print $2}')
EXEC_USER=$USER  # Automatically detect the current user

# Set up Python virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies from requirements.txt
REQ_FILE="./requirements.txt"
if [ ! -f "$REQ_FILE" ]; then
    echo "Error: requirements.txt not found!"
    exit 1
fi

echo "Installing required Python packages from requirements.txt..."
pip install -r "$REQ_FILE"

echo "Installation complete!"

# Create systemd service file
SERVICE_FILE="/etc/systemd/system/netcheck.service"

echo "Creating systemd service file at $SERVICE_FILE..."
cat <<EOF > $SERVICE_FILE
[Unit]
Description=netcheck service
After=network.target

[Service]
ExecStart=$(realpath $VENV_DIR)/bin/uvicorn netcheck:app --host 0.0.0.0 --port $PORT
WorkingDirectory=$(realpath .)
Restart=always
RestartSec=0
User=$EXEC_USER

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd, enable and start the service
echo "Reloading systemd..."
systemctl daemon-reload
systemctl enable netcheck
systemctl start netcheck

echo "NetCheck service has been started successfully!"