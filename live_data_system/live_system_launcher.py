#!/usr/bin/env python3
"""
Live Data System Launcher
Advanced Real-Time Raspberry Pi Prototyping System

This launcher integrates all systems:
- Smart Pi Auto-Configuration
- Intelligent Web Dashboard  
- Advanced Assembly Commands
- Real-time data streaming and visualization
"""

import os
import sys
import time
import threading
import signal
import logging
import asyncio
from pathlib import Path
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('live_data_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import our systems
try:
    from smart_pi_autoconfig import SmartPiAutoConfig
    from intelligent_dashboard import IntelligentDashboard, app, socketio
    from assembly_commands import AdvancedAssemblyCommands
except ImportError as e:
    logger.error(f"Failed to import system modules: {e}")
    sys.exit(1)

class LiveDataSystemLauncher:
    """Main launcher for the complete live data system"""
    
    def __init__(self):
        self.systems = {}
        self.system_threads = {}
        self.shutdown_event = threading.Event()
        self.system_status = {
            'auto_config': False,
            'dashboard': False,
            'assembly_commands': False,
            'data_streaming': False
        }
        
        # System configuration
        self.config = self.load_system_config()
        
    def load_system_config(self) -> dict:
        """Load system configuration"""
        config_path = Path(__file__).parent / 'system_config.json'
        
        default_config = {
            'auto_config': {
                'enabled': True,
                'detection_interval': 1.0,
                'auto_init': True,
                'streaming': True
            },
            'dashboard': {
                'enabled': True,
                'host': '0.0.0.0',
                'port': 5001,
                'debug': False
            },
            'assembly_commands': {
                'enabled': True,
                'web_integration': True
            },
            'data_streaming': {
                'enabled': True,
                'broadcast_rate': 20,  # Hz
                'data_retention': 1000  # data points
            },
            'logging': {
                'level': 'INFO',
                'file': 'live_data_system.log'
            }
        }
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    # Merge with defaults
                    for section, settings in user_config.items():
                        if section in default_config:
                            default_config[section].update(settings)
                        else:
                            default_config[section] = settings
            except Exception as e:
                logger.warning(f"Error loading config file: {e}")
        else:
            # Create default config file
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            logger.info(f"Created default config file: {config_path}")
        
        return default_config
    
    def initialize_systems(self):
        """Initialize all system components"""
        logger.info("🚀 Initializing Live Data System Components")
        
        try:
            # Initialize Auto-Configuration System
            if self.config['auto_config']['enabled']:
                self.initialize_auto_config()
            
            # Initialize Assembly Commands
            if self.config['assembly_commands']['enabled']:
                self.initialize_assembly_commands()
            
            # Initialize Dashboard (this will use the other systems)
            if self.config['dashboard']['enabled']:
                self.initialize_dashboard()
            
            # Setup signal handlers
            self.setup_signal_handlers()
            
            logger.info("✅ All systems initialized successfully!")
            self.print_system_status()
            
        except Exception as e:
            logger.error(f"❌ System initialization failed: {e}")
            raise
    
    def initialize_auto_config(self):
        """Initialize Smart Pi Auto-Configuration"""
        logger.info("🤖 Initializing Smart Pi Auto-Configuration...")
        
        try:
            # Load component database
            component_db = self.load_component_database()
            
            # Initialize auto-config system
            self.systems['auto_config'] = SmartPiAutoConfig(component_db)
            
            # Configure settings from config
            config = self.config['auto_config']
            self.systems['auto_config'].detection_enabled = config.get('enabled', True)
            self.systems['auto_config'].auto_init_enabled = config.get('auto_init', True) 
            self.systems['auto_config'].streaming_enabled = config.get('streaming', True)
            
            self.system_status['auto_config'] = True
            logger.info("✅ Auto-configuration system ready")
            
        except Exception as e:
            logger.error(f"❌ Auto-configuration initialization failed: {e}")
            raise
    
    def initialize_assembly_commands(self):
        """Initialize Advanced Assembly Commands"""
        logger.info("🔧 Initializing Advanced Assembly Commands...")
        
        try:
            component_db = self.load_component_database()
            auto_config = self.systems.get('auto_config')
            
            self.systems['assembly_commands'] = AdvancedAssemblyCommands(
                component_db=component_db,
                auto_config=auto_config
            )
            
            self.system_status['assembly_commands'] = True
            logger.info("✅ Assembly commands system ready")
            
        except Exception as e:
            logger.error(f"❌ Assembly commands initialization failed: {e}")
            raise
    
    def initialize_dashboard(self):
        """Initialize Intelligent Web Dashboard"""
        logger.info("🌐 Initializing Intelligent Web Dashboard...")
        
        try:
            # The dashboard is initialized via the imported module
            # We need to connect it to our other systems
            
            # Update dashboard with our systems
            from intelligent_dashboard import dashboard
            dashboard.auto_config = self.systems.get('auto_config')
            dashboard.assembly_commands = self.systems.get('assembly_commands')
            
            # Add assembly command endpoint to Flask app
            self.add_assembly_command_endpoints()
            
            self.system_status['dashboard'] = True
            logger.info("✅ Dashboard system ready")
            
        except Exception as e:
            logger.error(f"❌ Dashboard initialization failed: {e}")
            raise
    
    def add_assembly_command_endpoints(self):
        """Add assembly command endpoints to the dashboard"""
        from intelligent_dashboard import app
        from flask import request, jsonify
        
        @app.route('/api/assembly/command', methods=['POST'])
        def process_assembly_command():
            """Process assembly command via API"""
            try:
                data = request.json
                command = data.get('command', '')
                
                if not command:
                    return jsonify({'error': 'No command provided'}), 400
                
                # Process command using assembly commands system
                assembly_system = self.systems.get('assembly_commands')
                if assembly_system:
                    response = assembly_system.process_command(command)
                    return jsonify({
                        'success': True,
                        'command': command,
                        'response': response
                    })
                else:
                    return jsonify({'error': 'Assembly commands system not available'}), 503
                    
            except Exception as e:
                logger.error(f"Assembly command processing error: {e}")
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/assembly/components')
        def get_assembly_components():
            """Get available components for assembly"""
            try:
                assembly_system = self.systems.get('assembly_commands')
                if assembly_system:
                    components_info = assembly_system.component_library
                    return jsonify(components_info)
                else:
                    return jsonify({'error': 'Assembly commands system not available'}), 503
            except Exception as e:
                logger.error(f"Component listing error: {e}")
                return jsonify({'error': str(e)}), 500
    
    def load_component_database(self):
        """Load component database from analysis"""
        try:
            db_path = Path(__file__).parent.parent / 'component_code_mapping.json'
            if db_path.exists():
                with open(db_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load component database: {e}")
        
        # Return minimal fallback database
        return {
            "component_mapping": {
                "LED": {"complexity": 1, "pins_used": ["GPIO17"]},
                "DHT11": {"complexity": 3, "pins_used": ["GPIO17"]},
                "BMP180": {"complexity": 4, "pins_used": ["GPIO2", "GPIO3"], "i2c_address": "0x77"}
            }
        }
    
    def start_dashboard_server(self):
        """Start the dashboard web server"""
        config = self.config['dashboard']
        
        logger.info(f"🌐 Starting dashboard server on {config['host']}:{config['port']}")
        
        try:
            socketio.run(
                app,
                host=config['host'],
                port=config['port'],
                debug=config.get('debug', False),
                use_reloader=False,
                log_output=False  # Prevent duplicate logging
            )
        except Exception as e:
            logger.error(f"Dashboard server error: {e}")
    
    def start_background_tasks(self):
        """Start background monitoring and data processing tasks"""
        logger.info("📊 Starting background data processing tasks")
        
        # Start system health monitoring
        health_thread = threading.Thread(target=self.system_health_monitor, daemon=True)
        health_thread.start()
        self.system_threads['health_monitor'] = health_thread
        
        # Start performance monitoring
        perf_thread = threading.Thread(target=self.performance_monitor, daemon=True)
        perf_thread.start()
        self.system_threads['performance_monitor'] = perf_thread
        
        self.system_status['data_streaming'] = True
        logger.info("✅ Background tasks started")
    
    def system_health_monitor(self):
        """Monitor system health and component status"""
        while not self.shutdown_event.is_set():
            try:
                # Check auto-config system health
                if self.systems.get('auto_config'):
                    auto_config = self.systems['auto_config']
                    status = auto_config.get_system_status()
                    
                    # Log system statistics
                    detected_count = len(status.get('detected_components', {}))
                    active_count = len(status.get('active_sensors', {}))
                    
                    if detected_count != active_count:
                        logger.warning(f"Component status mismatch: {detected_count} detected, {active_count} active")
                
                # Check for system errors
                # Add more health checks here
                
                time.sleep(30)  # Health check every 30 seconds
                
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                time.sleep(60)
    
    def performance_monitor(self):
        """Monitor system performance metrics"""
        start_time = time.time()
        data_points_processed = 0
        
        while not self.shutdown_event.is_set():
            try:
                # Calculate performance metrics
                uptime = time.time() - start_time
                
                if self.systems.get('auto_config'):
                    auto_config = self.systems['auto_config']
                    status = auto_config.get_system_status()
                    
                    stream_count = status.get('data_streams', {})
                    total_streams = len([s for s in stream_count.values() if s > 0])
                    
                    # Log performance metrics periodically
                    if uptime % 300 < 30:  # Every 5 minutes
                        logger.info(f"📈 Performance: Uptime {uptime:.0f}s, Active streams: {total_streams}")
                
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"Performance monitor error: {e}")
                time.sleep(60)
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"🛑 Received signal {signum}, initiating graceful shutdown...")
            self.shutdown_system()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def run_system(self):
        """Run the complete live data system"""
        logger.info("🏃 Starting Live Data System main loop...")
        
        try:
            # Start background tasks
            self.start_background_tasks()
            
            # Start dashboard server (this will block)
            self.start_dashboard_server()
            
        except KeyboardInterrupt:
            logger.info("👋 Keyboard interrupt received")
        except Exception as e:
            logger.error(f"❌ System runtime error: {e}")
        finally:
            self.shutdown_system()
    
    def shutdown_system(self):
        """Gracefully shutdown all system components"""
        logger.info("🛑 Shutting down Live Data System...")
        
        self.shutdown_event.set()
        
        # Shutdown auto-configuration system
        if self.systems.get('auto_config'):
            try:
                self.systems['auto_config'].cleanup()
                logger.info("✅ Auto-configuration system shut down")
            except Exception as e:
                logger.error(f"Error shutting down auto-config: {e}")
        
        # Shutdown dashboard
        if self.systems.get('dashboard'):
            try:
                # Dashboard shutdown is handled by Flask/SocketIO
                logger.info("✅ Dashboard system shut down")
            except Exception as e:
                logger.error(f"Error shutting down dashboard: {e}")
        
        # Wait for background threads
        for thread_name, thread in self.system_threads.items():
            if thread.is_alive():
                logger.info(f"Waiting for {thread_name} to finish...")
                thread.join(timeout=5)
        
        logger.info("✅ Live Data System shutdown complete")
    
    def print_system_status(self):
        """Print comprehensive system status"""
        print("\n" + "="*70)
        print("🤖 LIVE DATA SYSTEM - COMPREHENSIVE STATUS")
        print("="*70)
        
        # System components status
        print("📋 SYSTEM COMPONENTS:")
        for component, status in self.system_status.items():
            status_icon = "✅" if status else "❌"
            print(f"  {status_icon} {component.replace('_', ' ').title()}")
        
        print("\n🔧 SYSTEM CAPABILITIES:")
        if self.system_status['auto_config']:
            print("  • Smart component auto-detection on boot")
            print("  • GPIO pattern-based sensor initialization") 
            print("  • Communication protocol optimization")
            print("  • Pin conflict resolution for multi-sensor scenarios")
        
        if self.system_status['dashboard']:
            print("  • Component specifications for auto-visualization")
            print("  • Sensor reading patterns for optimal sampling")
            print("  • Motor control patterns for actuator integration")
            print("  • Real-time breadboard overlay with live status")
        
        if self.system_status['assembly_commands']:
            print("  • Component database + code mapping integration")
            print("  • Compatibility matrices + optimal pin assignment")
            print("  • Auto-detection + conflict resolution debugging")
            print("  • 8-tier complexity analysis for layout optimization")
        
        print(f"\n🌐 ACCESS POINTS:")
        config = self.config['dashboard']
        print(f"  • Web Dashboard: http://{config['host']}:{config['port']}")
        print(f"  • Assembly Commands: Available via web interface")
        print(f"  • Real-time Data: WebSocket streaming enabled")
        
        print(f"\n💡 QUICK START:")
        print(f"  1. Connect components to your Raspberry Pi")
        print(f"  2. Open http://localhost:{config['port']} in your browser")
        print(f"  3. Watch auto-detection identify your components")
        print(f"  4. Use assembly commands: 'Show LED matrix setup'")
        print(f"  5. View live data streams and control actuators")
        
        print("="*70)

def check_dependencies():
    """Check system dependencies"""
    required_modules = [
        'flask', 'flask_socketio', 'json', 'threading', 'asyncio'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        logger.error(f"❌ Missing required modules: {missing_modules}")
        logger.info("Install with: pip install flask flask-socketio")
        return False
    
    return True

def create_system_directories():
    """Create necessary system directories"""
    directories = [
        'templates',
        'static/css',
        'static/js', 
        'logs',
        'data',
        'config'
    ]
    
    for directory in directories:
        dir_path = Path(directory)
        dir_path.mkdir(parents=True, exist_ok=True)
    
    logger.info("✅ System directories created")

def main():
    """Main entry point for Live Data System"""
    print("🚀 Starting Advanced Real-Time Raspberry Pi Live Data System...")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Create system directories
    create_system_directories()
    
    # Initialize and run system
    try:
        launcher = LiveDataSystemLauncher()
        launcher.initialize_systems()
        launcher.run_system()
        
    except KeyboardInterrupt:
        logger.info("👋 System stopped by user")
    except Exception as e:
        logger.error(f"❌ System failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()