#!/usr/bin/env python3
"""
Advanced Assembly Commands System
Live Data System for Raspberry Pi

This system leverages comprehensive analysis for:
- Component database + code mapping integration
- Compatibility matrices + optimal pin assignment
- Auto-detection + conflict resolution debugging
- 8-tier complexity analysis for layout optimization
"""

import re
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from smart_code_completion import SmartCodeCompletion
    from smart_pi_autoconfig import SmartPiAutoConfig
except ImportError:
    print("⚠️ Analysis modules not found")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AssemblyGuide:
    component: str
    wiring_steps: List[str]
    pin_assignments: Dict[str, int]
    code_example: str
    warnings: List[str]
    compatibility_notes: List[str]

@dataclass
class OptimizationSuggestion:
    type: str  # 'pin_assignment', 'layout', 'performance', 'safety'
    priority: str  # 'high', 'medium', 'low'
    description: str
    implementation: str
    impact: str

class AdvancedAssemblyCommands:
    """Advanced assembly command processor using comprehensive analysis"""
    
    def __init__(self, component_db=None, auto_config=None):
        self.component_db = component_db or self.load_component_database()
        self.auto_config = auto_config
        self.code_completion = SmartCodeCompletion()
        
        # Command patterns
        self.command_patterns = self.build_command_patterns()
        self.component_library = self.build_component_library()
        self.compatibility_matrix = self.build_compatibility_matrix()
        self.optimization_rules = self.build_optimization_rules()
        
        # Enhanced features for rapid prototyping
        self.project_templates = self.load_project_templates()
        self.learning_analytics = self.initialize_learning_analytics()
        
    def load_component_database(self) -> Dict:
        """Load comprehensive component database"""
        try:
            db_path = Path(__file__).parent.parent / 'component_code_mapping.json'
            if db_path.exists():
                with open(db_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load component database: {e}")
        
        # Enhanced fallback with assembly specifications
        return {
            "component_mapping": {
                "LED": {
                    "complexity": 1,
                    "pins_used": ["GPIO17"],
                    "assembly": {
                        "wiring": [
                            "Connect LED positive (longer leg) to GPIO pin via 220Ω resistor",
                            "Connect LED negative (shorter leg) to GND",
                            "Verify resistor value for 3.3V operation"
                        ],
                        "optimal_pins": [17, 18, 27, 22],
                        "warnings": ["Always use current limiting resistor", "Check LED forward voltage"],
                        "code_pattern": "led = LED(pin)\nled.on()\nled.off()"
                    }
                },
                "DHT11": {
                    "complexity": 3,
                    "pins_used": ["GPIO17"],
                    "i2c_address": None,
                    "assembly": {
                        "wiring": [
                            "Connect VCC to 3.3V power rail",
                            "Connect GND to ground rail", 
                            "Connect DATA to GPIO pin",
                            "Add 4.7kΩ pull-up resistor between DATA and VCC"
                        ],
                        "optimal_pins": [17, 4, 18],
                        "warnings": ["Requires pull-up resistor", "Sensitive to timing"],
                        "code_pattern": "dht = DHT(pin)\nresult = dht.readDHT11()\ntemp = dht.getTemperature()"
                    }
                },
                "BMP180": {
                    "complexity": 4,
                    "pins_used": ["GPIO2", "GPIO3"],
                    "i2c_address": "0x77",
                    "assembly": {
                        "wiring": [
                            "Connect VCC to 3.3V (Pin 1)",
                            "Connect GND to Ground (Pin 6)",
                            "Connect SDA to GPIO 2 (Pin 3) - I2C Data",
                            "Connect SCL to GPIO 3 (Pin 5) - I2C Clock"
                        ],
                        "optimal_pins": [2, 3],  # Fixed for I2C
                        "warnings": ["Enable I2C in raspi-config", "Check I2C address conflicts"],
                        "code_pattern": "import smbus\nbus = smbus.SMBus(1)\n# BMP180 communication"
                    }
                },
                "Ultrasonic_HC_SR04": {
                    "complexity": 3,
                    "pins_used": ["GPIO20", "GPIO21"],
                    "assembly": {
                        "wiring": [
                            "Connect VCC to 5V power rail",
                            "Connect GND to ground rail",
                            "Connect TRIG to GPIO pin (direct connection)",
                            "Connect ECHO to GPIO pin via voltage divider (5V to 3.3V)"
                        ],
                        "optimal_pins": [20, 21, 23, 24],
                        "warnings": ["ECHO pin needs voltage divider", "Requires 5V power"],
                        "code_pattern": "sensor = DistanceSensor(echo=21, trigger=20)\ndistance = sensor.distance"
                    }
                },
                "Servo": {
                    "complexity": 3,
                    "pins_used": ["GPIO17"],
                    "assembly": {
                        "wiring": [
                            "Connect red wire to 5V power (external recommended)",
                            "Connect brown/black wire to GND",
                            "Connect orange/yellow wire to GPIO pin"
                        ],
                        "optimal_pins": [17, 18, 27],
                        "warnings": ["May require external power", "Check servo voltage"],
                        "code_pattern": "servo = Servo(pin)\nservo.min()\nservo.max()\nservo.mid()"
                    }
                },
                "Motor_DC": {
                    "complexity": 4,
                    "pins_used": ["GPIO18", "GPIO19"],
                    "assembly": {
                        "wiring": [
                            "Connect motor driver VCC to 5V external power",
                            "Connect motor driver GND to common ground",
                            "Connect IN1 to GPIO pin (forward control)",
                            "Connect IN2 to GPIO pin (backward control)",
                            "Connect motor terminals to OUT1 and OUT2"
                        ],
                        "optimal_pins": [18, 19, 20, 21],
                        "warnings": ["Requires motor driver IC", "External power needed", "Check current limits"],
                        "code_pattern": "motor = Motor(forward=18, backward=19)\nmotor.forward(0.5)\nmotor.stop()"
                    }
                },
                "RGBLED": {
                    "complexity": 2,
                    "pins_used": ["GPIO17", "GPIO18", "GPIO27"],
                    "assembly": {
                        "wiring": [
                            "Connect RED pin to GPIO via 220Ω resistor",
                            "Connect GREEN pin to GPIO via 220Ω resistor",
                            "Connect BLUE pin to GPIO via 220Ω resistor",
                            "Connect common cathode to GND (or anode to 3.3V)"
                        ],
                        "optimal_pins": [17, 18, 27],
                        "warnings": ["Check common cathode vs anode", "Use appropriate resistors"],
                        "code_pattern": "led = RGBLED(red=17, green=18, blue=27)\nled.color = (1, 0, 0)  # Red"
                    }
                },
                "Matrix_8x8": {
                    "complexity": 5,
                    "pins_used": ["GPIO18", "GPIO8", "GPIO11"],
                    "assembly": {
                        "wiring": [
                            "Connect VCC to 5V power",
                            "Connect GND to ground",
                            "Connect DIN to GPIO 18 (SPI MOSI)",
                            "Connect CS to GPIO 8 (SPI CE0)",
                            "Connect CLK to GPIO 11 (SPI CLK)"
                        ],
                        "optimal_pins": [18, 8, 11],  # Hardware SPI
                        "warnings": ["Enable SPI in raspi-config", "Requires SPI library"],
                        "code_pattern": "# Use SPI for LED matrix control\nimport spidev\nspi = spidev.SpiDev()"
                    }
                }
            }
        }
    
    def build_command_patterns(self) -> Dict:
        """Build command pattern recognition"""
        return {
            "show": {
                "keywords": ["show", "display", "guide", "how"],
                "targets": ["setup", "wiring", "connection", "pins"],
                "handler": self.handle_show_command
            },
            "add": {
                "keywords": ["add", "connect", "install", "attach"],
                "targets": ["sensor", "component", "device"],
                "handler": self.handle_add_command
            },
            "debug": {
                "keywords": ["debug", "check", "test", "diagnose"],
                "targets": ["connections", "pins", "wiring", "signals"],
                "handler": self.handle_debug_command
            },
            "optimize": {
                "keywords": ["optimize", "improve", "layout", "arrange"],
                "targets": ["layout", "pins", "performance", "wiring"],
                "handler": self.handle_optimize_command
            },
            "list": {
                "keywords": ["list", "show all", "available"],
                "targets": ["components", "sensors", "devices"],
                "handler": self.handle_list_command
            },
            "remove": {
                "keywords": ["remove", "disconnect", "delete"],
                "targets": ["component", "sensor", "device"],
                "handler": self.handle_remove_command
            }
        }
    
    def build_component_library(self) -> Dict:
        """Build enhanced component library with assembly data"""
        library = {}
        
        for component_name, component_data in self.component_db.get('component_mapping', {}).items():
            library[component_name.lower()] = {
                'name': component_name,
                'complexity': component_data.get('complexity', 1),
                'assembly': component_data.get('assembly', {}),
                'category': self.categorize_component(component_name),
                'aliases': self.get_component_aliases(component_name)
            }
        
        return library
    
    def categorize_component(self, component_name: str) -> str:
        """Categorize component based on analysis"""
        sensors = ['DHT', 'BMP', 'PIR', 'Ultrasonic', 'Pressure', 'Temperature', 'Humidity']
        actuators = ['LED', 'Motor', 'Servo', 'Buzzer', 'Relay']
        displays = ['LCD', 'Matrix', 'OLED', 'Seven']
        communication = ['RFID', 'WiFi', 'Bluetooth', 'Radio']
        
        name_upper = component_name.upper()
        
        if any(sensor in name_upper for sensor in sensors):
            return 'sensor'
        elif any(actuator in name_upper for actuator in actuators):
            return 'actuator'
        elif any(display in name_upper for display in displays):
            return 'display'
        elif any(comm in name_upper for comm in communication):
            return 'communication'
        else:
            return 'other'
    
    def get_component_aliases(self, component_name: str) -> List[str]:
        """Get alternative names for component"""
        aliases = {
            'DHT11': ['temperature sensor', 'humidity sensor', 'temp sensor'],
            'BMP180': ['pressure sensor', 'barometer', 'atmospheric sensor'],
            'PIR_Sensor': ['motion sensor', 'pir', 'movement detector'],
            'Ultrasonic_HC_SR04': ['distance sensor', 'ultrasonic', 'sonar', 'hc-sr04'],
            'LED': ['light', 'diode', 'indicator'],
            'RGBLED': ['rgb', 'color led', 'multicolor led'],
            'Motor_DC': ['motor', 'dc motor', 'drive motor'],
            'Servo': ['servo motor', 'position motor'],
            'LCD1602': ['lcd', 'display', 'screen'],
            'Matrix_8x8': ['led matrix', 'dot matrix', '8x8 matrix']
        }
        
        return aliases.get(component_name, [])
    
    def build_compatibility_matrix(self) -> Dict:
        """Build component compatibility matrix from analysis"""
        return {
            'pin_conflicts': {
                'I2C': [2, 3],  # Reserved for I2C
                'SPI': [8, 9, 10, 11],  # Hardware SPI pins
                'UART': [14, 15],  # Serial communication
                '1Wire': [4]  # 1-Wire temperature sensors
            },
            'voltage_levels': {
                '3.3V': ['DHT11', 'BMP180', 'Most_GPIO'],
                '5V': ['Ultrasonic_HC_SR04', 'Some_Servos', 'Motor_Drivers']
            },
            'communication_protocols': {
                'I2C': ['BMP180', 'LCD1602', 'OLED', 'ADS1115'],
                'SPI': ['Matrix_8x8', 'RFID_MFRC522', 'Some_Displays'],
                'Digital': ['PIR_Sensor', 'Button', 'LED', 'Relay'],
                '1Wire': ['DS18B20', 'DHT22']
            },
            'good_combinations': [
                ['DHT11', 'LCD1602', 'LED'],  # Weather station
                ['PIR_Sensor', 'Buzzer', 'LED'],  # Alarm system
                ['Ultrasonic_HC_SR04', 'Servo', 'LED'],  # Distance-based control
                ['BMP180', 'OLED', 'Button']  # Barometer display
            ],
            'avoid_combinations': [
                ['Multiple_I2C_Same_Address'],  # Address conflicts
                ['High_Current_With_Sensors'],  # Noise issues
                ['Fast_Switching_Near_Analog']  # Signal integrity
            ]
        }
    
    def build_optimization_rules(self) -> List[Dict]:
        """Build optimization rules from 8-tier complexity analysis"""
        return [
            {
                'rule': 'group_i2c_devices',
                'priority': 'high',
                'description': 'Group I2C devices to minimize wire length',
                'condition': lambda components: len([c for c in components if 'i2c_address' in self.component_db.get('component_mapping', {}).get(c, {})]) > 1,
                'suggestion': 'Place I2C devices close together and use short wires'
            },
            {
                'rule': 'separate_power_domains',
                'priority': 'high', 
                'description': 'Separate 3.3V and 5V components',
                'condition': lambda components: self.has_mixed_voltage_levels(components),
                'suggestion': 'Use level shifters or separate power supplies for different voltage levels'
            },
            {
                'rule': 'use_hardware_peripherals',
                'priority': 'medium',
                'description': 'Use hardware SPI/I2C pins when available',
                'condition': lambda components: self.has_communication_devices(components),
                'suggestion': 'Use GPIO 2/3 for I2C and GPIO 8/9/10/11 for SPI'
            },
            {
                'rule': 'minimize_pin_conflicts',
                'priority': 'high',
                'description': 'Avoid pin assignment conflicts',
                'condition': lambda components: self.has_pin_conflicts(components),
                'suggestion': 'Reassign pins to avoid conflicts using optimal pin assignment'
            },
            {
                'rule': 'consider_complexity_progression',
                'priority': 'medium',
                'description': 'Progress from simple to complex components',
                'condition': lambda components: self.has_high_complexity_jump(components),
                'suggestion': 'Start with basic components before adding advanced ones'
            }
        ]
    
    def process_command(self, command: str) -> str:
        """Process natural language assembly command"""
        command = command.lower().strip()
        
        # Parse command intent
        intent = self.parse_command_intent(command)
        if not intent:
            return self.generate_help_response()
        
        # Execute command
        try:
            response = intent['handler'](command, intent)
            return response
        except Exception as e:
            logger.error(f"Command processing error: {e}")
            return f"Error processing command: {str(e)}"
    
    def parse_command_intent(self, command: str) -> Optional[Dict]:
        """Parse command to extract intent and parameters"""
        
        for command_type, pattern in self.command_patterns.items():
            if any(keyword in command for keyword in pattern['keywords']):
                
                # Extract component name
                component = self.extract_component_name(command)
                
                # Extract target/action
                target = None
                for target_word in pattern['targets']:
                    if target_word in command:
                        target = target_word
                        break
                
                return {
                    'type': command_type,
                    'component': component,
                    'target': target,
                    'handler': pattern['handler'],
                    'original_command': command
                }
        
        return None
    
    def extract_component_name(self, command: str) -> Optional[str]:
        """Extract component name from command using aliases"""
        
        # Direct component name matching
        for component_name, component_info in self.component_library.items():
            if component_name in command:
                return component_info['name']
            
            # Check aliases
            for alias in component_info['aliases']:
                if alias in command:
                    return component_info['name']
        
        # Pattern-based extraction
        component_patterns = [
            r'(dht\d+)', r'(bmp\d+)', r'(hc-sr\d+)', r'(ds18b20)',
            r'(led matrix)', r'(rgb led)', r'(servo motor)', r'(dc motor)'
        ]
        
        for pattern in component_patterns:
            match = re.search(pattern, command)
            if match:
                matched_text = match.group(1)
                # Map to actual component name
                return self.map_pattern_to_component(matched_text)
        
        return None
    
    def map_pattern_to_component(self, pattern: str) -> str:
        """Map extracted pattern to actual component name"""
        mapping = {
            'dht11': 'DHT11',
            'bmp180': 'BMP180',
            'hc-sr04': 'Ultrasonic_HC_SR04',
            'ds18b20': 'DS18B20',
            'led matrix': 'Matrix_8x8',
            'rgb led': 'RGBLED',
            'servo motor': 'Servo',
            'dc motor': 'Motor_DC'
        }
        
        return mapping.get(pattern, pattern.upper())
    
    def handle_show_command(self, command: str, intent: Dict) -> str:
        """Handle 'show' commands using component database"""
        component_name = intent.get('component')
        
        if not component_name:
            return "Please specify a component. Example: 'show LED setup' or 'show DHT11 wiring'"
        
        if component_name not in [comp['name'] for comp in self.component_library.values()]:
            return f"Component '{component_name}' not found. Use 'list components' to see available components."
        
        # Generate assembly guide
        guide = self.generate_assembly_guide(component_name)
        return self.format_assembly_guide(guide)
    
    def handle_add_command(self, command: str, intent: Dict) -> str:
        """Handle 'add' commands using compatibility matrices"""
        component_name = intent.get('component')
        
        if not component_name:
            return "Please specify a component to add. Example: 'add pressure sensor'"
        
        # Get current system state
        current_components = self.get_current_components()
        
        # Check compatibility
        compatibility_check = self.check_component_compatibility(component_name, current_components)
        
        if not compatibility_check['compatible']:
            return f"Cannot add {component_name}: {compatibility_check['reason']}"
        
        # Generate optimal pin assignment
        pin_assignment = self.get_optimal_pin_assignment(component_name, current_components)
        
        # Generate assembly guide
        guide = self.generate_assembly_guide(component_name, pin_assignment)
        
        response = f"✅ {component_name} can be added to your system.\n\n"
        response += self.format_assembly_guide(guide)
        
        if compatibility_check.get('warnings'):
            response += "\n⚠️ **Warnings:**\n"
            for warning in compatibility_check['warnings']:
                response += f"• {warning}\n"
        
        return response
    
    def handle_debug_command(self, command: str, intent: Dict) -> str:
        """Handle 'debug' commands using auto-detection + conflict resolution"""
        
        if not self.auto_config:
            return "Debug functionality requires auto-configuration system to be running."
        
        # Get system status
        system_status = self.auto_config.get_system_status()
        
        # Analyze detected components
        detected_components = system_status.get('detected_components', {})
        active_sensors = system_status.get('active_sensors', {})
        
        debug_report = "🔍 **System Debug Report**\n\n"
        
        # Component detection status
        debug_report += f"**Detected Components:** {len(detected_components)}\n"
        for name, component in detected_components.items():
            status = "🟢 Active" if name in active_sensors else "🟡 Detected but inactive"
            debug_report += f"• {name} (GPIO {component.get('pin', 'N/A')}) - {status}\n"
        
        # Pin conflict analysis
        conflicts = self.analyze_pin_conflicts(detected_components)
        if conflicts:
            debug_report += "\n**⚠️ Pin Conflicts Detected:**\n"
            for conflict in conflicts:
                debug_report += f"• {conflict}\n"
        else:
            debug_report += "\n**✅ No pin conflicts detected**\n"
        
        # Signal integrity analysis
        signal_issues = self.analyze_signal_integrity(detected_components)
        if signal_issues:
            debug_report += "\n**📡 Signal Issues:**\n"
            for issue in signal_issues:
                debug_report += f"• {issue}\n"
        
        # Recommendations
        recommendations = self.generate_debug_recommendations(system_status)
        if recommendations:
            debug_report += "\n**💡 Recommendations:**\n"
            for rec in recommendations:
                debug_report += f"• {rec}\n"
        
        return debug_report
    
    def handle_optimize_command(self, command: str, intent: Dict) -> str:
        """Handle 'optimize' commands using 8-tier complexity analysis"""
        
        # Get current components
        current_components = self.get_current_components()
        
        if not current_components:
            return "No components detected. Add some components first to get optimization suggestions."
        
        # Analyze current layout
        optimization_suggestions = self.analyze_layout_optimization(current_components)
        
        response = "🚀 **Layout Optimization Analysis**\n\n"
        
        # Complexity analysis
        total_complexity = sum(self.get_component_complexity(comp) for comp in current_components)
        complexity_level = self.get_complexity_level(total_complexity)
        
        response += f"**Current Complexity:** Level {complexity_level} (Score: {total_complexity})\n"
        response += f"**Component Count:** {len(current_components)}\n\n"
        
        # Optimization suggestions
        if optimization_suggestions:
            response += "**Optimization Suggestions:**\n"
            for suggestion in optimization_suggestions:
                priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}[suggestion.priority]
                response += f"{priority_icon} **{suggestion.type.title()}:** {suggestion.description}\n"
                response += f"   Implementation: {suggestion.implementation}\n"
                response += f"   Impact: {suggestion.impact}\n\n"
        else:
            response += "**✅ Current layout is well optimized!**\n"
        
        # Pin usage optimization
        pin_optimization = self.optimize_pin_usage(current_components)
        if pin_optimization:
            response += "**📍 Pin Usage Optimization:**\n"
            for opt in pin_optimization:
                response += f"• {opt}\n"
        
        return response
    
    def handle_list_command(self, command: str, intent: Dict) -> str:
        """Handle 'list' commands"""
        
        if 'components' in command:
            return self.list_available_components()
        elif 'active' in command or 'connected' in command:
            return self.list_active_components()
        else:
            return self.list_available_components()
    
    def handle_remove_command(self, command: str, intent: Dict) -> str:
        """Handle 'remove' commands"""
        component_name = intent.get('component')
        
        if not component_name:
            return "Please specify a component to remove. Example: 'remove DHT11'"
        
        # Check if component is currently active
        current_components = self.get_current_components()
        
        if component_name not in current_components:
            return f"Component '{component_name}' is not currently connected."
        
        # Generate removal guide
        response = f"🔧 **Removing {component_name}**\n\n"
        response += "**Steps:**\n"
        response += "1. Power off Raspberry Pi\n"
        response += "2. Disconnect all wires from the component\n"
        response += "3. Remove component from breadboard\n"
        response += "4. Update your code to remove component references\n\n"
        
        # Check impact on other components
        impact = self.analyze_removal_impact(component_name, current_components)
        if impact:
            response += "**⚠️ Impact on other components:**\n"
            for imp in impact:
                response += f"• {imp}\n"
        
        return response
    
    def generate_assembly_guide(self, component_name: str, pin_assignment: Dict = None) -> AssemblyGuide:
        """Generate comprehensive assembly guide using component database"""
        
        component_data = self.component_db.get('component_mapping', {}).get(component_name, {})
        assembly_data = component_data.get('assembly', {})
        
        # Get optimal pin assignment
        if not pin_assignment:
            pin_assignment = self.get_optimal_pin_assignment(component_name, [])
        
        # Generate wiring steps with actual pin numbers
        wiring_steps = []
        for step in assembly_data.get('wiring', []):
            # Replace generic "GPIO pin" with actual pin numbers
            if 'GPIO pin' in step and pin_assignment:
                actual_pin = list(pin_assignment.values())[0] if pin_assignment else 17
                step = step.replace('GPIO pin', f'GPIO {actual_pin}')
            wiring_steps.append(step)
        
        # Generate code example
        code_pattern = assembly_data.get('code_pattern', '')
        code_example = self.customize_code_pattern(code_pattern, pin_assignment)
        
        # Get compatibility notes
        compatibility_notes = self.get_compatibility_notes(component_name)
        
        return AssemblyGuide(
            component=component_name,
            wiring_steps=wiring_steps,
            pin_assignments=pin_assignment,
            code_example=code_example,
            warnings=assembly_data.get('warnings', []),
            compatibility_notes=compatibility_notes
        )
    
    def format_assembly_guide(self, guide: AssemblyGuide) -> str:
        """Format assembly guide for display"""
        
        response = f"🔧 **{guide.component} Assembly Guide**\n\n"
        
        # Pin assignments
        if guide.pin_assignments:
            response += "**📍 Pin Assignments:**\n"
            for signal, pin in guide.pin_assignments.items():
                response += f"• {signal}: GPIO {pin}\n"
            response += "\n"
        
        # Wiring steps
        response += "**🔌 Wiring Steps:**\n"
        for i, step in enumerate(guide.wiring_steps, 1):
            response += f"{i}. {step}\n"
        response += "\n"
        
        # Code example
        if guide.code_example:
            response += "**💻 Code Example:**\n"
            response += f"```python\n{guide.code_example}\n```\n\n"
        
        # Warnings
        if guide.warnings:
            response += "**⚠️ Warnings:**\n"
            for warning in guide.warnings:
                response += f"• {warning}\n"
            response += "\n"
        
        # Compatibility notes
        if guide.compatibility_notes:
            response += "**🔗 Compatibility Notes:**\n"
            for note in guide.compatibility_notes:
                response += f"• {note}\n"
        
        return response
    
    def get_optimal_pin_assignment(self, component_name: str, current_components: List[str]) -> Dict[str, int]:
        """Get optimal pin assignment using smart code completion"""
        
        # Get currently used pins
        used_pins = set()
        for comp in current_components:
            comp_data = self.component_db.get('component_mapping', {}).get(comp, {})
            pins = comp_data.get('pins_used', [])
            for pin_str in pins:
                if pin_str.startswith('GPIO'):
                    pin_num = int(pin_str.replace('GPIO', ''))
                    used_pins.add(pin_num)
        
        # Get optimal pins for new component
        component_data = self.component_db.get('component_mapping', {}).get(component_name, {})
        assembly_data = component_data.get('assembly', {})
        optimal_pins = assembly_data.get('optimal_pins', [17])
        
        # Special handling for different component types
        if 'i2c_address' in component_data:
            # I2C component - use fixed pins
            return {'SDA': 2, 'SCL': 3}
        elif component_name == 'Matrix_8x8':
            # SPI component - use hardware SPI pins
            return {'DIN': 18, 'CS': 8, 'CLK': 11}
        elif component_name == 'Ultrasonic_HC_SR04':
            # Dual pin component
            available_pins = [p for p in optimal_pins if p not in used_pins]
            if len(available_pins) >= 2:
                return {'TRIG': available_pins[0], 'ECHO': available_pins[1]}
            else:
                return {'TRIG': 20, 'ECHO': 21}  # Fallback
        elif component_name == 'RGBLED':
            # Three pin component
            available_pins = [p for p in optimal_pins if p not in used_pins]
            if len(available_pins) >= 3:
                return {'RED': available_pins[0], 'GREEN': available_pins[1], 'BLUE': available_pins[2]}
            else:
                return {'RED': 17, 'GREEN': 18, 'BLUE': 27}  # Fallback
        else:
            # Single pin component
            for pin in optimal_pins:
                if pin not in used_pins:
                    return {'pin': pin}
            return {'pin': optimal_pins[0]}  # Fallback to first option
    
    def check_component_compatibility(self, component_name: str, current_components: List[str]) -> Dict:
        """Check component compatibility using compatibility matrices"""
        
        result = {'compatible': True, 'reason': '', 'warnings': []}
        
        # Check for I2C address conflicts
        component_data = self.component_db.get('component_mapping', {}).get(component_name, {})
        new_i2c_addr = component_data.get('i2c_address')
        
        if new_i2c_addr:
            for existing_comp in current_components:
                existing_data = self.component_db.get('component_mapping', {}).get(existing_comp, {})
                existing_i2c_addr = existing_data.get('i2c_address')
                
                if existing_i2c_addr == new_i2c_addr:
                    result['compatible'] = False
                    result['reason'] = f"I2C address conflict with {existing_comp} (both use {new_i2c_addr})"
                    return result
        
        # Check voltage level compatibility
        new_voltage = self.get_component_voltage(component_name)
        mixed_voltages = any(self.get_component_voltage(comp) != new_voltage for comp in current_components)
        
        if mixed_voltages:
            result['warnings'].append(f"Mixed voltage levels detected - ensure proper level shifting")
        
        # Check pin availability
        required_pins = self.get_required_pin_count(component_name)
        available_pins = self.count_available_pins(current_components)
        
        if required_pins > available_pins:
            result['compatible'] = False
            result['reason'] = f"Insufficient available pins (need {required_pins}, have {available_pins})"
            return result
        
        # Check complexity progression
        new_complexity = self.get_component_complexity(component_name)
        max_current_complexity = max([self.get_component_complexity(comp) for comp in current_components] + [0])
        
        if new_complexity > max_current_complexity + 2:
            result['warnings'].append(f"Large complexity jump - consider intermediate components first")
        
        return result
    
    def get_current_components(self) -> List[str]:
        """Get currently connected components"""
        if self.auto_config:
            status = self.auto_config.get_system_status()
            return list(status.get('detected_components', {}).keys())
        else:
            # Fallback for simulation
            return []
    
    def analyze_pin_conflicts(self, detected_components: Dict) -> List[str]:
        """Analyze pin conflicts in current setup"""
        conflicts = []
        pin_usage = {}
        
        for comp_name, comp_data in detected_components.items():
            pin = comp_data.get('pin')
            if pin:
                if pin in pin_usage:
                    conflicts.append(f"Pin conflict: GPIO {pin} used by {pin_usage[pin]} and {comp_name}")
                else:
                    pin_usage[pin] = comp_name
        
        return conflicts
    
    def analyze_signal_integrity(self, detected_components: Dict) -> List[str]:
        """Analyze signal integrity issues"""
        issues = []
        
        # Check for mixed voltage levels
        voltage_3v3 = []
        voltage_5v = []
        
        for comp_name in detected_components.keys():
            voltage = self.get_component_voltage(comp_name)
            if voltage == '3.3V':
                voltage_3v3.append(comp_name)
            elif voltage == '5V':
                voltage_5v.append(comp_name)
        
        if voltage_3v3 and voltage_5v:
            issues.append("Mixed voltage levels detected - check level shifting requirements")
        
        # Check for high-speed signals near analog
        # This would require more detailed analysis of pin usage
        
        return issues
    
    def generate_debug_recommendations(self, system_status: Dict) -> List[str]:
        """Generate debug recommendations"""
        recommendations = []
        
        detected_count = len(system_status.get('detected_components', {}))
        active_count = len(system_status.get('active_sensors', {}))
        
        if detected_count > active_count:
            recommendations.append("Some detected components are not active - check initialization")
        
        if detected_count == 0:
            recommendations.append("No components detected - check connections and power")
        
        # Add more sophisticated recommendations based on analysis
        
        return recommendations
    
    def analyze_layout_optimization(self, current_components: List[str]) -> List[OptimizationSuggestion]:
        """Analyze layout for optimization opportunities"""
        suggestions = []
        
        # Check optimization rules
        for rule in self.optimization_rules:
            if rule['condition'](current_components):
                suggestions.append(OptimizationSuggestion(
                    type=rule['rule'],
                    priority=rule['priority'],
                    description=rule['description'],
                    implementation=rule['suggestion'],
                    impact="Improved reliability and performance"
                ))
        
        return suggestions
    
    def get_component_complexity(self, component_name: str) -> int:
        """Get component complexity from database"""
        component_data = self.component_db.get('component_mapping', {}).get(component_name, {})
        return component_data.get('complexity', 1)
    
    def get_complexity_level(self, total_complexity: int) -> int:
        """Convert total complexity to tier level (1-8)"""
        if total_complexity <= 3:
            return 1
        elif total_complexity <= 6:
            return 2
        elif total_complexity <= 10:
            return 3
        elif total_complexity <= 15:
            return 4
        elif total_complexity <= 20:
            return 5
        elif total_complexity <= 25:
            return 6
        elif total_complexity <= 30:
            return 7
        else:
            return 8
    
    def get_component_voltage(self, component_name: str) -> str:
        """Get component operating voltage"""
        voltage_map = {
            'DHT11': '3.3V',
            'BMP180': '3.3V',
            'PIR_Sensor': '5V',
            'Ultrasonic_HC_SR04': '5V',
            'LED': '3.3V',
            'RGBLED': '3.3V',
            'Servo': '5V',
            'Motor_DC': '5V'
        }
        
        return voltage_map.get(component_name, '3.3V')
    
    def get_required_pin_count(self, component_name: str) -> int:
        """Get number of pins required by component"""
        pin_counts = {
            'DHT11': 1,
            'BMP180': 0,  # Uses I2C
            'PIR_Sensor': 1,
            'Ultrasonic_HC_SR04': 2,
            'LED': 1,
            'RGBLED': 3,
            'Servo': 1,
            'Motor_DC': 2,
            'Matrix_8x8': 0  # Uses SPI
        }
        
        return pin_counts.get(component_name, 1)
    
    def count_available_pins(self, current_components: List[str]) -> int:
        """Count available GPIO pins"""
        total_pins = 26  # GPIO 2-27
        reserved_pins = {2, 3}  # I2C pins
        
        used_pins = len(reserved_pins)
        for comp in current_components:
            used_pins += self.get_required_pin_count(comp)
        
        return total_pins - used_pins
    
    def has_mixed_voltage_levels(self, components: List[str]) -> bool:
        """Check if components have mixed voltage levels"""
        voltages = set(self.get_component_voltage(comp) for comp in components)
        return len(voltages) > 1
    
    def has_communication_devices(self, components: List[str]) -> bool:
        """Check if components use communication protocols"""
        comm_components = ['BMP180', 'LCD1602', 'Matrix_8x8', 'RFID_MFRC522']
        return any(comp in comm_components for comp in components)
    
    def has_pin_conflicts(self, components: List[str]) -> bool:
        """Check for potential pin conflicts"""
        # Simplified check - would need actual pin assignments
        return False
    
    def has_high_complexity_jump(self, components: List[str]) -> bool:
        """Check for high complexity jumps"""
        if len(components) < 2:
            return False
        
        complexities = [self.get_component_complexity(comp) for comp in components]
        complexities.sort()
        
        for i in range(1, len(complexities)):
            if complexities[i] - complexities[i-1] > 2:
                return True
        
        return False
    
    def customize_code_pattern(self, pattern: str, pin_assignment: Dict) -> str:
        """Customize code pattern with actual pin assignments"""
        if not pattern or not pin_assignment:
            return pattern
        
        customized = pattern
        
        # Replace generic pin references with actual pins
        for signal, pin in pin_assignment.items():
            customized = customized.replace('pin', str(pin))
            customized = customized.replace(signal.lower(), str(pin))
        
        return customized
    
    def get_compatibility_notes(self, component_name: str) -> List[str]:
        """Get compatibility notes from analysis"""
        notes = []
        
        # Add component-specific compatibility notes
        if component_name == 'BMP180':
            notes.append("Compatible with other I2C devices")
            notes.append("Enable I2C in raspi-config before use")
        elif component_name == 'Ultrasonic_HC_SR04':
            notes.append("ECHO pin requires voltage divider for 3.3V compatibility")
            notes.append("Works well with distance-based control projects")
        elif component_name == 'DHT11':
            notes.append("Can be combined with displays for weather station")
            notes.append("Sensitive to timing - avoid intensive processing during reads")
        
        return notes
    
    def optimize_pin_usage(self, current_components: List[str]) -> List[str]:
        """Generate pin usage optimization suggestions"""
        optimizations = []
        
        # Check if I2C components are using optimal pins
        i2c_components = [comp for comp in current_components 
                         if self.component_db.get('component_mapping', {}).get(comp, {}).get('i2c_address')]
        
        if i2c_components:
            optimizations.append("I2C components detected - ensure they use GPIO 2/3 (SDA/SCL)")
        
        # Check for suboptimal pin usage
        total_pins_used = sum(self.get_required_pin_count(comp) for comp in current_components)
        if total_pins_used > 15:
            optimizations.append("High pin usage detected - consider using I2C/SPI multiplexers")
        
        return optimizations
    
    def list_available_components(self) -> str:
        """List all available components by category"""
        response = "📦 **Available Components**\n\n"
        
        categories = {}
        for comp_name, comp_info in self.component_library.items():
            category = comp_info['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(comp_info)
        
        for category, components in categories.items():
            response += f"**{category.title()}s:**\n"
            for comp in sorted(components, key=lambda x: x['complexity']):
                complexity_stars = "⭐" * comp['complexity']
                response += f"• {comp['name']} {complexity_stars}\n"
            response += "\n"
        
        return response
    
    def list_active_components(self) -> str:
        """List currently active components"""
        current_components = self.get_current_components()
        
        if not current_components:
            return "No components currently detected. Check connections and ensure auto-configuration is running."
        
        response = "🔌 **Currently Active Components**\n\n"
        
        for comp_name in current_components:
            comp_data = self.component_db.get('component_mapping', {}).get(comp_name, {})
            complexity = comp_data.get('complexity', 1)
            complexity_stars = "⭐" * complexity
            response += f"• {comp_name} {complexity_stars}\n"
        
        return response
    
    def analyze_removal_impact(self, component_name: str, current_components: List[str]) -> List[str]:
        """Analyze impact of removing a component"""
        impact = []
        
        # Check if component is used by others
        # This would require dependency analysis
        
        # Check if removal affects project functionality
        remaining_components = [comp for comp in current_components if comp != component_name]
        if len(remaining_components) < len(current_components) // 2:
            impact.append("Removing this component significantly reduces project functionality")
        
        return impact
    
    def generate_help_response(self) -> str:
        """Generate help response for unknown commands"""
        return """
🆘 **Assembly Command Help**

**Available Commands:**
• `show [component] setup` - Display wiring guide for component
• `add [component]` - Add component with optimal pin assignment  
• `debug connections` - Analyze current connections for issues
• `optimize layout` - Get layout optimization suggestions
• `list components` - Show all available components
• `remove [component]` - Guide for removing component

**Examples:**
• `show LED matrix setup`
• `add pressure sensor`
• `debug connections` 
• `optimize layout`

**Component Names:**
Use names like: LED, DHT11, BMP180, ultrasonic sensor, servo motor, etc.
"""

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
                'features': ['Real-time readings', 'Data logging', 'Threshold alerts'],
                'code_template': '''
import time
import board
import adafruit_dht
from gpiozero import LED
import smbus

# Initialize components
dht = adafruit_dht.DHT11(board.D17)
status_led = LED(18)
bus = smbus.SMBus(1)  # For BMP180

def read_sensors():
    try:
        temperature = dht.temperature
        humidity = dht.humidity
        # Add BMP180 pressure reading here
        return temperature, humidity, None
    except Exception as e:
        print(f"Sensor error: {e}")
        return None, None, None

def main():
    while True:
        temp, hum, pressure = read_sensors()
        if temp is not None:
            status_led.on()
            print(f"Temp: {temp}°C, Humidity: {hum}%")
        else:
            status_led.off()
        time.sleep(2)

if __name__ == "__main__":
    main()
'''
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
                'features': ['Motion detection', 'Photo capture', 'SMS alerts'],
                'code_template': '''
import time
from gpiozero import MotionSensor, Buzzer, LED
from picamera import PiCamera
from datetime import datetime

# Initialize components
pir = MotionSensor(24)
buzzer = Buzzer(25)
status_led = LED(18)
camera = PiCamera()

def on_motion():
    print(f"Motion detected at {datetime.now()}")
    status_led.on()
    buzzer.on()
    
    # Take photo
    filename = f"intruder_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    camera.capture(filename)
    print(f"Photo saved: {filename}")
    
    time.sleep(2)
    buzzer.off()
    status_led.off()

def main():
    print("Security system armed")
    pir.when_motion = on_motion
    
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Security system disarmed")

if __name__ == "__main__":
    main()
'''
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
                'features': ['Soil monitoring', 'Auto watering', 'Growth tracking'],
                'code_template': '''
import time
import board
import adafruit_dht
from gpiozero import LED, MCP3008, OutputDevice
import json

# Initialize components
dht = adafruit_dht.DHT11(board.D17)
soil_sensor = MCP3008(channel=0)  # ADC for soil moisture
light_sensor = MCP3008(channel=1)  # ADC for light
water_pump = OutputDevice(22)
status_led = LED(18)

# Thresholds
SOIL_MOISTURE_THRESHOLD = 0.3
LIGHT_THRESHOLD = 0.2

def read_sensors():
    try:
        temperature = dht.temperature
        humidity = dht.humidity
        soil_moisture = soil_sensor.value
        light_level = light_sensor.value
        
        return {
            'temperature': temperature,
            'humidity': humidity,
            'soil_moisture': soil_moisture,
            'light_level': light_level,
            'timestamp': time.time()
        }
    except Exception as e:
        print(f"Sensor error: {e}")
        return None

def water_plant():
    print("Watering plant...")
    water_pump.on()
    time.sleep(3)  # Water for 3 seconds
    water_pump.off()
    print("Watering complete")

def main():
    print("Plant monitor started")
    
    while True:
        data = read_sensors()
        if data:
            print(f"Temp: {data['temperature']}°C, Humidity: {data['humidity']}%")
            print(f"Soil: {data['soil_moisture']:.2f}, Light: {data['light_level']:.2f}")
            
            # Auto watering
            if data['soil_moisture'] < SOIL_MOISTURE_THRESHOLD:
                water_plant()
            
            status_led.on()
        else:
            status_led.off()
            
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()
'''
            }
        }
    
    def initialize_learning_analytics(self) -> Dict:
        """Initialize learning analytics tracking"""
        return {
            'user_progress': {
                'completed_projects': [],
                'used_components': [],
                'current_tier': 1,
                'total_assembly_time': 0,
                'error_patterns': [],
                'learning_velocity': 1.0
            },
            'component_usage_stats': {},
            'project_completion_rates': {},
            'difficulty_progression': []
        }
    
    def generate_project_code(self, template_id: str) -> str:
        """Generate complete project code from template"""
        template = self.project_templates.get(template_id)
        if not template:
            return "Project template not found"
        
        return template.get('code_template', '# Code template not available')
    
    def estimate_assembly_time(self, components: List[str]) -> int:
        """Estimate assembly time based on component complexity"""
        base_time = 10  # Base setup time in minutes
        component_times = {
            'LED': 2, 'Button': 2, 'Resistor': 1,
            'DHT11': 5, 'BMP180': 8, 'PIR': 3,
            'Ultrasonic': 6, 'Servo': 4, 'Motor': 10,
            'LCD1602': 15, 'Matrix_8x8': 12, 'Camera': 8,
            'Buzzer': 2, 'Relay': 5, 'LDR': 3
        }
        
        total_time = base_time
        for component in components:
            total_time += component_times.get(component, 5)
        
        # Add complexity multiplier
        complexity_factor = 1 + (len(components) - 1) * 0.2
        return int(total_time * complexity_factor)
    
    def get_next_recommended_projects(self, user_tier: int, completed_projects: List[str]) -> List[Dict]:
        """Get recommended next projects based on user progress"""
        recommendations = []
        
        for project_id, template in self.project_templates.items():
            if template['name'] not in completed_projects:
                tier_range = template['tier'].split('-')
                min_tier, max_tier = int(tier_range[0]), int(tier_range[1])
                
                # Recommend projects slightly above current tier
                if min_tier <= user_tier + 1 and max_tier >= user_tier:
                    recommendations.append({
                        'project_id': project_id,
                        'name': template['name'],
                        'difficulty': template['difficulty'],
                        'estimated_time': template['assemblyTime'],
                        'new_components': self.get_new_components_in_project(template, completed_projects)
                    })
        
        # Sort by difficulty and learning value
        recommendations.sort(key=lambda x: (x['difficulty'], -len(x['new_components'])))
        return recommendations[:3]
    
    def get_new_components_in_project(self, template: Dict, used_components: List[str]) -> List[str]:
        """Get components in project that user hasn't used yet"""
        project_components = template.get('components', [])
        return [comp for comp in project_components if comp not in used_components]
    
    def analyze_learning_pattern(self, user_data: Dict) -> Dict:
        """Analyze user learning patterns and suggest optimizations"""
        analysis = {
            'learning_velocity': 'normal',
            'preferred_complexity': 'balanced',
            'component_affinity': [],
            'suggested_focus': [],
            'next_challenges': []
        }
        
        completed_count = len(user_data.get('completed_projects', []))
        if completed_count > 0:
            avg_time = user_data.get('total_assembly_time', 0) / completed_count
            
            if avg_time < 30:
                analysis['learning_velocity'] = 'fast'
                analysis['suggested_focus'].append('Try more complex projects')
            elif avg_time > 60:
                analysis['learning_velocity'] = 'careful'
                analysis['suggested_focus'].append('Take time to understand each component')
        
        # Analyze component usage patterns
        used_components = user_data.get('used_components', [])
        sensor_count = sum(1 for comp in used_components if comp in ['DHT11', 'BMP180', 'PIR', 'Ultrasonic'])
        actuator_count = sum(1 for comp in used_components if comp in ['LED', 'Motor', 'Servo', 'Buzzer'])
        
        if sensor_count > actuator_count * 2:
            analysis['component_affinity'].append('sensors')
            analysis['next_challenges'].append('Try actuator-heavy projects')
        elif actuator_count > sensor_count * 2:
            analysis['component_affinity'].append('actuators')
            analysis['next_challenges'].append('Explore sensor integration')
        
        return analysis

# Example usage
if __name__ == '__main__':
    # Initialize assembly command system
    assembly_commands = AdvancedAssemblyCommands()
    
    # Test commands
    test_commands = [
        "show LED matrix setup",
        "add pressure sensor", 
        "debug connections",
        "optimize layout",
        "list components"
    ]
    
    for command in test_commands:
        print(f"\n{'='*50}")
        print(f"Command: {command}")
        print(f"{'='*50}")
        response = assembly_commands.process_command(command)
        print(response)