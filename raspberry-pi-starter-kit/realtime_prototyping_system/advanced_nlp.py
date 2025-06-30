#!/usr/bin/env python3
"""
Advanced Natural Language Interface
Component-Aware Project Generation System

This system uses the comprehensive component analysis to:
- Parse natural language project descriptions
- Map intents to optimal component combinations
- Generate complete assembly guides
- Create deployment-ready code
"""

import re
import json
import spacy
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass
from collections import defaultdict

# Try to load spaCy model, fallback to simple processing if not available
try:
    nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except OSError:
    SPACY_AVAILABLE = False
    print("Warning: spaCy model not available. Using simple NLP processing.")

logger = logging.getLogger(__name__)

@dataclass
class ComponentSuggestion:
    name: str
    confidence: float
    reason: str
    pins: Dict[str, int]
    alternatives: List[str]

@dataclass
class ProjectIntent:
    action: str  # monitor, control, detect, display, etc.
    target: str  # temperature, motion, light, etc.
    method: str  # continuously, on_trigger, remotely, etc.
    output: str  # led, display, buzzer, etc.
    complexity: int  # 1-5 scale

class AdvancedNLPProcessor:
    """Advanced NLP processor using comprehensive component analysis"""
    
    def __init__(self, component_db, code_completion):
        self.component_db = component_db
        self.code_completion = code_completion
        self.intent_mapping = self.build_comprehensive_intent_mapping()
        self.component_synonyms = self.build_component_synonyms()
        self.action_patterns = self.build_action_patterns()
        self.project_templates = self.load_project_templates()
        
    def build_comprehensive_intent_mapping(self) -> Dict[str, Dict]:
        """Build comprehensive intent mapping from analysis data"""
        mapping = {
            # Environmental monitoring
            'temperature': {
                'primary_components': ['DHT11', 'DHT22', 'DS18B20'],
                'supporting_components': ['LCD1602', 'LED', 'OLED'],
                'complexity': 3,
                'category': 'sensing',
                'keywords': ['temp', 'temperature', 'hot', 'cold', 'climate', 'weather']
            },
            'humidity': {
                'primary_components': ['DHT11', 'DHT22'],
                'supporting_components': ['LCD1602', 'LED'],
                'complexity': 3,
                'category': 'sensing',
                'keywords': ['humidity', 'moisture', 'damp', 'dry']
            },
            'pressure': {
                'primary_components': ['BMP180_Barometer', 'BMP280'],
                'supporting_components': ['LCD1602', 'OLED'],
                'complexity': 4,
                'category': 'sensing',
                'keywords': ['pressure', 'barometric', 'altitude', 'weather']
            },
            
            # Motion and proximity
            'motion': {
                'primary_components': ['PIR_Sensor', 'Ultrasonic_HC_SR04'],
                'supporting_components': ['LED', 'Buzzer', 'Camera_Module'],
                'complexity': 2,
                'category': 'detection',
                'keywords': ['motion', 'movement', 'person', 'detect', 'presence']
            },
            'distance': {
                'primary_components': ['Ultrasonic_HC_SR04', 'VL53L0X'],
                'supporting_components': ['LED', 'LCD1602', 'Buzzer'],
                'complexity': 3,
                'category': 'measurement',
                'keywords': ['distance', 'range', 'proximity', 'obstacle', 'parking']
            },
            'touch': {
                'primary_components': ['Touch_Sensor', 'Button'],
                'supporting_components': ['LED', 'RGBLED'],
                'complexity': 1,
                'category': 'input',
                'keywords': ['touch', 'tap', 'press', 'contact']
            },
            
            # Light and color
            'light': {
                'primary_components': ['Photoresistor', 'TSL2561'],
                'supporting_components': ['LED', 'RGBLED', 'LCD1602'],
                'complexity': 2,
                'category': 'sensing',
                'keywords': ['light', 'brightness', 'illumination', 'dark', 'bright']
            },
            'color': {
                'primary_components': ['TCS3200', 'RGBLED'],
                'supporting_components': ['LCD1602', 'LED'],
                'complexity': 4,
                'category': 'sensing',
                'keywords': ['color', 'rgb', 'hue', 'red', 'green', 'blue']
            },
            
            # Audio
            'sound': {
                'primary_components': ['Sound_Sensor', 'Microphone'],
                'supporting_components': ['LED', 'LCD1602', 'Buzzer'],
                'complexity': 3,
                'category': 'sensing',
                'keywords': ['sound', 'audio', 'noise', 'voice', 'music']
            },
            'speaker': {
                'primary_components': ['Buzzer', 'Speaker', 'PAM8403'],
                'supporting_components': ['Button', 'Potentiometer'],
                'complexity': 3,
                'category': 'output',
                'keywords': ['speaker', 'audio', 'sound', 'music', 'alarm', 'buzzer']
            },
            
            # Motor control
            'motor': {
                'primary_components': ['Motor_DC', 'L293D'],
                'supporting_components': ['Button', 'Joystick', 'Rotary_Encoder'],
                'complexity': 4,
                'category': 'actuation',
                'keywords': ['motor', 'rotate', 'spin', 'drive', 'wheel']
            },
            'servo': {
                'primary_components': ['Servo'],
                'supporting_components': ['Joystick', 'Button', 'Potentiometer'],
                'complexity': 3,
                'category': 'actuation',
                'keywords': ['servo', 'angle', 'position', 'arm', 'precise']
            },
            'stepper': {
                'primary_components': ['Stepper_Motor', 'ULN2003'],
                'supporting_components': ['Button', 'Rotary_Encoder'],
                'complexity': 5,
                'category': 'actuation',
                'keywords': ['stepper', 'precise', 'steps', 'accuracy']
            },
            
            # Communication
            'wireless': {
                'primary_components': ['ESP32', 'NRF24L01', 'WiFi'],
                'supporting_components': ['LED', 'Button'],
                'complexity': 6,
                'category': 'communication',
                'keywords': ['wireless', 'wifi', 'bluetooth', 'remote', 'internet']
            },
            'rfid': {
                'primary_components': ['RFID_MFRC522'],
                'supporting_components': ['LED', 'Buzzer', 'LCD1602'],
                'complexity': 5,
                'category': 'identification',
                'keywords': ['rfid', 'card', 'tag', 'access', 'identification']
            },
            
            # Display
            'display': {
                'primary_components': ['LCD1602', 'OLED', 'Nokia5110'],
                'supporting_components': ['Button', 'Rotary_Encoder'],
                'complexity': 3,
                'category': 'output',
                'keywords': ['display', 'screen', 'show', 'lcd', 'oled']
            },
            'matrix': {
                'primary_components': ['LED_Matrix_8x8', '74HC595'],
                'supporting_components': ['Button', 'Joystick'],
                'complexity': 4,
                'category': 'output',
                'keywords': ['matrix', 'grid', 'pattern', 'animation']
            },
            
            # Complex systems
            'camera': {
                'primary_components': ['Camera_Module'],
                'supporting_components': ['LED', 'PIR_Sensor', 'Button'],
                'complexity': 6,
                'category': 'sensing',
                'keywords': ['camera', 'photo', 'video', 'image', 'capture']
            },
            'robot': {
                'primary_components': ['Motor_DC', 'Ultrasonic_HC_SR04', 'L293D'],
                'supporting_components': ['Camera_Module', 'LED', 'Buzzer'],
                'complexity': 7,
                'category': 'integration',
                'keywords': ['robot', 'autonomous', 'navigation', 'follow']
            },
            'iot': {
                'primary_components': ['ESP32', 'DHT11', 'LED'],
                'supporting_components': ['Buzzer', 'LCD1602'],
                'complexity': 8,
                'category': 'integration',
                'keywords': ['iot', 'internet', 'cloud', 'remote', 'monitoring']
            }
        }
        
        return mapping
    
    def build_component_synonyms(self) -> Dict[str, List[str]]:
        """Build synonyms for component names"""
        return {
            'LED': ['light', 'led', 'lamp', 'bulb', 'indicator'],
            'RGBLED': ['rgb', 'color led', 'multicolor', 'colored light'],
            'Button': ['button', 'switch', 'press', 'click'],
            'DHT11': ['dht11', 'temperature sensor', 'humidity sensor'],
            'Ultrasonic_HC_SR04': ['ultrasonic', 'distance sensor', 'sonar'],
            'PIR_Sensor': ['pir', 'motion sensor', 'presence detector'],
            'Camera_Module': ['camera', 'cam', 'video', 'picture'],
            'Motor_DC': ['motor', 'dc motor', 'drive'],
            'Servo': ['servo', 'servo motor'],
            'LCD1602': ['lcd', 'display', 'screen'],
            'Buzzer': ['buzzer', 'speaker', 'alarm', 'beep']
        }
    
    def build_action_patterns(self) -> Dict[str, Dict]:
        """Build action pattern recognition"""
        return {
            'monitor': {
                'keywords': ['monitor', 'watch', 'track', 'observe', 'measure'],
                'implies': ['sensing', 'display'],
                'complexity_modifier': 0
            },
            'control': {
                'keywords': ['control', 'operate', 'manage', 'drive'],
                'implies': ['actuation', 'input'],
                'complexity_modifier': 1
            },
            'detect': {
                'keywords': ['detect', 'sense', 'find', 'identify'],
                'implies': ['sensing', 'notification'],
                'complexity_modifier': 0
            },
            'alert': {
                'keywords': ['alert', 'alarm', 'notify', 'warn'],
                'implies': ['sensing', 'output'],
                'complexity_modifier': 1
            },
            'automate': {
                'keywords': ['automate', 'automatic', 'smart', 'intelligent'],
                'implies': ['sensing', 'actuation', 'logic'],
                'complexity_modifier': 2
            },
            'record': {
                'keywords': ['record', 'log', 'save', 'store'],
                'implies': ['sensing', 'storage'],
                'complexity_modifier': 2
            },
            'stream': {
                'keywords': ['stream', 'live', 'realtime', 'broadcast'],
                'implies': ['sensing', 'communication'],
                'complexity_modifier': 3
            }
        }
    
    def load_project_templates(self) -> Dict[str, Dict]:
        """Load project templates based on common patterns"""
        return {
            'temperature_monitor': {
                'description': 'Monitor temperature and humidity with display',
                'components': ['DHT11', 'LCD1602', 'LED'],
                'complexity': 3,
                'estimated_time': '30 minutes',
                'skills_required': ['I2C communication', 'sensor reading']
            },
            'motion_alarm': {
                'description': 'Motion detection alarm system',
                'components': ['PIR_Sensor', 'Buzzer', 'LED'],
                'complexity': 2,
                'estimated_time': '20 minutes',
                'skills_required': ['digital input', 'basic output']
            },
            'distance_ranger': {
                'description': 'Ultrasonic distance measurement with LED indicator',
                'components': ['Ultrasonic_HC_SR04', 'LED', 'LCD1602'],
                'complexity': 3,
                'estimated_time': '25 minutes',
                'skills_required': ['timing', 'distance calculation']
            },
            'smart_light': {
                'description': 'Automatic light control based on ambient light',
                'components': ['Photoresistor', 'RGBLED', 'ADC'],
                'complexity': 3,
                'estimated_time': '35 minutes',
                'skills_required': ['analog reading', 'PWM control']
            },
            'robot_car': {
                'description': 'Remote controlled robot car',
                'components': ['Motor_DC', 'L293D', 'Ultrasonic_HC_SR04', 'Button'],
                'complexity': 6,
                'estimated_time': '2 hours',
                'skills_required': ['motor control', 'obstacle avoidance', 'multiple sensors']
            },
            'security_system': {
                'description': 'Complete security monitoring system',
                'components': ['PIR_Sensor', 'Camera_Module', 'Buzzer', 'LED', 'RFID_MFRC522'],
                'complexity': 8,
                'estimated_time': '4 hours',
                'skills_required': ['multiple sensors', 'camera control', 'RFID', 'system integration']
            }
        }
    
    def process_natural_language(self, user_input: str) -> Dict:
        """Process natural language input and generate complete project"""
        logger.info(f"Processing NLP input: {user_input}")
        
        # Parse the input
        parsed_intent = self.parse_intent(user_input)
        if not parsed_intent:
            return self.handle_unclear_intent(user_input)
        
        # Generate component suggestions
        component_suggestions = self.suggest_components(parsed_intent)
        if not component_suggestions:
            return self.handle_no_components(parsed_intent)
        
        # Create optimal component combination
        final_components = self.optimize_component_selection(component_suggestions, parsed_intent)
        
        # Generate pin assignments
        pin_assignments = self.code_completion.suggest_pin_assignments([c.name for c in final_components])
        
        # Generate assembly guide
        assembly_guide = self.generate_detailed_assembly_guide(final_components, parsed_intent)
        
        # Generate optimized code
        generated_code = self.generate_project_code(final_components, parsed_intent)
        
        # Suggest learning path
        learning_path = self.suggest_learning_path(final_components, parsed_intent)
        
        return {
            'success': True,
            'understood_intent': parsed_intent,
            'selected_components': [{'name': c.name, 'confidence': c.confidence, 'reason': c.reason} for c in final_components],
            'pin_assignments': pin_assignments,
            'assembly_guide': assembly_guide,
            'generated_code': generated_code,
            'learning_path': learning_path,
            'estimated_time': self.estimate_project_time(final_components),
            'difficulty_level': max(c.confidence for c in final_components),
            'next_suggestions': self.suggest_project_extensions(final_components, parsed_intent)
        }
    
    def parse_intent(self, user_input: str) -> Optional[ProjectIntent]:
        """Parse user input to extract project intent"""
        user_input = user_input.lower().strip()
        
        # Extract action
        detected_action = None
        for action, patterns in self.action_patterns.items():
            if any(keyword in user_input for keyword in patterns['keywords']):
                detected_action = action
                break
        
        if not detected_action:
            detected_action = 'monitor'  # Default action
        
        # Extract target (what to sense/control)
        detected_target = None
        target_confidence = 0
        for intent, data in self.intent_mapping.items():
            keyword_matches = sum(1 for keyword in data['keywords'] if keyword in user_input)
            if keyword_matches > target_confidence:
                detected_target = intent
                target_confidence = keyword_matches
        
        if not detected_target:
            return None
        
        # Extract method and output preferences
        method = 'continuously'
        if any(word in user_input for word in ['when', 'if', 'trigger']):
            method = 'on_trigger'
        if any(word in user_input for word in ['remote', 'wifi', 'bluetooth']):
            method = 'remotely'
        
        output = 'display'
        if any(word in user_input for word in ['led', 'light']):
            output = 'led'
        if any(word in user_input for word in ['buzz', 'alarm', 'sound']):
            output = 'buzzer'
        if any(word in user_input for word in ['screen', 'display', 'show']):
            output = 'display'
        
        # Calculate complexity
        base_complexity = self.intent_mapping[detected_target]['complexity']
        action_modifier = self.action_patterns[detected_action]['complexity_modifier']
        final_complexity = min(8, base_complexity + action_modifier)
        
        return ProjectIntent(
            action=detected_action,
            target=detected_target,
            method=method,
            output=output,
            complexity=final_complexity
        )
    
    def suggest_components(self, intent: ProjectIntent) -> List[ComponentSuggestion]:
        """Suggest optimal components based on parsed intent"""
        suggestions = []
        
        # Get primary components for the target
        target_data = self.intent_mapping[intent.target]
        
        # Add primary components
        for component in target_data['primary_components']:
            if component in self.component_db.get('component_mapping', {}):
                comp_data = self.component_db['component_mapping'][component]
                
                suggestions.append(ComponentSuggestion(
                    name=component,
                    confidence=0.9,
                    reason=f"Primary component for {intent.target} {intent.action}",
                    pins=self.get_default_pins(component),
                    alternatives=target_data['primary_components']
                ))
        
        # Add supporting components based on output preference
        if intent.output == 'led':
            suggestions.append(ComponentSuggestion(
                name='LED',
                confidence=0.8,
                reason=f"LED output for {intent.action} indication",
                pins={'pin': 17},
                alternatives=['RGBLED', 'WS2812_LED_Strip']
            ))
        elif intent.output == 'display':
            suggestions.append(ComponentSuggestion(
                name='LCD1602',
                confidence=0.8,
                reason=f"Display output for {intent.action} data",
                pins={'sda': 2, 'scl': 3},
                alternatives=['OLED', 'Nokia5110']
            ))
        elif intent.output == 'buzzer':
            suggestions.append(ComponentSuggestion(
                name='Buzzer',
                confidence=0.8,
                reason=f"Audio alert for {intent.action}",
                pins={'pin': 18},
                alternatives=['Speaker', 'PAM8403']
            ))
        
        # Add method-specific components
        if intent.method == 'remotely':
            suggestions.append(ComponentSuggestion(
                name='ESP32',
                confidence=0.7,
                reason="WiFi connectivity for remote control",
                pins={'various': 'multiple'},
                alternatives=['NRF24L01', 'Bluetooth']
            ))
        
        if intent.method == 'on_trigger':
            suggestions.append(ComponentSuggestion(
                name='Button',
                confidence=0.6,
                reason="Manual trigger input",
                pins={'pin': 18},
                alternatives=['Touch_Sensor', 'Rotary_Encoder']
            ))
        
        return suggestions
    
    def optimize_component_selection(self, suggestions: List[ComponentSuggestion], intent: ProjectIntent) -> List[ComponentSuggestion]:
        """Optimize component selection to avoid conflicts and improve compatibility"""
        optimized = []
        used_pins = set()
        
        # Sort by confidence
        suggestions.sort(key=lambda x: x.confidence, reverse=True)
        
        for suggestion in suggestions:
            # Check pin conflicts
            pin_conflict = False
            suggestion_pins = set()
            
            if isinstance(suggestion.pins, dict):
                for pin_val in suggestion.pins.values():
                    if isinstance(pin_val, int):
                        suggestion_pins.add(pin_val)
            
            if suggestion_pins.intersection(used_pins):
                # Try to reassign pins
                new_pins = self.reassign_pins(suggestion, used_pins)
                if new_pins:
                    suggestion.pins = new_pins
                    used_pins.update(pin_val for pin_val in new_pins.values() if isinstance(pin_val, int))
                else:
                    # Skip this component due to pin conflict
                    continue
            else:
                used_pins.update(suggestion_pins)
            
            optimized.append(suggestion)
        
        return optimized
    
    def reassign_pins(self, suggestion: ComponentSuggestion, used_pins: set) -> Optional[Dict]:
        """Reassign pins to avoid conflicts"""
        component_name = suggestion.name
        
        # Get available pins for this component type
        available_pins = [p for p in range(2, 28) if p not in used_pins]
        
        if component_name in ['LED', 'Button', 'Buzzer']:
            if available_pins:
                return {'pin': available_pins[0]}
        elif component_name in ['LCD1602', 'OLED']:
            # I2C components use fixed pins
            if 2 not in used_pins and 3 not in used_pins:
                return {'sda': 2, 'scl': 3}
        elif component_name == 'RGBLED':
            if len(available_pins) >= 3:
                return {'red': available_pins[0], 'green': available_pins[1], 'blue': available_pins[2]}
        
        return None
    
    def get_default_pins(self, component_name: str) -> Dict:
        """Get default pin assignments for component"""
        defaults = {
            'LED': {'pin': 17},
            'RGBLED': {'red': 17, 'green': 18, 'blue': 27},
            'Button': {'pin': 18},
            'DHT11': {'pin': 17},
            'Ultrasonic_HC_SR04': {'trigger': 20, 'echo': 21},
            'PIR_Sensor': {'pin': 17},
            'LCD1602': {'sda': 2, 'scl': 3},
            'Buzzer': {'pin': 18},
            'Motor_DC': {'forward': 18, 'backward': 19},
            'Servo': {'pin': 17}
        }
        
        return defaults.get(component_name, {'pin': 17})
    
    def generate_detailed_assembly_guide(self, components: List[ComponentSuggestion], intent: ProjectIntent) -> Dict:
        """Generate comprehensive assembly guide"""
        guide = {
            'title': f"{intent.action.title()} {intent.target.title()} System",
            'description': f"Complete guide to build a {intent.target} {intent.action} system",
            'difficulty': intent.complexity,
            'estimated_time': self.estimate_project_time(components),
            'required_components': [c.name for c in components],
            'tools_needed': ['Breadboard', 'Jumper wires', 'Raspberry Pi'],
            'steps': []
        }
        
        # Generate step-by-step instructions
        step_number = 1
        
        # Step 1: Preparation
        guide['steps'].append({
            'step': step_number,
            'title': 'Preparation',
            'description': 'Gather all components and prepare workspace',
            'details': [
                'Ensure Raspberry Pi is powered off',
                'Gather all required components',
                'Prepare breadboard and jumper wires',
                'Have the component datasheets ready'
            ],
            'estimated_time': '5 minutes',
            'warnings': ['Always power off Pi before making connections']
        })
        step_number += 1
        
        # Steps for each component
        for component in components:
            comp_data = self.component_db.get('component_mapping', {}).get(component.name, {})
            
            guide['steps'].append({
                'step': step_number,
                'title': f'Connect {component.name}',
                'description': f'Wire {component.name} to Raspberry Pi',
                'details': self.generate_component_wiring_steps(component),
                'pin_assignments': component.pins,
                'estimated_time': f'{comp_data.get("complexity", 1) * 3} minutes',
                'warnings': self.get_component_warnings(component.name),
                'testing': f'Test {component.name} with basic code before proceeding'
            })
            step_number += 1
        
        # Final testing step
        guide['steps'].append({
            'step': step_number,
            'title': 'Final Testing',
            'description': 'Test complete system functionality',
            'details': [
                'Power on Raspberry Pi',
                'Run the generated code',
                'Verify all components respond correctly',
                'Test edge cases and error conditions'
            ],
            'estimated_time': '10 minutes',
            'troubleshooting': self.generate_troubleshooting_guide(components)
        })
        
        return guide
    
    def generate_component_wiring_steps(self, component: ComponentSuggestion) -> List[str]:
        """Generate detailed wiring steps for a component"""
        component_name = component.name
        pins = component.pins
        
        wiring_guides = {
            'LED': [
                'Connect LED positive (longer leg) to GPIO pin via 220Ω resistor',
                'Connect LED negative (shorter leg) to GND',
                'Ensure proper polarity to avoid damage'
            ],
            'RGBLED': [
                'Connect RED pin to GPIO pin via 220Ω resistor',
                'Connect GREEN pin to GPIO pin via 220Ω resistor', 
                'Connect BLUE pin to GPIO pin via 220Ω resistor',
                'Connect common cathode to GND (or anode to 3.3V for common anode)'
            ],
            'Button': [
                'Connect one side of button to GPIO pin',
                'Connect other side of button to GND',
                'Add 10kΩ pull-up resistor between GPIO and 3.3V'
            ],
            'DHT11': [
                'Connect VCC to 3.3V',
                'Connect GND to ground',
                'Connect DATA to GPIO pin',
                'Add 4.7kΩ pull-up resistor between DATA and VCC'
            ],
            'Ultrasonic_HC_SR04': [
                'Connect VCC to 5V',
                'Connect GND to ground',
                'Connect TRIG to GPIO pin',
                'Connect ECHO to GPIO pin (through voltage divider for 3.3V)'
            ],
            'LCD1602': [
                'Connect VCC to 5V',
                'Connect GND to ground',
                'Connect SDA to GPIO2 (I2C SDA)',
                'Connect SCL to GPIO3 (I2C SCL)',
                'Verify I2C backpack is properly configured'
            ]
        }
        
        return wiring_guides.get(component_name, [
            f'Connect {component_name} according to datasheet',
            'Verify power requirements (3.3V or 5V)',
            'Connect signal pins as specified in pin assignments'
        ])
    
    def get_component_warnings(self, component_name: str) -> List[str]:
        """Get safety warnings for component"""
        warnings = {
            'Motor_DC': ['Motors require external power supply', 'Use motor driver IC to prevent GPIO damage'],
            'Servo': ['Servo motors can draw significant current', 'Consider external power for multiple servos'],
            'Ultrasonic_HC_SR04': ['HC-SR04 operates at 5V - use voltage divider for ECHO pin'],
            'LED': ['Always use current limiting resistor', 'Check LED forward voltage'],
            'Camera_Module': ['Handle camera module carefully', 'Ensure proper ribbon cable connection']
        }
        
        return warnings.get(component_name, ['Follow component datasheet specifications'])
    
    def generate_troubleshooting_guide(self, components: List[ComponentSuggestion]) -> List[Dict]:
        """Generate troubleshooting guide for the project"""
        return [
            {
                'problem': 'Component not responding',
                'solutions': [
                    'Check all connections',
                    'Verify power supply',
                    'Test individual components',
                    'Check pin assignments in code'
                ]
            },
            {
                'problem': 'GPIO errors in code',
                'solutions': [
                    'Ensure GPIO library is installed',
                    'Check for pin conflicts',
                    'Verify pin numbering (BCM vs BOARD)',
                    'Run as sudo if required'
                ]
            },
            {
                'problem': 'I2C devices not detected',
                'solutions': [
                    'Enable I2C in raspi-config',
                    'Check I2C wiring (SDA/SCL)',
                    'Run i2cdetect -y 1 to scan devices',
                    'Verify pull-up resistors'
                ]
            }
        ]
    
    def generate_project_code(self, components: List[ComponentSuggestion], intent: ProjectIntent) -> str:
        """Generate optimized project code"""
        # Use our code completion system as base
        component_names = [c.name for c in components]
        base_code = self.code_completion.generate_code_template(component_names)
        
        # Enhance code based on intent
        enhanced_code = self.enhance_code_for_intent(base_code, intent, components)
        
        return enhanced_code
    
    def enhance_code_for_intent(self, base_code: str, intent: ProjectIntent, components: List[ComponentSuggestion]) -> str:
        """Enhance generated code based on specific intent"""
        lines = base_code.split('\n')
        
        # Add intent-specific functionality
        if intent.action == 'monitor':
            # Add continuous monitoring loop
            monitoring_code = '''
def monitor_continuously():
    """Continuous monitoring based on user intent"""
    while True:
        # Read sensor values
        readings = {}
        '''
            
            for component in components:
                if 'Sensor' in component.name or component.name in ['DHT11', 'Ultrasonic_HC_SR04']:
                    monitoring_code += f'''
        # Read {component.name}
        try:
            value = read_{component.name.lower()}()
            readings['{component.name}'] = value
            print(f"{component.name}: {{value}}")
        except Exception as e:
            print(f"Error reading {component.name}: {{e}}")
        '''
            
            monitoring_code += '''
        time.sleep(1)  # Monitoring interval
        '''
            
            lines.insert(-5, monitoring_code)
        
        elif intent.action == 'alert':
            # Add threshold-based alerting
            alert_code = '''
def check_alerts():
    """Check sensor values against thresholds and trigger alerts"""
    # Define thresholds based on application
    thresholds = {
        'temperature_high': 30,
        'motion_detected': True,
        'distance_close': 10
    }
    
    # Check conditions and trigger alerts
    '''
            lines.insert(-5, alert_code)
        
        return '\n'.join(lines)
    
    def estimate_project_time(self, components: List[ComponentSuggestion]) -> str:
        """Estimate total project completion time"""
        base_time = 15  # Base setup time
        
        for component in components:
            comp_data = self.component_db.get('component_mapping', {}).get(component.name, {})
            complexity = comp_data.get('complexity', 1)
            base_time += complexity * 5
        
        if base_time < 30:
            return "20-30 minutes"
        elif base_time < 60:
            return "45-60 minutes"
        elif base_time < 120:
            return "1-2 hours"
        else:
            return "2+ hours"
    
    def suggest_learning_path(self, components: List[ComponentSuggestion], intent: ProjectIntent) -> Dict:
        """Suggest learning path based on project complexity"""
        max_complexity = max(c.confidence for c in components) if components else 1
        
        if max_complexity <= 2:
            path = "beginner"
            next_steps = ["Try adding more sensors", "Experiment with different outputs", "Add remote control"]
        elif max_complexity <= 5:
            path = "intermediate" 
            next_steps = ["Add IoT connectivity", "Implement data logging", "Create mobile app interface"]
        else:
            path = "advanced"
            next_steps = ["Machine learning integration", "Multi-device coordination", "Commercial deployment"]
        
        return {
            'current_level': path,
            'next_steps': next_steps,
            'recommended_tutorials': self.get_recommended_tutorials(intent.target),
            'skill_focus': self.get_skill_focus(components)
        }
    
    def get_recommended_tutorials(self, target: str) -> List[str]:
        """Get recommended tutorials based on target domain"""
        tutorials = {
            'temperature': ['I2C communication', 'Sensor calibration', 'Data logging'],
            'motion': ['Digital input handling', 'Interrupt programming', 'Real-time processing'],
            'motor': ['PWM control', 'Motor driver circuits', 'Feedback systems'],
            'camera': ['Image processing', 'OpenCV basics', 'Streaming protocols']
        }
        
        return tutorials.get(target, ['GPIO basics', 'Python programming', 'Electronics fundamentals'])
    
    def get_skill_focus(self, components: List[ComponentSuggestion]) -> List[str]:
        """Determine skill focus areas for the project"""
        skills = set()
        
        for component in components:
            comp_data = self.component_db.get('component_mapping', {}).get(component.name, {})
            
            if 'I2C' in str(comp_data) or component.name in ['LCD1602', 'DHT11']:
                skills.add('I2C Communication')
            if 'SPI' in str(comp_data):
                skills.add('SPI Communication')
            if 'Motor' in component.name:
                skills.add('Motor Control')
            if 'Sensor' in component.name:
                skills.add('Sensor Integration')
            if component.name in ['Camera_Module']:
                skills.add('Image Processing')
        
        return list(skills)
    
    def suggest_project_extensions(self, components: List[ComponentSuggestion], intent: ProjectIntent) -> List[Dict]:
        """Suggest project extensions and improvements"""
        extensions = []
        
        # Add IoT if not present
        has_connectivity = any('ESP32' in c.name or 'WiFi' in c.name for c in components)
        if not has_connectivity:
            extensions.append({
                'name': 'IoT Connectivity',
                'description': 'Add WiFi connectivity for remote monitoring',
                'components': ['ESP32', 'WiFi'],
                'complexity_increase': 2
            })
        
        # Add data logging
        extensions.append({
            'name': 'Data Logging',
            'description': 'Log sensor data to SD card or cloud',
            'components': ['SD_Card', 'RTC'],
            'complexity_increase': 1
        })
        
        # Add mobile app
        extensions.append({
            'name': 'Mobile App Control',
            'description': 'Create smartphone app for remote control',
            'components': ['Bluetooth', 'App_Interface'],
            'complexity_increase': 3
        })
        
        return extensions
    
    def handle_unclear_intent(self, user_input: str) -> Dict:
        """Handle cases where intent is unclear"""
        return {
            'success': False,
            'error': 'Could not understand the project description',
            'suggestions': [
                'Try: "Build a temperature monitor with LED alerts"',
                'Try: "Create a motion detection alarm system"',
                'Try: "Make a distance sensor with display"'
            ],
            'detected_keywords': self.extract_keywords(user_input),
            'help': 'Use action words (monitor, control, detect) with target objects (temperature, motion, distance)'
        }
    
    def handle_no_components(self, intent: ProjectIntent) -> Dict:
        """Handle cases where no suitable components are found"""
        return {
            'success': False,
            'error': f'No suitable components found for {intent.action} {intent.target}',
            'intent': intent.__dict__,
            'suggestions': [
                'Try a different action word',
                'Specify more details about your project',
                'Check available components in the library'
            ]
        }
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from text"""
        # Simple keyword extraction
        words = text.lower().split()
        relevant_words = []
        
        for word in words:
            if len(word) > 3 and word not in ['with', 'using', 'that', 'will', 'can']:
                relevant_words.append(word)
        
        return relevant_words

# Example usage
if __name__ == '__main__':
    # Mock data for testing
    component_db = {'component_mapping': {}}
    
    class MockCodeCompletion:
        def generate_code_template(self, components):
            return f"# Generated code for {components}"
        def suggest_pin_assignments(self, components):
            return {comp: {'pin': 17 + i} for i, comp in enumerate(components)}
    
    nlp_processor = AdvancedNLPProcessor(component_db, MockCodeCompletion())
    
    test_inputs = [
        "Build a temperature monitor with LCD display",
        "Create a motion detection alarm system",
        "Make a robot car with obstacle avoidance",
        "Monitor humidity and control fans automatically"
    ]
    
    for test_input in test_inputs:
        print(f"\nInput: {test_input}")
        result = nlp_processor.process_natural_language(test_input)
        print(f"Result: {result.get('success', False)}")
        if result.get('success'):
            print(f"Components: {[c['name'] for c in result['selected_components']]}")