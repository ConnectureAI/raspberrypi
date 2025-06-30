#!/bin/bash

# Raspberry Pi Companion Installation Script
# Sets up the Pi companion system for auto-detection and WebSocket communication

set -e  # Exit on any error

echo "=========================================="
echo "Raspberry Pi Companion Installation"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   error "This script should not be run as root. Run as pi user instead."
   exit 1
fi

# Check if we're on a Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    warn "This doesn't appear to be a Raspberry Pi. Continuing anyway..."
fi

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
INSTALL_DIR="/home/pi/pi-companion"

log "Script directory: $SCRIPT_DIR"
log "Install directory: $INSTALL_DIR"

# Update system packages
log "Updating system packages..."
sudo apt update

# Install system dependencies
log "Installing system dependencies..."
sudo apt install -y     python3     python3-pip     python3-venv     git     i2c-tools     python3-smbus     python3-spidev     pigpio     python3-pigpio

# Install Node.js
log "Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Gemini CLI
log "Installing Gemini CLI..."
sudo npm install -g @google/generative-ai-cli

# Enable I2C and SPI
log "Enabling I2C and SPI interfaces..."
if ! grep -q "dtparam=i2c=on" /boot/config.txt; then
    echo "dtparam=i2c=on" | sudo tee -a /boot/config.txt
    log "I2C enabled in config.txt"
fi

if ! grep -q "dtparam=spi=on" /boot/config.txt; then
    echo "dtparam=spi=on" | sudo tee -a /boot/config.txt
    log "SPI enabled in config.txt"
fi

# Enable pigpio daemon
log "Enabling pigpio daemon..."
sudo systemctl enable pigpiod
sudo systemctl start pigpiod

# Create installation directory
log "Creating installation directory..."
if [ -d "$INSTALL_DIR" ]; then
    warn "Installation directory exists. Backing up..."
    sudo mv "$INSTALL_DIR" "${INSTALL_DIR}.backup.$(date +%Y%m%d_%H%M%S)"
fi

sudo mkdir -p "$INSTALL_DIR"
sudo chown pi:pi "$INSTALL_DIR"

# Copy files to installation directory
log "Copying Pi companion files..."
cp "$SCRIPT_DIR"/*.py "$INSTALL_DIR/"
cp "$SCRIPT_DIR"/requirements.txt "$INSTALL_DIR/"
cp "$SCRIPT_DIR"/config.json "$INSTALL_DIR/"

# Create Python virtual environment
log "Creating Python virtual environment..."
cd "$INSTALL_DIR"
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
log "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
log "Installing Python dependencies..."
pip install -r requirements.txt

# Create log directory
log "Creating log directory..."
sudo mkdir -p /var/log
sudo touch /var/log/pi-companion.log
sudo chown pi:pi /var/log/pi-companion.log

# Install systemd service
log "Installing systemd service..."
sudo cp "$SCRIPT_DIR"/pi-companion.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable pi-companion.service

# Create startup script
log "Creating startup script..."
cat > "$INSTALL_DIR/start.sh" << 'EOF'
#!/bin/bash
cd /home/pi/pi-companion
source venv/bin/activate
python3 pi_server.py
EOF

chmod +x "$INSTALL_DIR/start.sh"

# Test GPIO access
log "Testing GPIO access..."
if python3 -c "import RPi.GPIO; RPi.GPIO.setmode(RPi.GPIO.BCM); print('GPIO test passed')" 2>/dev/null; then
    log "GPIO access test passed"
else
    warn "GPIO access test failed. You may need to add pi user to gpio group:"
    warn "sudo usermod -a -G gpio pi"
fi

# Test I2C access
log "Testing I2C access..."
if i2cdetect -y 1 >/dev/null 2>&1; then
    log "I2C test passed"
else
    warn "I2C test failed. Check if I2C is enabled and working."
fi

# Create network discovery script
log "Creating network discovery script..."
cat > "$INSTALL_DIR/find_mac.py" << 'EOF'
#!/usr/bin/env python3
import socket
import subprocess

def get_pi_ip():
    try:
        result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
        return result.stdout.strip().split()[0]
    except:
        return "127.0.0.1"

def scan_for_mac(port=5001):
    pi_ip = get_pi_ip()
    network = '.'.join(pi_ip.split('.')[:-1]) + '.'
    
    print(f"Scanning network {network}* for Mac on port {port}...")
    
    for i in range(1, 255):
        ip = f"{network}{i}"
        if ip == pi_ip:
            continue
            
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.1)
            result = sock.connect_ex((ip, port))
            sock.close()
            
            if result == 0:
                print(f"Found Mac at {ip}:{port}")
                return ip
        except:
            continue
    
    print("Mac not found on network")
    return None

if __name__ == "__main__":
    scan_for_mac()
EOF

chmod +x "$INSTALL_DIR/find_mac.py"

# Create test script
log "Creating test script..."
cat > "$INSTALL_DIR/test_components.py" << 'EOF'
#!/usr/bin/env python3
"""Test script to verify component detection and drivers"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from gpio_detector import GPIODetector
from sensor_drivers import SensorManager
import time

def main():
    print("Testing GPIO component detection...")
    
    detector = GPIODetector()
    sensor_manager = SensorManager()
    
    # Detect components
    print("\nScanning for components...")
    components = detector.detect_components()
    
    if components:
        print(f"\nFound {len(components)} components:")
        for comp_id, details in components.items():
            print(f"  {comp_id}: {details['type']} ({details.get('subtype', 'unknown')})")
        
        # Initialize sensor manager
        print("\nInitializing sensor manager...")
        sensor_manager.initialize(components)
        
        # Read sensor data
        print("\nReading sensor data...")
        for i in range(5):
            readings = sensor_manager.read_all_sensors()
            print(f"Reading {i+1}: {len(readings)} sensors")
            for sensor_id, data in readings.items():
                print(f"  {sensor_id}: {data}")
            time.sleep(1)
            
    else:
        print("No components detected. Try connecting some sensors!")
    
    print("\nTest completed.")
    sensor_manager.cleanup()

if __name__ == "__main__":
    main()
EOF

chmod +x "$INSTALL_DIR/test_components.py"

# Create uninstall script
log "Creating uninstall script..."
cat > "$INSTALL_DIR/uninstall.sh" << 'EOF'
#!/bin/bash
echo "Uninstalling Pi Companion..."

# Stop and disable service
sudo systemctl stop pi-companion.service
sudo systemctl disable pi-companion.service
sudo rm -f /etc/systemd/system/pi-companion.service
sudo systemctl daemon-reload

# Remove installation directory
sudo rm -rf /home/pi/pi-companion

# Remove log file
sudo rm -f /var/log/pi-companion.log

echo "Pi Companion uninstalled."
EOF

chmod +x "$INSTALL_DIR/uninstall.sh"

# Set permissions
sudo chown -R pi:pi "$INSTALL_DIR"

echo ""
echo "=========================================="
echo -e "${GREEN}Installation completed successfully!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Reboot your Pi to enable I2C/SPI:"
echo "   sudo reboot"
echo ""
echo "2. After reboot, test the installation:"
echo "   cd $INSTALL_DIR"
echo "   ./test_components.py"
echo ""
echo "3. Start the service:"
echo "   sudo systemctl start pi-companion.service"
echo ""
echo "4. Check service status:"
echo "   sudo systemctl status pi-companion.service"
echo ""
echo "5. View logs:"
echo "   tail -f /var/log/pi-companion.log"
echo ""
echo "6. Find your Mac on the network:"
echo "   cd $INSTALL_DIR"
echo "   ./find_mac.py"
echo ""
echo "Configuration file: $INSTALL_DIR/config.json"
echo "Manual start: $INSTALL_DIR/start.sh"
echo "Uninstall: $INSTALL_DIR/uninstall.sh"
echo ""

if ! systemctl is-enabled pigpiod >/dev/null 2>&1; then
    warn "pigpiod service may not be enabled. Enable it with:"
    warn "sudo systemctl enable pigpiod"
fi

log "Installation directory: $INSTALL_DIR"
log "Service name: pi-companion.service"
log "Log file: /var/log/pi-companion.log"

echo ""
echo -e "${BLUE}Ready to connect to your Mac!${NC}"