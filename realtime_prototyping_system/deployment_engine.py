#!/usr/bin/env python3
"""
Zero-Config Deployment Pipeline
Advanced Real-Time Raspberry Pi Prototyping System

Features:
- Instant code generation using smart_code_completion.py
- Auto-deploy to Pi using extracted patterns
- Hot-swap detection with component auto-detection
- Progressive component suggestions based on learning pathways
"""

import asyncio
import paramiko
import json
import time
import threading
import socket
from pathlib import Path
import subprocess
import os
import hashlib
from typing import Dict, List, Optional, Tuple
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeploymentEngine:
    """Zero-config deployment pipeline for Raspberry Pi projects"""
    
    def __init__(self, component_db, code_completion):
        self.component_db = component_db
        self.code_completion = code_completion
        self.pi_connections = {}
        self.deployment_history = []
        self.hot_swap_monitor = HotSwapMonitor(self)
        self.code_generator = InstantCodeGenerator(component_db, code_completion)
        
    async def discover_pi_devices(self) -> List[Dict]:
        """Auto-discover Raspberry Pi devices on network"""
        logger.info("🔍 Discovering Raspberry Pi devices...")
        
        discovered_devices = []
        
        # Common Raspberry Pi default IPs and hostnames
        common_addresses = [
            'raspberrypi.local',
            'raspberrypi',
            '192.168.1.100',
            '192.168.1.101',
            '192.168.1.102'
        ]
        
        # Scan local network range
        local_ip = self.get_local_ip()
        if local_ip:
            network_base = '.'.join(local_ip.split('.')[:-1])
            for i in range(100, 110):  # Common Pi IP range
                common_addresses.append(f"{network_base}.{i}")
        
        # Test each address
        tasks = [self.test_pi_connection(addr) for addr in common_addresses]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for addr, result in zip(common_addresses, results):
            if isinstance(result, dict) and result.get('accessible'):
                discovered_devices.append({
                    'address': addr,
                    'hostname': result.get('hostname', 'Unknown'),
                    'pi_version': result.get('pi_version', 'Unknown'),
                    'python_version': result.get('python_version', 'Unknown'),
                    'gpio_library': result.get('gpio_library', False)
                })
        
        logger.info(f"✅ Found {len(discovered_devices)} Raspberry Pi devices")
        return discovered_devices
    
    async def test_pi_connection(self, address: str) -> Dict:
        """Test connection to potential Raspberry Pi"""
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Try common credentials
            credentials = [
                ('pi', 'raspberry'),
                ('pi', 'pi'),
                ('pi', ''),
                ('ubuntu', 'ubuntu')
            ]
            
            for username, password in credentials:
                try:
                    ssh.connect(address, username=username, password=password, timeout=5)
                    
                    # Verify it's a Pi and get system info
                    stdin, stdout, stderr = ssh.exec_command('cat /proc/cpuinfo | grep "Raspberry Pi"')
                    pi_info = stdout.read().decode()
                    
                    if 'Raspberry Pi' in pi_info:
                        # Get additional info
                        system_info = await self.get_pi_system_info(ssh)
                        ssh.close()
                        
                        return {
                            'accessible': True,
                            'username': username,
                            'hostname': address,
                            **system_info
                        }
                    
                    ssh.close()
                    break
                    
                except:
                    continue
            
            return {'accessible': False}
            
        except Exception as e:
            return {'accessible': False, 'error': str(e)}
    
    async def get_pi_system_info(self, ssh) -> Dict:
        """Get detailed Raspberry Pi system information"""
        info = {}
        
        try:
            # Get Pi version
            stdin, stdout, stderr = ssh.exec_command('cat /proc/device-tree/model')
            info['pi_version'] = stdout.read().decode().strip()
            
            # Get Python version
            stdin, stdout, stderr = ssh.exec_command('python3 --version')
            info['python_version'] = stdout.read().decode().strip()
            
            # Check for GPIO libraries
            stdin, stdout, stderr = ssh.exec_command('python3 -c "import gpiozero; print(True)"')
            info['gpio_library'] = 'True' in stdout.read().decode()
            
            # Get available GPIO pins
            stdin, stdout, stderr = ssh.exec_command('ls /sys/class/gpio/')
            gpio_pins = stdout.read().decode()
            info['available_pins'] = [p for p in gpio_pins.split() if p.startswith('gpio')]
            
        except Exception as e:
            logger.warning(f"Error getting system info: {e}")
        
        return info
    
    def get_local_ip(self) -> Optional[str]:
        """Get local machine IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return None
    
    async def instant_deploy(self, project_config: Dict, target_pi: str) -> Dict:
        """Deploy project instantly to Raspberry Pi with zero configuration"""
        logger.info(f"🚀 Starting instant deployment to {target_pi}")
        
        try:
            # Generate optimized code
            code_result = await self.code_generator.generate_optimized_code(project_config)
            if not code_result['success']:
                return {'success': False, 'error': 'Code generation failed'}
            
            # Establish SSH connection
            ssh = self.get_ssh_connection(target_pi)
            if not ssh:
                return {'success': False, 'error': 'Cannot connect to Raspberry Pi'}
            
            # Deploy dependencies
            deps_result = await self.deploy_dependencies(ssh, code_result['dependencies'])
            if not deps_result['success']:
                return {'success': False, 'error': f"Dependency installation failed: {deps_result['error']}"}
            
            # Deploy main code
            deploy_result = await self.deploy_code(ssh, code_result['code'], code_result['filename'])
            if not deploy_result['success']:
                return {'success': False, 'error': f"Code deployment failed: {deploy_result['error']}"}
            
            # Start hot-swap monitoring
            if project_config.get('hot_swap_enabled', True):
                await self.hot_swap_monitor.start_monitoring(target_pi, project_config)
            
            # Run the code
            run_result = await self.run_code(ssh, code_result['filename'], project_config.get('auto_run', True))
            
            ssh.close()
            
            # Record deployment
            self.deployment_history.append({
                'timestamp': time.time(),
                'target': target_pi,
                'project': project_config,
                'code_hash': hashlib.md5(code_result['code'].encode()).hexdigest(),
                'success': True
            })
            
            return {
                'success': True,
                'deployment_id': len(self.deployment_history),
                'code_output': run_result.get('output', ''),
                'monitoring_active': project_config.get('hot_swap_enabled', True)
            }
            
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_ssh_connection(self, target_pi: str) -> Optional[paramiko.SSHClient]:
        """Get SSH connection to Raspberry Pi"""
        if target_pi in self.pi_connections:
            return self.pi_connections[target_pi]
        
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Try stored credentials or defaults
            ssh.connect(target_pi, username='pi', password='raspberry', timeout=10)
            self.pi_connections[target_pi] = ssh
            return ssh
            
        except Exception as e:
            logger.error(f"Cannot connect to {target_pi}: {e}")
            return None
    
    async def deploy_dependencies(self, ssh, dependencies: List[str]) -> Dict:
        """Deploy required dependencies to Raspberry Pi"""
        if not dependencies:
            return {'success': True}
        
        try:
            # Update package list
            stdin, stdout, stderr = ssh.exec_command('sudo apt update')
            stdout.channel.recv_exit_status()  # Wait for completion
            
            # Install Python packages
            for dep in dependencies:
                if dep.startswith('pip:'):
                    package = dep.replace('pip:', '')
                    stdin, stdout, stderr = ssh.exec_command(f'pip3 install {package}')
                    exit_status = stdout.channel.recv_exit_status()
                    if exit_status != 0:
                        error = stderr.read().decode()
                        return {'success': False, 'error': f"Failed to install {package}: {error}"}
                
                elif dep.startswith('apt:'):
                    package = dep.replace('apt:', '')
                    stdin, stdout, stderr = ssh.exec_command(f'sudo apt install -y {package}')
                    exit_status = stdout.channel.recv_exit_status()
                    if exit_status != 0:
                        error = stderr.read().decode()
                        return {'success': False, 'error': f"Failed to install {package}: {error}"}
            
            return {'success': True}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def deploy_code(self, ssh, code: str, filename: str) -> Dict:
        """Deploy generated code to Raspberry Pi"""
        try:
            # Create project directory
            stdin, stdout, stderr = ssh.exec_command('mkdir -p ~/raspberry_pi_projects')
            stdout.channel.recv_exit_status()
            
            # Write code file
            code_path = f'~/raspberry_pi_projects/{filename}'
            stdin, stdout, stderr = ssh.exec_command(f'cat > {code_path}')
            stdin.write(code)
            stdin.close()
            
            exit_status = stdout.channel.recv_exit_status()
            if exit_status != 0:
                error = stderr.read().decode()
                return {'success': False, 'error': f"Failed to write code: {error}"}
            
            # Make executable
            stdin, stdout, stderr = ssh.exec_command(f'chmod +x {code_path}')
            stdout.channel.recv_exit_status()
            
            return {'success': True, 'path': code_path}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def run_code(self, ssh, filename: str, auto_run: bool = True) -> Dict:
        """Run deployed code on Raspberry Pi"""
        if not auto_run:
            return {'success': True, 'message': 'Code deployed but not executed'}
        
        try:
            code_path = f'~/raspberry_pi_projects/{filename}'
            
            # Run in background to avoid blocking
            command = f'cd ~/raspberry_pi_projects && python3 {filename} > output.log 2>&1 &'
            stdin, stdout, stderr = ssh.exec_command(command)
            stdout.channel.recv_exit_status()
            
            # Wait a bit then check for output
            await asyncio.sleep(2)
            
            stdin, stdout, stderr = ssh.exec_command('cd ~/raspberry_pi_projects && head -20 output.log')
            output = stdout.read().decode()
            
            return {'success': True, 'output': output}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

class InstantCodeGenerator:
    """Generates optimized code instantly using analysis patterns"""
    
    def __init__(self, component_db, code_completion):
        self.component_db = component_db
        self.code_completion = code_completion
    
    async def generate_optimized_code(self, project_config: Dict) -> Dict:
        """Generate optimized code for instant deployment"""
        try:
            components = project_config.get('components', [])
            if not components:
                return {'success': False, 'error': 'No components specified'}
            
            # Use our smart code completion for base template
            base_code = self.code_completion.generate_code_template([c['name'] for c in components])
            
            # Optimize for specific deployment environment
            optimized_code = self.optimize_for_pi(base_code, project_config)
            
            # Add monitoring and debugging features
            enhanced_code = self.add_deployment_features(optimized_code, project_config)
            
            # Determine dependencies
            dependencies = self.extract_dependencies(components)
            
            return {
                'success': True,
                'code': enhanced_code,
                'filename': f"project_{int(time.time())}.py",
                'dependencies': dependencies,
                'estimated_runtime': self.estimate_runtime(components)
            }
            
        except Exception as e:
            logger.error(f"Code generation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def optimize_for_pi(self, code: str, config: Dict) -> str:
        """Optimize code specifically for Raspberry Pi deployment"""
        optimizations = [
            # Add Pi-specific imports
            "import RPi.GPIO as GPIO",
            "import os",
            "import signal",
            "import sys",
            
            # Add cleanup handler
            """
def signal_handler(sig, frame):
    print('Cleaning up GPIO...')
    GPIO.cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
""",
            
            # Add error handling for common Pi issues
            """
try:
    # Check if running on Raspberry Pi
    with open('/proc/cpuinfo', 'r') as f:
        if 'Raspberry Pi' not in f.read():
            print('Warning: Not running on Raspberry Pi')
except:
    pass
"""
        ]
        
        # Insert optimizations at the beginning
        lines = code.split('\n')
        header_end = 0
        for i, line in enumerate(lines):
            if line.startswith('import') or line.startswith('from'):
                header_end = i + 1
        
        optimized_lines = lines[:header_end] + [''] + optimizations + [''] + lines[header_end:]
        
        return '\n'.join(optimized_lines)
    
    def add_deployment_features(self, code: str, config: Dict) -> str:
        """Add deployment-specific features like logging and monitoring"""
        features = []
        
        # Add logging
        if config.get('enable_logging', True):
            features.append("""
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('project.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
""")
        
        # Add performance monitoring
        if config.get('enable_monitoring', True):
            features.append("""
import psutil
import threading

def monitor_performance():
    while True:
        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent
        temp = 0
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = int(f.read().strip()) / 1000
        except:
            pass
        
        logger.info(f'Performance: CPU={cpu_percent}%, Memory={memory_percent}%, Temp={temp}°C')
        time.sleep(30)

# Start monitoring thread
monitor_thread = threading.Thread(target=monitor_performance, daemon=True)
monitor_thread.start()
""")
        
        # Add remote control capability
        if config.get('enable_remote_control', True):
            features.append("""
import socket
import json
import threading

class RemoteControl:
    def __init__(self, port=8888):
        self.port = port
        self.running = True
        
    def start(self):
        def server():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(('0.0.0.0', self.port))
                sock.listen(1)
                logger.info(f'Remote control listening on port {self.port}')
                
                while self.running:
                    try:
                        conn, addr = sock.accept()
                        data = conn.recv(1024).decode()
                        command = json.loads(data)
                        
                        response = self.handle_command(command)
                        conn.send(json.dumps(response).encode())
                        conn.close()
                    except:
                        pass
                        
            except Exception as e:
                logger.error(f'Remote control error: {e}')
        
        threading.Thread(target=server, daemon=True).start()
    
    def handle_command(self, command):
        # Handle remote commands here
        return {'status': 'ok', 'message': 'Command received'}

remote_control = RemoteControl()
remote_control.start()
""")
        
        # Insert features after imports
        lines = code.split('\n')
        import_end = 0
        for i, line in enumerate(lines):
            if not (line.startswith('import') or line.startswith('from') or line.strip() == '' or line.startswith('#')):
                import_end = i
                break
        
        enhanced_lines = lines[:import_end] + features + [''] + lines[import_end:]
        
        return '\n'.join(enhanced_lines)
    
    def extract_dependencies(self, components: List[Dict]) -> List[str]:
        """Extract required dependencies for components"""
        dependencies = set()
        
        for component in components:
            comp_name = component['name']
            if comp_name in self.component_db.get('component_mapping', {}):
                comp_data = self.component_db['component_mapping'][comp_name]
                
                # Add common dependencies
                dependencies.add('pip:gpiozero')
                dependencies.add('pip:RPi.GPIO')
                dependencies.add('pip:psutil')
                
                # Component-specific dependencies
                if 'I2C' in comp_name or 'i2c_address' in comp_data:
                    dependencies.add('pip:smbus')
                    
                if 'SPI' in comp_name:
                    dependencies.add('pip:spidev')
                    
                if 'Camera' in comp_name:
                    dependencies.add('pip:picamera')
                    
                if 'WS2812' in comp_name:
                    dependencies.add('pip:rpi_ws281x')
                    
                if 'DHT' in comp_name:
                    dependencies.add('pip:adafruit-circuitpython-dht')
                    dependencies.add('apt:libgpiod2')
        
        return list(dependencies)
    
    def estimate_runtime(self, components: List[Dict]) -> int:
        """Estimate project runtime complexity in seconds"""
        base_time = 30  # Base startup time
        
        for component in components:
            comp_name = component['name']
            if comp_name in self.component_db.get('component_mapping', {}):
                complexity = self.component_db['component_mapping'][comp_name].get('complexity', 1)
                base_time += complexity * 10
        
        return base_time

class HotSwapMonitor:
    """Monitor for component changes and auto-redeploy"""
    
    def __init__(self, deployment_engine):
        self.deployment_engine = deployment_engine
        self.monitoring_tasks = {}
    
    async def start_monitoring(self, target_pi: str, project_config: Dict):
        """Start monitoring for component changes"""
        if target_pi in self.monitoring_tasks:
            self.monitoring_tasks[target_pi].cancel()
        
        task = asyncio.create_task(self.monitor_loop(target_pi, project_config))
        self.monitoring_tasks[target_pi] = task
        logger.info(f"🔍 Started hot-swap monitoring for {target_pi}")
    
    async def monitor_loop(self, target_pi: str, project_config: Dict):
        """Main monitoring loop for component changes"""
        last_config_hash = self.hash_config(project_config)
        
        while True:
            try:
                await asyncio.sleep(5)  # Check every 5 seconds
                
                # Check for GPIO state changes on Pi
                changes = await self.detect_gpio_changes(target_pi)
                
                if changes:
                    logger.info(f"🔄 Detected component changes on {target_pi}: {changes}")
                    
                    # Auto-suggest new components based on changes
                    suggestions = self.suggest_components_for_changes(changes)
                    
                    if suggestions:
                        # Auto-redeploy with new components
                        updated_config = project_config.copy()
                        updated_config['components'].extend(suggestions)
                        
                        await self.deployment_engine.instant_deploy(updated_config, target_pi)
                        logger.info(f"♻️ Auto-redeployed project with new components")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
    
    async def detect_gpio_changes(self, target_pi: str) -> List[Dict]:
        """Detect GPIO pin state changes that might indicate new components"""
        ssh = self.deployment_engine.get_ssh_connection(target_pi)
        if not ssh:
            return []
        
        try:
            # Read current GPIO states
            stdin, stdout, stderr = ssh.exec_command('cat /sys/kernel/debug/gpio')
            gpio_state = stdout.read().decode()
            
            # Analyze for new connections (simplified detection)
            changes = []
            
            # Look for pins that changed from input to output or vice versa
            # This is a simplified example - real implementation would be more sophisticated
            
            return changes
            
        except Exception as e:
            logger.error(f"GPIO detection error: {e}")
            return []
    
    def suggest_components_for_changes(self, changes: List[Dict]) -> List[Dict]:
        """Suggest components based on detected changes"""
        suggestions = []
        
        for change in changes:
            pin = change.get('pin')
            state = change.get('state')
            
            # Simple heuristics for component suggestion
            if state == 'input_pullup':
                suggestions.append({'name': 'Button', 'pins': {'pin': pin}})
            elif state == 'output_high':
                suggestions.append({'name': 'LED', 'pins': {'pin': pin}})
        
        return suggestions
    
    def hash_config(self, config: Dict) -> str:
        """Generate hash of project configuration"""
        config_str = json.dumps(config, sort_keys=True)
        return hashlib.md5(config_str.encode()).hexdigest()

# Example usage and testing
async def test_deployment():
    """Test the deployment system"""
    
    # Mock component database
    component_db = {
        'component_mapping': {
            'LED': {'complexity': 1, 'pins_used': ['GPIO17']},
            'Button': {'complexity': 1, 'pins_used': ['GPIO18']}
        }
    }
    
    # Mock code completion
    class MockCodeCompletion:
        def generate_code_template(self, components):
            return f"# Generated code for {components}\nprint('Hello from Pi!')"
    
    # Initialize deployment engine
    engine = DeploymentEngine(component_db, MockCodeCompletion())
    
    # Test project configuration
    project_config = {
        'components': [
            {'name': 'LED', 'pins': {'pin': 17}},
            {'name': 'Button', 'pins': {'pin': 18}}
        ],
        'hot_swap_enabled': True,
        'auto_run': True,
        'enable_logging': True,
        'enable_monitoring': True
    }
    
    # Discover Pi devices
    devices = await engine.discover_pi_devices()
    print(f"Discovered devices: {devices}")
    
    # Deploy to first discovered device (if any)
    if devices:
        target = devices[0]['address']
        result = await engine.instant_deploy(project_config, target)
        print(f"Deployment result: {result}")

if __name__ == '__main__':
    asyncio.run(test_deployment())