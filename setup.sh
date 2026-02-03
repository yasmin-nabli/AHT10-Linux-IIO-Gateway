#!/bin/bash

# --- Colors for better readability ---
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting Omni-Sense IoT Gateway Installation...${NC}"

# 1. Install Python dependencies
echo -e "${GREEN}Installing Python dependencies...${NC}"
pip3 install -r requirements.txt

# 2. Configure Mosquitto (Optional but recommended)
echo -e "${GREEN}Setting up Mosquitto configuration...${NC}"
sudo cp config/mosquitto.conf /etc/mosquitto/conf.d/
sudo systemctl restart mosquitto

# 3. Setup the Systemd Service
echo -e "${GREEN}Configuring background service (systemd)...${NC}"
# Use 'pwd' to get the current directory dynamically for ExecStart
WORKING_DIR=$(pwd)
SERVICE_FILE="systemd/iot_gateway.service"

# Update the path in the service file automatically to match the user's folder
sudo sed -i "s|ExecStart=.*|ExecStart=/usr/bin/python3 $WORKING_DIR/src/aht10_collector.py|g" $SERVICE_FILE
sudo sed -i "s|WorkingDirectory=.*|WorkingDirectory=$WORKING_DIR/src|g" $SERVICE_FILE

# Copy and enable the service
sudo cp $SERVICE_FILE /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable iot_gateway.service
sudo systemctl start iot_gateway.service

echo -e "${BLUE}==============================================${NC}"
echo -e "${GREEN}Installation Complete!${NC}"
echo -e "Your IoT Gateway is now running in the background."
echo -e "Check status with: ${BLUE}systemctl status iot_gateway.service${NC}"