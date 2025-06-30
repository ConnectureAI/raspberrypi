#!/usr/bin/env python3
"""
Raspberry Pi Companion Server
WebSocket server that connects to Mac and streams sensor data
"""

import asyncio
import websockets
import json
import logging
import socket
import time
from datetime import datetime
from gpio_detector import GPIODetector
from sensor_drivers import SensorManager
import subprocess
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/pi-companion.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PiServer:
    def __init__(self, config_file='config.json'):
        self.config = self.load_config(config_file)
        self.gpio_detector = GPIODetector()
        self.sensor_manager = SensorManager()
        self.mac_websocket = None
        self.running = False
        self.last_detection = None
        
    def load_config(self, config_file):
        """Load configuration from JSON file"""
        default_config = {
            "websocket_port": 8765,
            "mac_host": "localhost",
            "mac_port": 5001,
            "sensor_interval": 1.0,
            "detection_interval": 5.0,
            "auto_discover": True,
            "debug": True
        }
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    default_config.update(config)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            
        return default_config
    
    def get_pi_ip(self):
        """Get the Pi's IP address"""
        try:
            # Get IP address of wlan0 interface
            result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
            ip = result.stdout.strip().split()[0]
            return ip
        except:
            return "127.0.0.1"
    
    def discover_mac_on_network(self):
        """Try to discover Mac on local network"""
        if not self.config.get('auto_discover', True):
            return None
            
        logger.info("Scanning network for Mac...")
        try:
            # Get network range
            pi_ip = self.get_pi_ip()
            network = '.'.join(pi_ip.split('.')[:-1]) + '.'
            
            # Scan common IP addresses
            for i in range(1, 255):
                ip = f"{network}{i}"
                if ip == pi_ip:
                    continue
                    
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.1)
                    result = sock.connect_ex((ip, self.config['mac_port']))
                    sock.close()
                    
                    if result == 0:
                        logger.info(f"Found Mac at {ip}:{self.config['mac_port']}")
                        return ip
                except:
                    continue
                    
        except Exception as e:
            logger.error(f"Network discovery error: {e}")
            
        return None
    
    async def connect_to_mac(self):
        """Connect to Mac WebSocket server"""
        mac_host = self.config['mac_host']
        
        # Try to discover Mac if localhost fails
        if mac_host == "localhost":
            discovered_ip = self.discover_mac_on_network()
            if discovered_ip:
                mac_host = discovered_ip
        
        max_retries = 5
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                uri = f"ws://{mac_host}:{self.config['mac_port']}/pi"
                logger.info(f"Attempting to connect to Mac at {uri} (attempt {attempt + 1})")
                
                self.mac_websocket = await websockets.connect(uri)
                logger.info(f"Connected to Mac at {mac_host}:{self.config['mac_port']}")
                
                # Send initial connection message
                await self.send_to_mac({
                    "type": "connection",
                    "message": "Pi connected",
                    "pi_ip": self.get_pi_ip(),
                    "timestamp": datetime.now().isoformat()
                })
                
                return True
                
            except Exception as e:
                logger.warning(f"Failed to connect to Mac (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    
        logger.error("Could not connect to Mac after all attempts")
        return False
    
    async def send_to_mac(self, data):
        """Send data to Mac via WebSocket"""
        if self.mac_websocket:
            try:
                await self.mac_websocket.send(json.dumps(data))
            except Exception as e:
                logger.error(f"Error sending to Mac: {e}")
                self.mac_websocket = None
    
    async def handle_mac_message(self, message):
        """Handle commands from Mac"""
        try:
            data = json.loads(message)
            command_type = data.get('type')
            
            logger.info(f"Received command from Mac: {command_type}")
            
            if command_type == 'led_control':
                pin = data.get('pin')
                state = data.get('state')
                self.sensor_manager.control_led(pin, state)
                
            elif command_type == 'motor_control':
                pin = data.get('pin')
                direction = data.get('direction')
                speed = data.get('speed', 100)
                self.sensor_manager.control_motor(pin, direction, speed)
                
            elif command_type == 'servo_control':
                pin = data.get('pin')
                angle = data.get('angle')
                self.sensor_manager.control_servo(pin, angle)
                
            elif command_type == 'buzzer_control':
                pin = data.get('pin')
                frequency = data.get('frequency', 1000)
                duration = data.get('duration', 0.5)
                self.sensor_manager.control_buzzer(pin, frequency, duration)
                
            elif command_type == 'request_data':
                # Force immediate sensor reading
                sensor_data = self.sensor_manager.read_all_sensors()
                await self.send_to_mac({
                    "type": "sensor_data",
                    "data": sensor_data,
                    "timestamp": datetime.now().isoformat()
                })
                
        except Exception as e:
            logger.error(f"Error handling Mac message: {e}")
    
    async def sensor_loop(self):
        """Main sensor reading and transmission loop"""
        logger.info("Starting sensor loop")
        
        while self.running:
            try:
                # Check for new GPIO components
                if time.time() - (self.last_detection or 0) > self.config['detection_interval']:
                    detected_components = self.gpio_detector.detect_components()
                    self.sensor_manager.update_components(detected_components)
                    
                    await self.send_to_mac({
                        "type": "gpio_detection",
                        "components": detected_components,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    self.last_detection = time.time()
                
                # Read sensor data
                sensor_data = self.sensor_manager.read_all_sensors()
                
                # Send to Mac
                await self.send_to_mac({
                    "type": "sensor_data",
                    "data": sensor_data,
                    "timestamp": datetime.now().isoformat()
                })
                
                await asyncio.sleep(self.config['sensor_interval'])
                
            except Exception as e:
                logger.error(f"Error in sensor loop: {e}")
                await asyncio.sleep(1)
    
    async def mac_listener(self):
        """Listen for messages from Mac"""
        while self.running and self.mac_websocket:
            try:
                message = await self.mac_websocket.recv()
                await self.handle_mac_message(message)
            except websockets.exceptions.ConnectionClosed:
                logger.warning("Connection to Mac closed")
                self.mac_websocket = None
                break
            except Exception as e:
                logger.error(f"Error receiving from Mac: {e}")
                break
    
    async def websocket_handler(self, websocket, path):
        """Handle incoming WebSocket connections (for debugging)"""
        logger.info(f"WebSocket connection from {websocket.remote_address}")
        try:
            async for message in websocket:
                # Echo back for debugging
                await websocket.send(f"Pi received: {message}")
        except Exception as e:
            logger.error(f"WebSocket handler error: {e}")
    
    async def start_server(self):
        """Start the Pi server"""
        logger.info("Starting Pi Companion Server")
        self.running = True
        
        # Initialize components
        logger.info("Initializing GPIO detector and sensor manager")
        detected_components = self.gpio_detector.detect_components()
        self.sensor_manager.initialize(detected_components)
        
        # Start local WebSocket server for debugging
        logger.info(f"Starting WebSocket server on port {self.config['websocket_port']}")
        server = await websockets.serve(
            self.websocket_handler, 
            "0.0.0.0", 
            self.config['websocket_port']
        )
        
        # Connect to Mac
        mac_connected = await self.connect_to_mac()
        
        # Start main loops
        tasks = [self.sensor_loop()]
        
        if mac_connected:
            tasks.append(self.mac_listener())
        
        # Run all tasks
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.info("Shutting down server")
        finally:
            self.running = False
            server.close()
            await server.wait_closed()
            if self.mac_websocket:
                await self.mac_websocket.close()
            self.sensor_manager.cleanup()

def main():
    """Main entry point"""
    server = PiServer()
    
    try:
        asyncio.run(server.start_server())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")

if __name__ == "__main__":
    main()