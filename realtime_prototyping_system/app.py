#!/usr/bin/env python3
"""
Advanced Real-Time Raspberry Pi Prototyping System
Web Application Foundation

This system leverages the comprehensive analysis to provide:
- Intelligent component assembly interface
- Real-time breadboard visualization
- Smart code generation and deployment
- Natural language project creation
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import json
import os
import sys
import subprocess
from pathlib import Path

# Add parent directory to path to import our analysis modules
sys.path.append(str(Path(__file__).parent.parent))

try:
    from smart_code_completion import SmartCodeCompletion
    from code_pattern_library import *
except ImportError:
    print("Warning: Could not import analysis modules. Please ensure they are in the parent directory.")

app = Flask(__name__)
app.secret_key = 'raspberry_pi_prototyping_system_2024'

class PrototypingSystem:
    """Main prototyping system controller"""
    
    def __init__(self):
        self.load_analysis_data()
        self.initialize_systems()
    
    def load_analysis_data(self):
        """Load all analysis data from the comprehensive analysis"""
        try:
            # Load component mapping from our analysis
            with open('../component_code_mapping.json', 'r') as f:
                self.component_db = json.load(f)
            
            # Initialize smart code completion
            self.code_completion = SmartCodeCompletion()
            
            print("✅ Analysis data loaded successfully")
        except Exception as e:
            print(f"❌ Error loading analysis data: {e}")
            # Fallback to embedded data
            self.load_fallback_data()
    
    def load_fallback_data(self):
        """Fallback component data if files not found"""
        self.component_db = {
            "component_mapping": {
                "LED": {
                    "examples": ["01.1.1_Blink", "02.1.1_ButtonLED"],
                    "pins_used": ["GPIO17", "GPIO18"],
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
                }
            }
        }
        self.code_completion = SmartCodeCompletion()
    
    def initialize_systems(self):
        """Initialize all subsystems"""
        self.breadboard_state = {
            "components": [],
            "connections": [],
            "conflicts": [],
            "suggestions": []
        }
        
        self.deployment_config = {
            "pi_ip": None,
            "pi_user": "pi",
            "auto_deploy": False,
            "hot_swap_enabled": True
        }
        
        self.nlp_processor = NaturalLanguageProcessor(self.component_db, self.code_completion)

# Global system instance
prototyping_system = PrototypingSystem()

@app.route('/')
def index():
    """Main application interface"""
    return render_template('index.html', 
                         components=prototyping_system.component_db.get('component_mapping', {}),
                         breadboard_state=prototyping_system.breadboard_state)

@app.route('/api/components')
def get_components():
    """API endpoint to get all components from our analysis"""
    return jsonify(prototyping_system.component_db.get('component_mapping', {}))

@app.route('/api/component/<component_name>')
def get_component_details(component_name):
    """Get detailed information about a specific component"""
    components = prototyping_system.component_db.get('component_mapping', {})
    if component_name in components:
        component = components[component_name]
        
        # Add smart suggestions based on our analysis
        suggestions = prototyping_system.code_completion.suggest_next_component([component_name])
        
        return jsonify({
            'component': component,
            'suggestions': suggestions,
            'pin_conflicts': prototyping_system.get_pin_conflicts(component_name),
            'assembly_guide': prototyping_system.generate_assembly_guide(component_name)
        })
    return jsonify({'error': 'Component not found'}), 404

@app.route('/api/breadboard/add_component', methods=['POST'])
def add_component_to_breadboard():
    """Add component to virtual breadboard with conflict detection"""
    data = request.json
    component_name = data.get('component')
    pin_assignment = data.get('pins', {})
    
    # Use our smart pin assignment system
    if not pin_assignment:
        current_components = [c['name'] for c in prototyping_system.breadboard_state['components']]
        pin_suggestions = prototyping_system.code_completion.suggest_pin_assignments(current_components + [component_name])
        pin_assignment = pin_suggestions.get(component_name, {})
    
    # Check for conflicts using our analysis
    conflicts = prototyping_system.check_pin_conflicts(component_name, pin_assignment)
    
    component_info = {
        'name': component_name,
        'pins': pin_assignment,
        'conflicts': conflicts,
        'timestamp': data.get('timestamp')
    }
    
    prototyping_system.breadboard_state['components'].append(component_info)
    
    # Generate smart suggestions for next components
    current_components = [c['name'] for c in prototyping_system.breadboard_state['components']]
    suggestions = prototyping_system.code_completion.suggest_next_component(current_components)
    prototyping_system.breadboard_state['suggestions'] = suggestions
    
    return jsonify({
        'success': True,
        'breadboard_state': prototyping_system.breadboard_state,
        'generated_code': prototyping_system.generate_project_code()
    })

@app.route('/api/breadboard/validate')
def validate_breadboard():
    """Validate current breadboard configuration using our patterns"""
    current_components = [c['name'] for c in prototyping_system.breadboard_state['components']]
    
    # Use our code completion system for validation
    validation_results = {
        'valid': True,
        'warnings': [],
        'errors': [],
        'suggestions': []
    }
    
    # Check for pin conflicts
    used_pins = {}
    for component in prototyping_system.breadboard_state['components']:
        for pin_type, pin_num in component.get('pins', {}).items():
            if pin_num in used_pins:
                validation_results['errors'].append(f"Pin conflict: GPIO{pin_num} used by {used_pins[pin_num]} and {component['name']}")
                validation_results['valid'] = False
            else:
                used_pins[pin_num] = component['name']
    
    # Add complexity-based suggestions
    total_complexity = sum(prototyping_system.get_component_complexity(c['name']) for c in prototyping_system.breadboard_state['components'])
    if total_complexity > 15:
        validation_results['warnings'].append("High complexity project - consider breaking into smaller components")
    
    return jsonify(validation_results)

@app.route('/api/code/generate', methods=['POST'])
def generate_code():
    """Generate code using our smart code completion system"""
    data = request.json
    components = data.get('components', [])
    project_type = data.get('type', 'basic')
    
    # Use our code completion system
    if components:
        generated_code = prototyping_system.code_completion.generate_code_template(components)
    else:
        # Use current breadboard state
        current_components = [c['name'] for c in prototyping_system.breadboard_state['components']]
        generated_code = prototyping_system.code_completion.generate_code_template(current_components)
    
    # Add pin assignments from breadboard
    pin_assignments = {}
    for component in prototyping_system.breadboard_state['components']:
        pin_assignments[component['name']] = component.get('pins', {})
    
    # Customize code with actual pin assignments
    customized_code = prototyping_system.customize_code_with_pins(generated_code, pin_assignments)
    
    return jsonify({
        'code': customized_code,
        'filename': f"generated_project_{len(components)}_components.py",
        'pin_assignments': pin_assignments,
        'deployment_ready': True
    })

@app.route('/api/deploy', methods=['POST'])
def deploy_to_pi():
    """Deploy generated code to Raspberry Pi"""
    data = request.json
    code = data.get('code')
    filename = data.get('filename', 'project.py')
    pi_ip = data.get('pi_ip', prototyping_system.deployment_config['pi_ip'])
    
    if not pi_ip:
        return jsonify({'error': 'Raspberry Pi IP address not configured'}), 400
    
    try:
        # Save code locally first
        local_path = f"/tmp/{filename}"
        with open(local_path, 'w') as f:
            f.write(code)
        
        # Deploy to Pi using SCP
        scp_command = f"scp {local_path} {prototyping_system.deployment_config['pi_user']}@{pi_ip}:/home/{prototyping_system.deployment_config['pi_user']}/"
        result = subprocess.run(scp_command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Optionally run the code on Pi
            if data.get('auto_run', False):
                ssh_command = f"ssh {prototyping_system.deployment_config['pi_user']}@{pi_ip} 'python3 {filename}'"
                run_result = subprocess.run(ssh_command, shell=True, capture_output=True, text=True)
                
                return jsonify({
                    'success': True,
                    'message': f'Code deployed and running on Pi at {pi_ip}',
                    'output': run_result.stdout,
                    'errors': run_result.stderr
                })
            else:
                return jsonify({
                    'success': True,
                    'message': f'Code deployed to Pi at {pi_ip}',
                    'path': f"/home/{prototyping_system.deployment_config['pi_user']}/{filename}"
                })
        else:
            return jsonify({'error': f'Deployment failed: {result.stderr}'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Deployment error: {str(e)}'}), 500

@app.route('/api/nlp/process', methods=['POST'])
def process_natural_language():
    """Process natural language input and generate project"""
    data = request.json
    user_input = data.get('input', '')
    
    # Use our NLP processor
    result = prototyping_system.nlp_processor.process_request(user_input)
    
    return jsonify(result)

# Additional helper methods for PrototypingSystem
def check_pin_conflicts(self, component_name, pin_assignment):
    """Check for pin conflicts using our analysis data"""
    conflicts = []
    current_pins = {}
    
    # Collect currently used pins
    for component in self.breadboard_state['components']:
        for pin_type, pin_num in component.get('pins', {}).items():
            if pin_num in current_pins:
                current_pins[pin_num].append(f"{component['name']}.{pin_type}")
            else:
                current_pins[pin_num] = [f"{component['name']}.{pin_type}"]
    
    # Check new component's pins
    for pin_type, pin_num in pin_assignment.items():
        if pin_num in current_pins:
            conflicts.append({
                'pin': pin_num,
                'current_use': current_pins[pin_num],
                'new_use': f"{component_name}.{pin_type}",
                'severity': 'error'
            })
    
    return conflicts

def generate_assembly_guide(self, component_name):
    """Generate step-by-step assembly guide"""
    components = self.component_db.get('component_mapping', {})
    if component_name not in components:
        return None
    
    component = components[component_name]
    
    guide = {
        'title': f"Assembly Guide: {component_name}",
        'complexity': component.get('complexity', 1),
        'estimated_time': f"{component.get('complexity', 1) * 5} minutes",
        'required_components': [component_name],
        'steps': []
    }
    
    # Generate steps based on component type
    if 'pins_used' in component:
        guide['steps'].append({
            'step': 1,
            'description': f"Connect {component_name} to Raspberry Pi",
            'details': f"Use pins: {', '.join(component['pins_used'])}",
            'image': f"/static/assembly/{component_name.lower()}_step1.png"
        })
    
    if 'common_patterns' in component:
        guide['steps'].append({
            'step': 2,
            'description': "Test basic functionality",
            'details': f"Try: {component['common_patterns'][0]}",
            'code_snippet': component['common_patterns'][0]
        })
    
    return guide

def get_component_complexity(self, component_name):
    """Get complexity level from our analysis"""
    components = self.component_db.get('component_mapping', {})
    if component_name in components:
        return components[component_name].get('complexity', 1)
    return 1

def customize_code_with_pins(self, code, pin_assignments):
    """Customize generated code with actual pin assignments"""
    customized = code
    
    # Replace generic pin numbers with actual assignments
    for component, pins in pin_assignments.items():
        if isinstance(pins, dict):
            for pin_type, pin_num in pins.items():
                # Replace common patterns
                customized = customized.replace(f"pin", str(pin_num))
                customized = customized.replace(f"{pin_type}_pin", str(pin_num))
        elif isinstance(pins, (int, str)):
            customized = customized.replace("pin", str(pins))
    
    return customized

def generate_project_code(self):
    """Generate complete project code from current breadboard state"""
    current_components = [c['name'] for c in self.breadboard_state['components']]
    if not current_components:
        return ""
    
    return self.code_completion.generate_code_template(current_components)

# Add methods to PrototypingSystem class
PrototypingSystem.check_pin_conflicts = check_pin_conflicts
PrototypingSystem.generate_assembly_guide = generate_assembly_guide
PrototypingSystem.get_component_complexity = get_component_complexity
PrototypingSystem.customize_code_with_pins = customize_code_with_pins
PrototypingSystem.generate_project_code = generate_project_code

class NaturalLanguageProcessor:
    """Natural language processing for project creation"""
    
    def __init__(self, component_db, code_completion):
        self.component_db = component_db
        self.code_completion = code_completion
        self.intent_mapping = self.build_intent_mapping()
    
    def build_intent_mapping(self):
        """Build intent-to-component mapping from our analysis"""
        return {
            # Temperature monitoring
            'temperature': ['DHT11', 'LCD1602', 'LED'],
            'humidity': ['DHT11', 'LCD1602'],
            'weather': ['DHT11', 'BMP180_Barometer', 'LCD1602'],
            
            # Motion and distance
            'motion': ['PIR_Sensor', 'LED', 'Buzzer'],
            'distance': ['DistanceSensor', 'LED', 'LCD1602'],
            'security': ['PIR_Sensor', 'Camera_Module', 'Buzzer'],
            
            # Lighting
            'light': ['LED', 'Button', 'Photoresistor'],
            'rgb': ['RGBLED', 'Button', 'ADC'],
            'strip': ['WS2812_LED_Strip', 'Button'],
            
            # Motor control
            'motor': ['Motor', 'Button', 'DistanceSensor'],
            'servo': ['Servo', 'Button', 'Rotary_Encoder'],
            'robot': ['Motor', 'DistanceSensor', 'Camera_Module'],
            
            # Data logging
            'log': ['DHT11', 'BMP180_Barometer', 'ADC'],
            'monitor': ['Camera_Module', 'DHT11', 'PIR_Sensor']
        }
    
    def process_request(self, user_input):
        """Process natural language request and generate project"""
        user_input = user_input.lower()
        
        # Find matching intents
        matched_components = set()
        matched_intents = []
        
        for intent, components in self.intent_mapping.items():
            if intent in user_input:
                matched_components.update(components)
                matched_intents.append(intent)
        
        if not matched_components:
            return {
                'error': 'Could not understand request',
                'suggestions': list(self.intent_mapping.keys())
            }
        
        # Generate project
        components = list(matched_components)
        pin_assignments = self.code_completion.suggest_pin_assignments(components)
        generated_code = self.code_completion.generate_code_template(components)
        
        return {
            'success': True,
            'understood_intents': matched_intents,
            'selected_components': components,
            'pin_assignments': pin_assignments,
            'generated_code': generated_code,
            'assembly_guides': [prototyping_system.generate_assembly_guide(comp) for comp in components],
            'next_suggestions': self.code_completion.suggest_next_component(components)
        }

if __name__ == '__main__':
    print("🚀 Starting Advanced Raspberry Pi Prototyping System")
    print("📊 Loading comprehensive analysis data...")
    print("🔧 Initializing intelligent systems...")
    
    # Create templates directory
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/assembly', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)