#!/usr/bin/env python3
"""
Advanced Real-Time Raspberry Pi Prototyping System
Startup Script and System Integration

This script initializes and starts the complete prototyping system:
- Loads comprehensive component analysis
- Starts web interface with intelligent assembly
- Initializes deployment pipeline
- Activates natural language processing
- Sets up hot-swap monitoring
"""

import os
import sys
import asyncio
import signal
import threading
import json
from pathlib import Path
import logging
import time
from typing import Dict, List

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('prototyping_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import our modules
try:
    from app import app, prototyping_system
    from deployment_engine import DeploymentEngine
    from advanced_nlp import AdvancedNLPProcessor
    from smart_code_completion import SmartCodeCompletion
    from code_pattern_library import *
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    sys.exit(1)

class PrototypingSystemManager:
    """Manages the complete prototyping system lifecycle"""
    
    def __init__(self):
        self.system_status = {
            'web_server': False,
            'deployment_engine': False,
            'nlp_processor': False,
            'hot_swap_monitor': False,
            'component_db_loaded': False
        }
        
        self.components = {}
        self.deployment_engine = None
        self.nlp_processor = None
        self.web_server_thread = None
        self.shutdown_event = threading.Event()
        
    def initialize_system(self):
        """Initialize all system components"""
        logger.info("🚀 Initializing Advanced Raspberry Pi Prototyping System...")
        
        try:
            # Load component database
            self.load_component_database()
            
            # Initialize smart code completion
            self.initialize_code_completion()
            
            # Initialize deployment engine
            self.initialize_deployment_engine()
            
            # Initialize NLP processor
            self.initialize_nlp_processor()
            
            # Start web server
            self.start_web_server()
            
            # Setup signal handlers
            self.setup_signal_handlers()
            
            logger.info("✅ System initialization complete!")
            self.print_system_status()
            
        except Exception as e:
            logger.error(f"❌ System initialization failed: {e}")
            raise
    
    def load_component_database(self):
        """Load comprehensive component analysis data"""
        logger.info("📊 Loading component database...")
        
        try:
            # Load component mapping
            mapping_path = Path(__file__).parent.parent / 'component_code_mapping.json'
            if mapping_path.exists():
                with open(mapping_path, 'r') as f:
                    self.components = json.load(f)
                logger.info(f"✅ Loaded {len(self.components.get('component_mapping', {}))} components")
            else:
                logger.warning("⚠️ Component mapping file not found, using fallback data")
                self.components = self.create_fallback_component_data()
            
            # Update global prototyping system
            prototyping_system.component_db = self.components
            self.system_status['component_db_loaded'] = True
            
        except Exception as e:
            logger.error(f"❌ Failed to load component database: {e}")
            raise
    
    def create_fallback_component_data(self):
        """Create fallback component data if files not found"""
        return {
            "component_mapping": {
                "LED": {
                    "examples": ["01.1.1_Blink", "02.1.1_ButtonLED"],
                    "pins_used": ["GPIO17"],
                    "complexity": 1,
                    "libraries": ["gpiozero.LED"],
                    "common_patterns": ["led.on()", "led.off()"]
                },
                "Button": {
                    "examples": ["02.1.1_ButtonLED"],
                    "pins_used": ["GPIO18"],
                    "complexity": 1,
                    "libraries": ["gpiozero.Button"],
                    "common_patterns": ["button.is_pressed"]
                },
                "RGBLED": {
                    "examples": ["05.1.1_ColorfulLED"],
                    "pins_used": ["GPIO17", "GPIO18", "GPIO27"],
                    "complexity": 2,
                    "libraries": ["gpiozero.RGBLED"],
                    "common_patterns": ["led.red = value", "led.color = (r,g,b)"]
                },
                "DHT11": {
                    "examples": ["21.1.1_DHT11"],
                    "pins_used": ["GPIO17"],
                    "complexity": 3,
                    "libraries": ["Freenove_DHT.DHT"],
                    "common_patterns": ["dht.readDHT11()", "dht.getTemperature()"]
                }
            },
            "learning_progression": {
                "level_1_basic": ["LED", "Button"],
                "level_2_analog": ["RGBLED", "DHT11"],
                "level_3_advanced": ["Camera_Module", "Motor_DC"]
            }
        }
    
    def initialize_code_completion(self):
        """Initialize smart code completion system"""
        logger.info("🧠 Initializing smart code completion...")
        
        try:
            prototyping_system.code_completion = SmartCodeCompletion()
            logger.info("✅ Code completion system ready")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize code completion: {e}")
            raise
    
    def initialize_deployment_engine(self):
        """Initialize zero-config deployment engine"""
        logger.info("🚀 Initializing deployment engine...")
        
        try:
            self.deployment_engine = DeploymentEngine(
                self.components, 
                prototyping_system.code_completion
            )
            self.system_status['deployment_engine'] = True
            logger.info("✅ Deployment engine ready")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize deployment engine: {e}")
            raise
    
    def initialize_nlp_processor(self):
        """Initialize natural language processor"""
        logger.info("🗣️ Initializing NLP processor...")
        
        try:
            self.nlp_processor = AdvancedNLPProcessor(
                self.components,
                prototyping_system.code_completion
            )
            
            # Update global prototyping system
            prototyping_system.nlp_processor = self.nlp_processor
            self.system_status['nlp_processor'] = True
            logger.info("✅ NLP processor ready")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize NLP processor: {e}")
            raise
    
    def start_web_server(self):
        """Start the web server in a separate thread"""
        logger.info("🌐 Starting web server...")
        
        try:
            def run_server():
                app.run(
                    host='0.0.0.0',
                    port=5000,
                    debug=False,
                    use_reloader=False,
                    threaded=True
                )
            
            self.web_server_thread = threading.Thread(target=run_server, daemon=True)
            self.web_server_thread.start()
            
            # Wait a moment for server to start
            time.sleep(2)
            self.system_status['web_server'] = True
            logger.info("✅ Web server running on http://0.0.0.0:5000")
            
        except Exception as e:
            logger.error(f"❌ Failed to start web server: {e}")
            raise
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"🛑 Received signal {signum}, shutting down...")
            self.shutdown_system()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def print_system_status(self):
        """Print current system status"""
        print("\n" + "="*60)
        print("🤖 ADVANCED RASPBERRY PI PROTOTYPING SYSTEM")
        print("="*60)
        print(f"📊 Component Database: {'✅ Loaded' if self.system_status['component_db_loaded'] else '❌ Failed'}")
        print(f"🧠 Code Completion: {'✅ Ready' if prototyping_system.code_completion else '❌ Failed'}")
        print(f"🚀 Deployment Engine: {'✅ Ready' if self.system_status['deployment_engine'] else '❌ Failed'}")
        print(f"🗣️ NLP Processor: {'✅ Ready' if self.system_status['nlp_processor'] else '❌ Failed'}")
        print(f"🌐 Web Server: {'✅ Running' if self.system_status['web_server'] else '❌ Failed'}")
        print("="*60)
        print("\n📋 AVAILABLE FEATURES:")
        print("• Interactive breadboard visualizer with conflict detection")
        print("• Smart component suggestions based on 35+ component analysis")
        print("• Natural language project creation ('Build temperature monitor')")
        print("• Zero-config deployment to Raspberry Pi")
        print("• Hot-swap component detection and auto-redeployment")
        print("• Real-time code generation using extracted patterns")
        print("• Visual assembly guides with step-by-step instructions")
        print("• Learning pathway recommendations")
        print("\n🌐 ACCESS:")
        print("Web Interface: http://localhost:5000")
        print("API Endpoints: http://localhost:5000/api/")
        print("\n💡 QUICK START:")
        print("1. Open http://localhost:5000 in your browser")
        print("2. Try: 'Build a temperature monitor with LCD display'")
        print("3. Add components from the library")
        print("4. Generate and deploy code to your Pi")
        print("="*60)
    
    async def start_pi_discovery(self):
        """Start automatic Pi discovery in background"""
        if self.deployment_engine:
            logger.info("🔍 Starting Raspberry Pi auto-discovery...")
            
            try:
                devices = await self.deployment_engine.discover_pi_devices()
                if devices:
                    logger.info(f"✅ Found {len(devices)} Raspberry Pi devices:")
                    for device in devices:
                        logger.info(f"  • {device['address']} - {device.get('hostname', 'Unknown')}")
                else:
                    logger.info("ℹ️ No Raspberry Pi devices found on network")
                    
            except Exception as e:
                logger.error(f"❌ Pi discovery failed: {e}")
    
    def run_system(self):
        """Run the main system loop"""
        logger.info("🏃 Starting main system loop...")
        
        # Start Pi discovery
        try:
            asyncio.run(self.start_pi_discovery())
        except Exception as e:
            logger.error(f"Failed to start Pi discovery: {e}")
        
        # Main loop
        try:
            while not self.shutdown_event.is_set():
                # System health checks
                self.perform_health_checks()
                
                # Wait or handle other periodic tasks
                self.shutdown_event.wait(30)  # Check every 30 seconds
                
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
        finally:
            self.shutdown_system()
    
    def perform_health_checks(self):
        """Perform periodic system health checks"""
        # Check if web server is still running
        if self.web_server_thread and not self.web_server_thread.is_alive():
            logger.warning("⚠️ Web server thread died, attempting restart...")
            try:
                self.start_web_server()
            except Exception as e:
                logger.error(f"Failed to restart web server: {e}")
        
        # Log system status
        active_connections = len(getattr(prototyping_system, 'pi_connections', {}))
        if active_connections > 0:
            logger.info(f"📡 Active Pi connections: {active_connections}")
    
    def shutdown_system(self):
        """Gracefully shutdown the system"""
        logger.info("🛑 Shutting down prototyping system...")
        
        self.shutdown_event.set()
        
        # Close Pi connections
        if hasattr(prototyping_system, 'pi_connections'):
            for pi_addr, connection in prototyping_system.pi_connections.items():
                try:
                    connection.close()
                    logger.info(f"✅ Closed connection to {pi_addr}")
                except:
                    pass
        
        logger.info("✅ System shutdown complete")

def check_dependencies():
    """Check if all required dependencies are available"""
    required_modules = [
        'flask',
        'paramiko', 
        'asyncio'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        logger.error(f"❌ Missing required modules: {missing_modules}")
        logger.info("Install with: pip install flask paramiko")
        return False
    
    return True

def create_project_structure():
    """Create necessary project directories"""
    directories = [
        'templates',
        'static/css',
        'static/js',
        'static/assembly',
        'logs',
        'projects',
        'backups'
    ]
    
    for directory in directories:
        dir_path = Path(directory)
        dir_path.mkdir(parents=True, exist_ok=True)
    
    logger.info("✅ Project structure created")

def main():
    """Main entry point"""
    print("🚀 Starting Advanced Raspberry Pi Prototyping System...")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Create project structure
    create_project_structure()
    
    # Initialize and run system
    try:
        system_manager = PrototypingSystemManager()
        system_manager.initialize_system()
        system_manager.run_system()
        
    except KeyboardInterrupt:
        logger.info("👋 System stopped by user")
    except Exception as e:
        logger.error(f"❌ System failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()