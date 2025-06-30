#!/usr/bin/env python3
"""
Intelligent Web Dashboard
Live Data System for Raspberry Pi

This dashboard leverages comprehensive analysis for:
- Import component specifications for automatic data visualization
- Use sensor reading patterns for optimal sampling rates
- Apply motor control patterns for actuator components
- Real-time breadboard overlay showing live component status
"""

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import json
import time
import threading
import asyncio
from pathlib import Path
import sys
import logging
from typing import Dict, List, Optional
from dataclasses import asdict
import queue

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from smart_pi_autoconfig import SmartPiAutoConfig, SensorReading
    from smart_code_completion import SmartCodeCompletion
except ImportError:
    print("⚠️ Auto-config modules not found")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'live_data_system_2024'
socketio = SocketIO(app, cors_allowed_origins="*")

class IntelligentDashboard:
    """Intelligent dashboard using component analysis for auto-visualization"""
    
    def __init__(self):
        self.auto_config = None
        self.assembly_commands = None
        self.component_db = self.load_component_database()
        self.visualization_configs = self.generate_visualization_configs()
        self.actuator_controls = self.generate_actuator_controls()
        
        # Enhanced features for rapid prototyping
        self.project_templates = self.load_project_templates()
        self.active_projects = {}
        self.learning_analytics = {}
        self.live_data = {}
        self.client_connections = set()
        
        # Data streaming
        self.data_queue = queue.Queue()
        self.streaming_active = False
        
        self.initialize_system()
    
    def load_component_database(self) -> Dict:
        """Load component database from comprehensive analysis"""
        try:
            db_path = Path(__file__).parent.parent / 'component_code_mapping.json'
            if db_path.exists():
                with open(db_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load component database: {e}")
        
        # Enhanced fallback with visualization specs
        return {
            "component_mapping": {
                "DHT11": {
                    "complexity": 3,
                    "data_type": "temperature_humidity",
                    "visualization": {
                        "chart_type": "line_dual",
                        "y_axes": [
                            {"label": "Temperature (°C)", "color": "#ff6b6b", "range": [-10, 50]},
                            {"label": "Humidity (%RH)", "color": "#4ecdc4", "range": [0, 100]}
                        ],
                        "update_interval": 2000,
                        "data_points": 100
                    },
                    "thresholds": {
                        "temperature": {"min": 15, "max": 35, "critical": 40},
                        "humidity": {"min": 30, "max": 70, "critical": 90}
                    }
                },
                "DS18B20": {
                    "complexity": 3,
                    "data_type": "temperature",
                    "visualization": {
                        "chart_type": "line_single",
                        "y_axis": {"label": "Temperature (°C)", "color": "#ff9f43", "range": [-55, 125]},
                        "update_interval": 1000,
                        "data_points": 150,
                        "gauge": True
                    },
                    "thresholds": {
                        "temperature": {"min": 0, "max": 30, "critical": 50}
                    }
                },
                "BMP180": {
                    "complexity": 4,
                    "data_type": "pressure_temperature",
                    "visualization": {
                        "chart_type": "line_dual",
                        "y_axes": [
                            {"label": "Pressure (hPa)", "color": "#5f27cd", "range": [950, 1050]},
                            {"label": "Temperature (°C)", "color": "#ff9f43", "range": [-10, 50]}
                        ],
                        "update_interval": 500,
                        "data_points": 200
                    },
                    "thresholds": {
                        "pressure": {"min": 980, "max": 1030, "critical": 1050},
                        "temperature": {"min": 15, "max": 35, "critical": 40}
                    }
                },
                "PIR_Sensor": {
                    "complexity": 2,
                    "data_type": "motion",
                    "visualization": {
                        "chart_type": "event_timeline",
                        "color": "#ff6348",
                        "update_interval": 100,
                        "event_history": 50,
                        "activity_indicator": True
                    },
                    "thresholds": {
                        "motion_frequency": {"max": 10, "critical": 20}  # events per minute
                    }
                },
                "Ultrasonic_HC_SR04": {
                    "complexity": 3,
                    "data_type": "distance",
                    "visualization": {
                        "chart_type": "line_single",
                        "y_axis": {"label": "Distance (cm)", "color": "#2ed573", "range": [0, 400]},
                        "update_interval": 200,
                        "data_points": 100,
                        "proximity_indicator": True
                    },
                    "thresholds": {
                        "distance": {"min": 5, "max": 300, "critical": 2}
                    }
                },
                "ADS1115": {
                    "complexity": 4,
                    "data_type": "analog_voltage",
                    "visualization": {
                        "chart_type": "line_multi",
                        "channels": 4,
                        "y_axis": {"label": "Voltage (V)", "range": [0, 5.0]},
                        "colors": ["#ff6b6b", "#4ecdc4", "#45b7d1", "#96ceb4"],
                        "update_interval": 50,
                        "data_points": 500
                    },
                    "thresholds": {
                        "voltage": {"min": 0.1, "max": 4.9, "critical": 5.1}
                    }
                },
                "LED": {
                    "complexity": 1,
                    "data_type": "actuator",
                    "control": {
                        "type": "switch",
                        "states": ["off", "on"],
                        "colors": {"off": "#6c757d", "on": "#ffc107"}
                    }
                },
                "RGBLED": {
                    "complexity": 2,
                    "data_type": "actuator",
                    "control": {
                        "type": "color_picker",
                        "channels": ["red", "green", "blue"],
                        "range": [0, 255]
                    }
                },
                "Motor_DC": {
                    "complexity": 4,
                    "data_type": "actuator",
                    "control": {
                        "type": "motor_control",
                        "directions": ["forward", "backward", "stop"],
                        "speed_range": [0, 100],
                        "safety_timeout": 30
                    }
                },
                "Servo": {
                    "complexity": 3,
                    "data_type": "actuator",
                    "control": {
                        "type": "slider",
                        "range": [-90, 90],
                        "unit": "degrees",
                        "precision": 1
                    }
                }
            }
        }
    
    def generate_visualization_configs(self) -> Dict:
        """Generate visualization configurations from component analysis"""
        configs = {}
        
        for component_name, component_data in self.component_db.get('component_mapping', {}).items():
            if 'visualization' in component_data:
                viz_config = component_data['visualization'].copy()
                
                # Add component-specific enhancements
                viz_config['component_name'] = component_name
                viz_config['complexity'] = component_data.get('complexity', 1)
                viz_config['thresholds'] = component_data.get('thresholds', {})
                
                # Auto-generate chart configuration
                viz_config['chart_config'] = self.generate_chart_config(component_name, viz_config)
                
                configs[component_name] = viz_config
        
        return configs
    
    def generate_chart_config(self, component_name: str, viz_config: Dict) -> Dict:
        """Generate Chart.js configuration from component analysis"""
        
        chart_type = viz_config.get('chart_type', 'line_single')
        
        if chart_type == 'line_single':
            return {
                'type': 'line',
                'data': {
                    'labels': [],
                    'datasets': [{
                        'label': viz_config['y_axis']['label'],
                        'borderColor': viz_config['y_axis']['color'],
                        'backgroundColor': viz_config['y_axis']['color'] + '20',
                        'data': [],
                        'fill': False,
                        'tension': 0.1
                    }]
                },
                'options': {
                    'responsive': True,
                    'scales': {
                        'y': {
                            'min': viz_config['y_axis']['range'][0],
                            'max': viz_config['y_axis']['range'][1]
                        }
                    },
                    'plugins': {
                        'title': {
                            'display': True,
                            'text': f'{component_name} Data'
                        }
                    }
                }
            }
        
        elif chart_type == 'line_dual':
            return {
                'type': 'line',
                'data': {
                    'labels': [],
                    'datasets': [
                        {
                            'label': viz_config['y_axes'][0]['label'],
                            'borderColor': viz_config['y_axes'][0]['color'],
                            'backgroundColor': viz_config['y_axes'][0]['color'] + '20',
                            'data': [],
                            'yAxisID': 'y',
                            'fill': False
                        },
                        {
                            'label': viz_config['y_axes'][1]['label'],
                            'borderColor': viz_config['y_axes'][1]['color'],
                            'backgroundColor': viz_config['y_axes'][1]['color'] + '20',
                            'data': [],
                            'yAxisID': 'y1',
                            'fill': False
                        }
                    ]
                },
                'options': {
                    'responsive': True,
                    'scales': {
                        'y': {
                            'type': 'linear',
                            'display': True,
                            'position': 'left',
                            'min': viz_config['y_axes'][0]['range'][0],
                            'max': viz_config['y_axes'][0]['range'][1]
                        },
                        'y1': {
                            'type': 'linear',
                            'display': True,
                            'position': 'right',
                            'min': viz_config['y_axes'][1]['range'][0],
                            'max': viz_config['y_axes'][1]['range'][1],
                            'grid': {
                                'drawOnChartArea': False,
                            }
                        }
                    }
                }
            }
        
        elif chart_type == 'line_multi':
            datasets = []
            for i in range(viz_config.get('channels', 1)):
                datasets.append({
                    'label': f'Channel {i+1}',
                    'borderColor': viz_config['colors'][i % len(viz_config['colors'])],
                    'backgroundColor': viz_config['colors'][i % len(viz_config['colors'])] + '20',
                    'data': [],
                    'fill': False
                })
            
            return {
                'type': 'line',
                'data': {
                    'labels': [],
                    'datasets': datasets
                },
                'options': {
                    'responsive': True,
                    'scales': {
                        'y': {
                            'min': viz_config['y_axis']['range'][0],
                            'max': viz_config['y_axis']['range'][1]
                        }
                    }
                }
            }
        
        # Default configuration
        return {
            'type': 'line',
            'data': {'labels': [], 'datasets': []},
            'options': {'responsive': True}
        }
    
    def generate_actuator_controls(self) -> Dict:
        """Generate actuator control interfaces from component analysis"""
        controls = {}
        
        for component_name, component_data in self.component_db.get('component_mapping', {}).items():
            if 'control' in component_data:
                control_config = component_data['control'].copy()
                control_config['component_name'] = component_name
                
                # Generate HTML control interface
                control_config['html'] = self.generate_control_html(component_name, control_config)
                
                controls[component_name] = control_config
        
        return controls
    
    def generate_control_html(self, component_name: str, control_config: Dict) -> str:
        """Generate HTML control interface for actuator"""
        
        control_type = control_config.get('type', 'switch')
        
        if control_type == 'switch':
            return f'''
            <div class="actuator-control" data-component="{component_name}">
                <h6>{component_name} Control</h6>
                <div class="form-check form-switch">
                    <input class="form-check-input" type="checkbox" id="{component_name}_switch" 
                           onchange="controlActuator('{component_name}', 'switch', this.checked)">
                    <label class="form-check-label" for="{component_name}_switch">
                        Power
                    </label>
                </div>
            </div>
            '''
        
        elif control_type == 'color_picker':
            return f'''
            <div class="actuator-control" data-component="{component_name}">
                <h6>{component_name} Control</h6>
                <div class="row">
                    <div class="col-4">
                        <label>Red</label>
                        <input type="range" class="form-range" min="0" max="255" value="0" 
                               id="{component_name}_red" 
                               oninput="controlActuator('{component_name}', 'color', {{r: this.value, g: document.getElementById('{component_name}_green').value, b: document.getElementById('{component_name}_blue').value}})">
                    </div>
                    <div class="col-4">
                        <label>Green</label>
                        <input type="range" class="form-range" min="0" max="255" value="0" 
                               id="{component_name}_green"
                               oninput="controlActuator('{component_name}', 'color', {{r: document.getElementById('{component_name}_red').value, g: this.value, b: document.getElementById('{component_name}_blue').value}})">
                    </div>
                    <div class="col-4">
                        <label>Blue</label>
                        <input type="range" class="form-range" min="0" max="255" value="0" 
                               id="{component_name}_blue"
                               oninput="controlActuator('{component_name}', 'color', {{r: document.getElementById('{component_name}_red').value, g: document.getElementById('{component_name}_green').value, b: this.value}})">
                    </div>
                </div>
            </div>
            '''
        
        elif control_type == 'motor_control':
            return f'''
            <div class="actuator-control" data-component="{component_name}">
                <h6>{component_name} Control</h6>
                <div class="mb-3">
                    <label>Speed</label>
                    <input type="range" class="form-range" min="0" max="100" value="0" 
                           id="{component_name}_speed">
                </div>
                <div class="btn-group" role="group">
                    <button type="button" class="btn btn-outline-primary" 
                            onclick="controlActuator('{component_name}', 'motor', {{direction: 'forward', speed: document.getElementById('{component_name}_speed').value}})">
                        Forward
                    </button>
                    <button type="button" class="btn btn-outline-secondary" 
                            onclick="controlActuator('{component_name}', 'motor', {{direction: 'stop', speed: 0}})">
                        Stop
                    </button>
                    <button type="button" class="btn btn-outline-primary" 
                            onclick="controlActuator('{component_name}', 'motor', {{direction: 'backward', speed: document.getElementById('{component_name}_speed').value}})">
                        Backward
                    </button>
                </div>
            </div>
            '''
        
        elif control_type == 'slider':
            min_val = control_config.get('range', [0, 100])[0]
            max_val = control_config.get('range', [0, 100])[1]
            unit = control_config.get('unit', '')
            
            return f'''
            <div class="actuator-control" data-component="{component_name}">
                <h6>{component_name} Control</h6>
                <div class="mb-3">
                    <label>Position ({unit})</label>
                    <input type="range" class="form-range" min="{min_val}" max="{max_val}" value="{(min_val + max_val) // 2}" 
                           id="{component_name}_position"
                           oninput="controlActuator('{component_name}', 'position', this.value); document.getElementById('{component_name}_value').textContent = this.value + '{unit}'">
                    <div class="text-center">
                        <span id="{component_name}_value">{(min_val + max_val) // 2}{unit}</span>
                    </div>
                </div>
            </div>
            '''
        
        return f'<div class="actuator-control"><h6>{component_name}</h6><p>Control interface not available</p></div>'
    
    def initialize_system(self):
        """Initialize the intelligent dashboard system"""
        logger.info("🚀 Initializing Intelligent Web Dashboard")
        
        # Initialize auto-configuration system
        try:
            self.auto_config = SmartPiAutoConfig()
            logger.info("✅ Auto-configuration system connected")
        except Exception as e:
            logger.warning(f"⚠️ Auto-configuration unavailable: {e}")
        
        # Start data streaming
        self.start_data_streaming()
    
    def start_data_streaming(self):
        """Start real-time data streaming to web clients"""
        self.streaming_active = True
        
        # Start data collection thread
        data_thread = threading.Thread(target=self.data_collection_loop, daemon=True)
        data_thread.start()
        
        # Start WebSocket broadcasting thread
        broadcast_thread = threading.Thread(target=self.broadcast_loop, daemon=True)
        broadcast_thread.start()
        
        logger.info("📊 Real-time data streaming started")
    
    def data_collection_loop(self):
        """Collect data from auto-configuration system"""
        while self.streaming_active:
            try:
                if self.auto_config:
                    # Get system status
                    status = self.auto_config.get_system_status()
                    
                    # Process active sensors
                    for sensor_name, sensor_info in status.get('active_sensors', {}).items():
                        if sensor_info.get('last_reading'):
                            reading_data = sensor_info['last_reading']
                            
                            # Add to live data
                            if sensor_name not in self.live_data:
                                self.live_data[sensor_name] = {
                                    'readings': [],
                                    'last_update': 0,
                                    'component_type': sensor_info.get('component_type', 'Unknown')
                                }
                            
                            # Add reading with timestamp
                            self.live_data[sensor_name]['readings'].append({
                                'timestamp': reading_data['timestamp'],
                                'value': reading_data['value'],
                                'unit': reading_data['unit'],
                                'quality': reading_data['quality']
                            })
                            
                            # Keep only recent readings
                            max_readings = 1000
                            if len(self.live_data[sensor_name]['readings']) > max_readings:
                                self.live_data[sensor_name]['readings'] = \
                                    self.live_data[sensor_name]['readings'][-max_readings:]
                            
                            self.live_data[sensor_name]['last_update'] = time.time()
                
                time.sleep(0.1)  # 10Hz data collection
                
            except Exception as e:
                logger.error(f"Data collection error: {e}")
                time.sleep(1)
    
    def broadcast_loop(self):
        """Broadcast data to connected WebSocket clients"""
        while self.streaming_active:
            try:
                if self.live_data and self.client_connections:
                    # Prepare broadcast data
                    broadcast_data = {}
                    
                    for sensor_name, sensor_data in self.live_data.items():
                        if sensor_data['readings']:
                            latest_reading = sensor_data['readings'][-1]
                            
                            broadcast_data[sensor_name] = {
                                'timestamp': latest_reading['timestamp'],
                                'value': latest_reading['value'],
                                'unit': latest_reading['unit'],
                                'quality': latest_reading['quality'],
                                'component_type': sensor_data['component_type']
                            }
                    
                    if broadcast_data:
                        socketio.emit('sensor_data', broadcast_data)
                
                time.sleep(0.05)  # 20Hz broadcast rate
                
            except Exception as e:
                logger.error(f"Broadcast error: {e}")
                time.sleep(1)
    
    def get_dashboard_config(self) -> Dict:
        """Get complete dashboard configuration"""
        return {
            'visualizations': self.visualization_configs,
            'actuator_controls': self.actuator_controls,
            'component_database': self.component_db,
            'live_data_status': {
                name: {
                    'readings_count': len(data['readings']),
                    'last_update': data['last_update'],
                    'component_type': data['component_type']
                }
                for name, data in self.live_data.items()
            }
        }
    
    # Enhanced methods for rapid prototyping
    def load_project_templates(self) -> Dict:
        """Load project templates for rapid prototyping"""
        return {
            'iot_weather_station': {
                'name': 'IoT Weather Station',
                'difficulty': 5,
                'tier': '4-6',
                'components': ['DHT11', 'BMP180', 'LCD1602', 'LED', 'Resistor'],
                'assemblyTime': 45,
                'description': 'Monitor temperature, humidity, and pressure with LCD display',
                'wiring': {
                    'DHT11': {'pin': 17, 'description': 'Temperature & humidity sensor'},
                    'BMP180': {'pins': [2, 3], 'description': 'Pressure sensor (I2C)'},
                    'LCD1602': {'pins': [4, 6, 13, 19, 26], 'description': '16x2 character display'},
                    'LED': {'pin': 18, 'description': 'Status indicator'}
                },
                'features': ['Real-time readings', 'Data logging', 'Threshold alerts']
            },
            'home_security': {
                'name': 'Home Security System',
                'difficulty': 6,
                'tier': '4-6',
                'components': ['PIR', 'Buzzer', 'LED', 'Camera', 'Resistor'],
                'assemblyTime': 60,
                'description': 'Motion detection with camera capture and alerts',
                'wiring': {
                    'PIR': {'pin': 24, 'description': 'Motion detection sensor'},
                    'Buzzer': {'pin': 25, 'description': 'Alert sound'},
                    'LED': {'pin': 18, 'description': 'Status LED'},
                    'Camera': {'connection': 'CSI', 'description': 'Pi Camera module'}
                },
                'features': ['Motion detection', 'Photo capture', 'SMS alerts']
            },
            'plant_monitor': {
                'name': 'Smart Plant Monitor',
                'difficulty': 4,
                'tier': '3-5',
                'components': ['DHT11', 'SoilMoisture', 'LDR', 'LED', 'Relay'],
                'assemblyTime': 30,
                'description': 'Monitor plant health with automatic watering',
                'wiring': {
                    'DHT11': {'pin': 17, 'description': 'Air temperature & humidity'},
                    'SoilMoisture': {'pin': 'A0', 'description': 'Soil moisture (via ADC)'},
                    'LDR': {'pin': 'A1', 'description': 'Light sensor'},
                    'Relay': {'pin': 22, 'description': 'Water pump control'}
                },
                'features': ['Soil monitoring', 'Auto watering', 'Growth tracking']
            }
        }
    
    def estimate_assembly_time(self, components: List[str]) -> int:
        """Estimate assembly time based on component complexity"""
        if self.assembly_commands:
            return self.assembly_commands.estimate_assembly_time(components)
        
        # Fallback estimation
        base_time = 10
        component_times = {
            'LED': 2, 'Button': 2, 'DHT11': 5, 'BMP180': 8, 'PIR': 3,
            'LCD1602': 15, 'Camera': 8, 'Buzzer': 2, 'Relay': 5
        }
        
        total_time = base_time
        for component in components:
            total_time += component_times.get(component, 5)
        
        return total_time
    
    def generate_assembly_guide(self, template: Dict) -> List[str]:
        """Generate step-by-step assembly guide"""
        guide = [
            f"Building {template['name']}",
            f"Estimated time: {template['assemblyTime']} minutes",
            "",
            "Assembly Steps:"
        ]
        
        step = 1
        for component, wiring in template['wiring'].items():
            if 'pin' in wiring:
                guide.append(f"{step}. Connect {component} to GPIO {wiring['pin']} - {wiring['description']}")
            elif 'pins' in wiring:
                guide.append(f"{step}. Connect {component} to GPIO pins {', '.join(map(str, wiring['pins']))} - {wiring['description']}")
            else:
                guide.append(f"{step}. Connect {component} - {wiring['description']}")
            step += 1
        
        guide.extend([
            "",
            "Safety checks:",
            "• Verify all connections are secure",
            "• Check power supply compatibility", 
            "• Test basic functionality before full deployment"
        ])
        
        return guide
    
    def generate_project_code(self, template_id: str) -> str:
        """Generate project code from template"""
        if self.assembly_commands:
            return self.assembly_commands.generate_project_code(template_id)
        
        # Fallback code generation
        template = self.project_templates.get(template_id, {})
        return f"""# {template.get('name', 'Project')} - Auto-generated code
import time
import RPi.GPIO as GPIO
from gpiozero import *

# Component initialization
print("Starting {template.get('name', 'project')}...")

def main():
    try:
        while True:
            # Main project loop
            print("Project running...")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Project stopped")
        GPIO.cleanup()

if __name__ == "__main__":
    main()
"""
    
    def generate_breadboard_layout(self, template: Dict) -> Dict:
        """Generate breadboard layout for project"""
        layout = {
            'components': {},
            'connections': [],
            'power_requirements': {},
            'pin_assignments': {}
        }
        
        for component, wiring in template['wiring'].items():
            layout['components'][component] = {
                'type': component,
                'description': wiring['description']
            }
            
            if 'pin' in wiring:
                layout['pin_assignments'][wiring['pin']] = component
                layout['connections'].append({
                    'from': component,
                    'to': f"GPIO {wiring['pin']}",
                    'type': 'digital'
                })
            elif 'pins' in wiring:
                for pin in wiring['pins']:
                    layout['pin_assignments'][pin] = component
                    layout['connections'].append({
                        'from': component,
                        'to': f"GPIO {pin}",
                        'type': 'i2c' if component == 'BMP180' else 'digital'
                    })
        
        return layout
    
    def generate_component_recommendations(self, current_components: List[str], project_type: str) -> List[Dict]:
        """Generate smart component recommendations"""
        recommendations = []
        
        # Define component synergies
        synergies = {
            'DHT11': ['LCD1602', 'LED', 'Buzzer'],  # Temperature display and alerts
            'PIR': ['Camera', 'Buzzer', 'LED'],     # Security system
            'BMP180': ['DHT11', 'LCD1602'],         # Weather station
            'Camera': ['PIR', 'LED', 'Buzzer'],     # Security/monitoring
            'Relay': ['SoilMoisture', 'DHT11']      # Automation
        }
        
        for component in current_components:
            if component in synergies:
                for synergy_comp in synergies[component]:
                    if synergy_comp not in current_components:
                        recommendations.append({
                            'component': synergy_comp,
                            'reason': f'Works well with {component}',
                            'compatibility': 'high',
                            'estimated_time': 10
                        })
        
        # Remove duplicates and limit results
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec['component'] not in seen:
                seen.add(rec['component'])
                unique_recommendations.append(rec)
        
        return unique_recommendations[:5]
    
    def get_time_breakdown(self, components: List[str]) -> Dict:
        """Get detailed time breakdown for components"""
        breakdown = {
            'setup': 10,
            'components': {},
            'testing': 5,
            'total': 15
        }
        
        component_times = {
            'LED': 2, 'Button': 2, 'DHT11': 5, 'BMP180': 8, 'PIR': 3,
            'LCD1602': 15, 'Camera': 8, 'Buzzer': 2, 'Relay': 5
        }
        
        for component in components:
            time_required = component_times.get(component, 5)
            breakdown['components'][component] = time_required
            breakdown['total'] += time_required
        
        return breakdown

# Global dashboard instance
dashboard = IntelligentDashboard()

# Flask routes
@app.route('/')
def index():
    """Main dashboard interface"""
    return render_template('dashboard.html', 
                         config=dashboard.get_dashboard_config())

@app.route('/api/dashboard/config')
def get_dashboard_config():
    """Get dashboard configuration"""
    return jsonify(dashboard.get_dashboard_config())

@app.route('/api/sensors/status')
def get_sensors_status():
    """Get current sensor status"""
    if dashboard.auto_config:
        return jsonify(dashboard.auto_config.get_system_status())
    else:
        return jsonify({'error': 'Auto-configuration not available'})

@app.route('/api/sensors/<sensor_name>/data')
def get_sensor_data(sensor_name):
    """Get historical data for specific sensor"""
    if sensor_name in dashboard.live_data:
        return jsonify(dashboard.live_data[sensor_name])
    else:
        return jsonify({'error': 'Sensor not found'}), 404

@app.route('/api/actuators/<actuator_name>/control', methods=['POST'])
def control_actuator(actuator_name):
    """Control actuator device"""
    data = request.json
    
    try:
        # Send control command to auto-config system
        if dashboard.auto_config:
            # Implementation would depend on actuator control interface
            logger.info(f"🎛️ Controlling {actuator_name}: {data}")
            return jsonify({'success': True, 'message': f'Control sent to {actuator_name}'})
        else:
            return jsonify({'error': 'Auto-configuration not available'}), 503
            
    except Exception as e:
        logger.error(f"Actuator control error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/breadboard/layout')
def get_breadboard_layout():
    """Get current breadboard layout with live component status"""
    if dashboard.auto_config:
        status = dashboard.auto_config.get_system_status()
        
        # Generate breadboard layout
        layout = {
            'gpio_pins': {},
            'i2c_devices': status.get('i2c_devices', {}),
            'detected_components': status.get('detected_components', {}),
            'live_status': {}
        }
        
        # Add GPIO pin status
        for pin in range(2, 28):
            layout['gpio_pins'][pin] = {
                'occupied': False,
                'component': None,
                'signal_type': 'unused',
                'live_value': None
            }
        
        # Mark occupied pins
        for component_name, component_data in status.get('detected_components', {}).items():
            pin = component_data.get('pin')
            if isinstance(pin, int) and 2 <= pin <= 27:
                layout['gpio_pins'][pin] = {
                    'occupied': True,
                    'component': component_name,
                    'signal_type': component_data.get('component_type', 'unknown'),
                    'live_value': dashboard.live_data.get(component_name, {}).get('readings', [{}])[-1:][0] if dashboard.live_data.get(component_name, {}).get('readings') else None
                }
        
        return jsonify(layout)
    else:
        return jsonify({'error': 'Auto-configuration not available'}), 503

# Enhanced API endpoints for rapid prototyping
@app.route('/api/projects/templates')
def get_project_templates():
    """Get available project templates"""
    return jsonify(dashboard.project_templates)

@app.route('/api/projects/generate', methods=['POST'])
def generate_project():
    """Generate a complete project from template"""
    data = request.json
    template_id = data.get('template_id')
    difficulty_filter = data.get('difficulty_filter', 'all')
    
    if template_id not in dashboard.project_templates:
        return jsonify({'error': 'Project template not found'}), 404
    
    template = dashboard.project_templates[template_id]
    
    # Generate project with optimized component selection
    project_data = {
        'template_id': template_id,
        'name': template['name'],
        'components': template['components'],
        'wiring': template['wiring'],
        'estimated_time': dashboard.estimate_assembly_time(template['components']),
        'assembly_guide': dashboard.generate_assembly_guide(template),
        'code': dashboard.generate_project_code(template_id),
        'breadboard_layout': dashboard.generate_breadboard_layout(template)
    }
    
    # Store active project
    dashboard.active_projects[template_id] = {
        'data': project_data,
        'start_time': time.time(),
        'status': 'in_progress'
    }
    
    return jsonify(project_data)

@app.route('/api/projects/<project_id>/code')
def get_project_code(project_id):
    """Get generated code for a project"""
    if project_id not in dashboard.project_templates:
        return jsonify({'error': 'Project not found'}), 404
    
    code = dashboard.generate_project_code(project_id)
    return jsonify({'project_id': project_id, 'code': code})

@app.route('/api/projects/<project_id>/deploy', methods=['POST'])
def deploy_project_code(project_id):
    """Deploy project code to Raspberry Pi"""
    if project_id not in dashboard.project_templates:
        return jsonify({'error': 'Project not found'}), 404
    
    # Simulate code deployment
    try:
        template = dashboard.project_templates[project_id]
        code = dashboard.generate_project_code(project_id)
        
        # In real implementation, this would:
        # 1. Transfer code to Pi via SSH/SCP
        # 2. Install dependencies
        # 3. Start the service
        
        deployment_result = {
            'project_id': project_id,
            'status': 'deployed',
            'message': f'{template["name"]} deployed successfully',
            'timestamp': time.time()
        }
        
        return jsonify(deployment_result)
        
    except Exception as e:
        return jsonify({'error': f'Deployment failed: {str(e)}'}), 500

@app.route('/api/learning/recommendations')
def get_learning_recommendations():
    """Get personalized project recommendations"""
    # Get user progress from request or stored analytics
    user_tier = request.args.get('tier', 1, type=int)
    completed_projects = request.args.getlist('completed')
    
    if dashboard.assembly_commands:
        recommendations = dashboard.assembly_commands.get_next_recommended_projects(
            user_tier, completed_projects
        )
        return jsonify(recommendations)
    else:
        # Fallback recommendations
        fallback = [
            {'project_id': 'iot_weather_station', 'name': 'IoT Weather Station', 'difficulty': 5},
            {'project_id': 'plant_monitor', 'name': 'Plant Monitor', 'difficulty': 4}
        ]
        return jsonify(fallback)

@app.route('/api/learning/analytics', methods=['POST'])
def update_learning_analytics():
    """Update user learning analytics"""
    data = request.json
    user_id = data.get('user_id', 'default')
    
    analytics_update = {
        'completed_projects': data.get('completed_projects', []),
        'used_components': data.get('used_components', []),
        'current_tier': data.get('current_tier', 1),
        'total_assembly_time': data.get('total_assembly_time', 0)
    }
    
    dashboard.learning_analytics[user_id] = analytics_update
    
    # Generate insights
    if dashboard.assembly_commands:
        insights = dashboard.assembly_commands.analyze_learning_pattern(analytics_update)
        return jsonify({'status': 'updated', 'insights': insights})
    else:
        return jsonify({'status': 'updated', 'insights': {}})

@app.route('/api/components/recommendations')
def get_component_recommendations():
    """Get smart component recommendations"""
    current_components = request.args.getlist('current')
    project_type = request.args.get('type', 'general')
    
    # Generate recommendations based on compatibility and learning progression
    recommendations = dashboard.generate_component_recommendations(current_components, project_type)
    
    return jsonify(recommendations)

@app.route('/api/assembly/estimate', methods=['POST'])
def estimate_assembly_time():
    """Estimate assembly time for component list"""
    data = request.json
    components = data.get('components', [])
    
    if dashboard.assembly_commands:
        estimated_time = dashboard.assembly_commands.estimate_assembly_time(components)
    else:
        # Fallback estimation
        estimated_time = len(components) * 5 + 10  # 5 min per component + 10 min setup
    
    return jsonify({
        'components': components,
        'estimated_time': estimated_time,
        'breakdown': dashboard.get_time_breakdown(components)
    })

# WebSocket events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    dashboard.client_connections.add(request.sid)
    logger.info(f"📱 Client connected: {request.sid}")
    
    # Send initial configuration
    emit('dashboard_config', dashboard.get_dashboard_config())

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    dashboard.client_connections.discard(request.sid)
    logger.info(f"📱 Client disconnected: {request.sid}")

@socketio.on('request_historical_data')
def handle_historical_data_request(data):
    """Handle request for historical sensor data"""
    sensor_name = data.get('sensor_name')
    time_range = data.get('time_range', 3600)  # Default 1 hour
    
    if sensor_name in dashboard.live_data:
        current_time = time.time()
        cutoff_time = current_time - time_range
        
        filtered_readings = [
            reading for reading in dashboard.live_data[sensor_name]['readings']
            if reading['timestamp'] >= cutoff_time
        ]
        
        emit('historical_data', {
            'sensor_name': sensor_name,
            'readings': filtered_readings
        })

@socketio.on('actuator_control')
def handle_actuator_control(data):
    """Handle actuator control via WebSocket"""
    actuator_name = data.get('actuator_name')
    control_data = data.get('control_data')
    
    logger.info(f"🎛️ WebSocket actuator control: {actuator_name} -> {control_data}")
    
    # Send control command
    # Implementation would interface with actual hardware
    
    emit('actuator_response', {
        'actuator_name': actuator_name,
        'status': 'success',
        'message': 'Control applied'
    })

if __name__ == '__main__':
    logger.info("🌐 Starting Intelligent Web Dashboard")
    logger.info("📊 Dashboard available at: http://localhost:5001")
    
    try:
        socketio.run(app, host='0.0.0.0', port=5001, debug=False)
    except KeyboardInterrupt:
        logger.info("👋 Dashboard shutting down")
        dashboard.streaming_active = False