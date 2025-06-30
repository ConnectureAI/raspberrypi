#!/usr/bin/env python3
"""
Intelligent Code Completion System
Based on component combinations and patterns from Raspberry Pi Starter Kit

This system provides smart code suggestions based on:
1. Component combinations detected
2. Common usage patterns
3. Best practices from analyzed projects
"""

import json
import re
from typing import List, Dict, Tuple, Optional

class SmartCodeCompletion:
    """Intelligent code completion based on component analysis"""
    
    def __init__(self):
        self.component_patterns = self._load_component_patterns()
        self.common_combinations = self._load_common_combinations()
        self.import_suggestions = self._load_import_suggestions()
    
    def _load_component_patterns(self) -> Dict:
        """Load component-specific code patterns"""
        return {
            "LED": {
                "imports": ["from gpiozero import LED"],
                "init": "led = LED({pin})",
                "methods": ["led.on()", "led.off()", "led.blink()", "led.pulse()"],
                "common_pins": [17, 18, 27],
                "cleanup": "# LED automatically cleaned up"
            },
            "RGBLED": {
                "imports": ["from gpiozero import RGBLED"],
                "init": "led = RGBLED(red={red_pin}, green={green_pin}, blue={blue_pin}, active_high=False)",
                "methods": ["led.red = value/100", "led.green = value/100", "led.blue = value/100", "led.color = (r, g, b)"],
                "common_pins": {"red": 17, "green": 18, "blue": 27},
                "cleanup": "led.close()"
            },
            "Button": {
                "imports": ["from gpiozero import Button"],
                "init": "button = Button({pin})",
                "methods": ["button.is_pressed", "button.wait_for_press()", "button.when_pressed = function"],
                "common_pins": [18, 2, 3],
                "cleanup": "# Button automatically cleaned up"
            },
            "Motor": {
                "imports": ["from gpiozero import Motor"],
                "init": "motor = Motor(forward={forward_pin}, backward={backward_pin})",
                "methods": ["motor.forward(speed)", "motor.backward(speed)", "motor.stop()"],
                "common_pins": {"forward": 18, "backward": 19},
                "cleanup": "motor.stop()"
            },
            "Servo": {
                "imports": ["from gpiozero import Servo"],
                "init": "servo = Servo({pin})",
                "methods": ["servo.min()", "servo.max()", "servo.mid()", "servo.value = angle"],
                "common_pins": [17, 18],
                "cleanup": "servo.close()"
            },
            "DistanceSensor": {
                "imports": ["from gpiozero import DistanceSensor"],
                "init": "sensor = DistanceSensor(echo={echo_pin}, trigger={trigger_pin})",
                "methods": ["sensor.distance", "sensor.when_in_range = function", "sensor.when_out_of_range = function"],
                "common_pins": {"echo": 21, "trigger": 20},
                "cleanup": "# Sensor automatically cleaned up"
            },
            "ADC": {
                "imports": ["from ADCDevice import ADCDevice, PCF8591, ADS7830"],
                "init": """adc = ADCDevice()
if adc.detectI2C(0x48): adc = PCF8591()
elif adc.detectI2C(0x4b): adc = ADS7830()""",
                "methods": ["value = adc.analogRead(channel)", "voltage = value / 255.0 * 3.3"],
                "i2c_addresses": ["0x48", "0x4b"],
                "cleanup": "adc.close()"
            },
            "DHT11": {
                "imports": ["from Freenove_DHT import DHT"],
                "init": "dht = DHT({pin})",
                "methods": ["result = dht.readDHT11()", "temperature = dht.getTemperature()", "humidity = dht.getHumidity()"],
                "common_pins": [17, 18],
                "cleanup": "# DHT11 automatically cleaned up"
            },
            "LCD1602": {
                "imports": ["from LCD1602 import LCD1602"],
                "init": "lcd = LCD1602()",
                "methods": ["lcd.write(row, col, text)", "lcd.clear()", "lcd.backlight()"],
                "i2c_addresses": ["0x27", "0x3F"],
                "cleanup": "# LCD automatically cleaned up"
            }
        }
    
    def _load_common_combinations(self) -> Dict:
        """Load common component combinations and their patterns"""
        return {
            ("LED", "Button"): {
                "description": "Button-controlled LED",
                "template": """from gpiozero import LED, Button

led = LED(17)
button = Button(18)

while True:
    if button.is_pressed:
        led.on()
    else:
        led.off()""",
                "complexity": 1
            },
            ("LED", "ADC"): {
                "description": "Sensor-controlled LED brightness",
                "template": """from gpiozero import PWMLED
from ADCDevice import *

led = PWMLED(17)
adc = ADCDevice()
if adc.detectI2C(0x48): adc = PCF8591()

while True:
    value = adc.analogRead(0)
    brightness = value / 255.0
    led.value = brightness""",
                "complexity": 3
            },
            ("RGBLED", "ADC"): {
                "description": "Sensor-controlled RGB LED colors",
                "template": """from gpiozero import RGBLED
from ADCDevice import *
import random

led = RGBLED(red=17, green=18, blue=27, active_high=False)
adc = ADCDevice()
if adc.detectI2C(0x48): adc = PCF8591()

while True:
    value = adc.analogRead(0)
    if value > 128:
        # High sensor value - random colors
        led.red = random.random()
        led.green = random.random()
        led.blue = random.random()
    else:
        led.off()""",
                "complexity": 4
            },
            ("Motor", "Button"): {
                "description": "Button-controlled motor",
                "template": """from gpiozero import Motor, Button

motor = Motor(forward=18, backward=19)
button_forward = Button(2)
button_backward = Button(3)

while True:
    if button_forward.is_pressed:
        motor.forward()
    elif button_backward.is_pressed:
        motor.backward()
    else:
        motor.stop()""",
                "complexity": 3
            },
            ("DistanceSensor", "LED"): {
                "description": "Distance-based LED control",
                "template": """from gpiozero import DistanceSensor, LED

sensor = DistanceSensor(echo=21, trigger=20)
led = LED(17)

while True:
    distance = sensor.distance * 100  # Convert to cm
    if distance < 20:
        led.on()
    else:
        led.off()""",
                "complexity": 3
            }
        }
    
    def _load_import_suggestions(self) -> Dict:
        """Load intelligent import suggestions"""
        return {
            "time": ["time.sleep()", "time.time()"],
            "random": ["random.randint()", "random.random()", "random.choice()"],
            "gpiozero": ["LED", "Button", "RGBLED", "Motor", "Servo", "DistanceSensor", "PWMLED"],
            "ADCDevice": ["ADCDevice", "PCF8591", "ADS7830"]
        }
    
    def suggest_imports(self, code_content: str) -> List[str]:
        """Suggest imports based on code content"""
        suggestions = []
        
        # Check for GPIO Zero components
        gpiozero_components = ["LED", "Button", "RGBLED", "Motor", "Servo", "DistanceSensor", "PWMLED"]
        found_components = [comp for comp in gpiozero_components if comp in code_content]
        if found_components:
            suggestions.append(f"from gpiozero import {', '.join(found_components)}")
        
        # Check for time functions
        if any(func in code_content for func in ["sleep", "time()"]):
            suggestions.append("import time")
        
        # Check for random functions
        if any(func in code_content for func in ["randint", "random()", "choice"]):
            suggestions.append("import random")
        
        # Check for ADC usage
        if any(adc in code_content for adc in ["ADCDevice", "PCF8591", "ADS7830"]):
            suggestions.append("from ADCDevice import ADCDevice, PCF8591, ADS7830")
        
        return suggestions
    
    def detect_components(self, code_content: str) -> List[str]:
        """Detect components being used in code"""
        components = []
        
        patterns = {
            "LED": r"LED\(\d+\)",
            "RGBLED": r"RGBLED\(",
            "Button": r"Button\(\d+\)",
            "Motor": r"Motor\(",
            "Servo": r"Servo\(\d+\)",
            "DistanceSensor": r"DistanceSensor\(",
            "ADC": r"(PCF8591|ADS7830|ADCDevice)",
            "DHT11": r"DHT\(\d+\)"
        }
        
        for component, pattern in patterns.items():
            if re.search(pattern, code_content):
                components.append(component)
        
        return components
    
    def suggest_next_component(self, current_components: List[str]) -> List[Dict]:
        """Suggest next components based on current ones"""
        suggestions = []
        
        # Common progression paths
        progressions = {
            "LED": ["Button", "ADC", "RGBLED"],
            "Button": ["LED", "Motor", "Servo"],
            "ADC": ["LED", "RGBLED", "LCD1602"],
            "Motor": ["Button", "DistanceSensor", "Encoder"],
            "DistanceSensor": ["LED", "Motor", "Buzzer"]
        }
        
        for component in current_components:
            if component in progressions:
                for next_comp in progressions[component]:
                    if next_comp not in current_components:
                        suggestions.append({
                            "component": next_comp,
                            "reason": f"Commonly used with {component}",
                            "complexity": self._get_component_complexity(next_comp)
                        })
        
        return suggestions
    
    def _get_component_complexity(self, component: str) -> int:
        """Get complexity level of component (1-5)"""
        complexity_map = {
            "LED": 1, "Button": 1,
            "RGBLED": 2, "Buzzer": 2,
            "ADC": 3, "Motor": 3, "Servo": 3,
            "DistanceSensor": 3, "LCD1602": 4,
            "DHT11": 4, "MPU6050": 5, "RFID": 5
        }
        return complexity_map.get(component, 3)
    
    def generate_code_template(self, components: List[str]) -> str:
        """Generate complete code template for given components"""
        template_parts = []
        
        # Header
        template_parts.append("#!/usr/bin/env python3")
        template_parts.append('"""')
        template_parts.append(f"Project: {' + '.join(components)} Control")
        template_parts.append(f"Components: {', '.join(components)}")
        template_parts.append('"""')
        template_parts.append("")
        
        # Imports
        imports = set()
        for component in components:
            if component in self.component_patterns:
                pattern = self.component_patterns[component]
                imports.update(pattern.get("imports", []))
        
        imports.add("import time")
        for imp in sorted(imports):
            template_parts.append(imp)
        template_parts.append("")
        
        # Component initialization
        template_parts.append("# Component initialization")
        for component in components:
            if component in self.component_patterns:
                pattern = self.component_patterns[component]
                init_code = pattern.get("init", f"# Initialize {component}")
                template_parts.append(init_code)
        template_parts.append("")
        
        # Main functions
        template_parts.append("def setup():")
        template_parts.append('    """Initialize hardware components"""')
        template_parts.append("    print('Hardware setup complete')")
        template_parts.append("")
        
        template_parts.append("def loop():")
        template_parts.append('    """Main execution loop"""')
        template_parts.append("    while True:")
        template_parts.append("        # Add your main logic here")
        
        # Add component-specific methods as comments
        for component in components:
            if component in self.component_patterns:
                pattern = self.component_patterns[component]
                methods = pattern.get("methods", [])
                if methods:
                    template_parts.append(f"        # {component} methods:")
                    for method in methods[:2]:  # Show first 2 methods
                        template_parts.append(f"        # {method}")
        
        template_parts.append("        time.sleep(0.1)")
        template_parts.append("")
        
        template_parts.append("def cleanup():")
        template_parts.append('    """Clean up resources"""')
        for component in components:
            if component in self.component_patterns:
                pattern = self.component_patterns[component]
                cleanup = pattern.get("cleanup", f"# Cleanup {component}")
                template_parts.append(f"    {cleanup}")
        template_parts.append('    print("Cleanup complete")')
        template_parts.append("")
        
        # Main execution
        template_parts.append("if __name__ == '__main__':")
        template_parts.append("    print('Starting project...')")
        template_parts.append("    try:")
        template_parts.append("        setup()")
        template_parts.append("        loop()")
        template_parts.append("    except KeyboardInterrupt:")
        template_parts.append('        print("\\nProgram interrupted by user")')
        template_parts.append("    finally:")
        template_parts.append("        cleanup()")
        
        return "\n".join(template_parts)
    
    def suggest_pin_assignments(self, components: List[str]) -> Dict[str, Dict]:
        """Suggest optimal pin assignments for components"""
        suggestions = {}
        used_pins = set()
        
        # Priority pins for each component type
        pin_priorities = {
            "LED": [17, 18, 27, 22],
            "Button": [18, 2, 3, 4],
            "Motor": {"forward": [18, 19], "backward": [19, 20]},
            "Servo": [17, 18, 27],
            "RGBLED": {"red": 17, "green": 18, "blue": 27},
            "DistanceSensor": {"trigger": 20, "echo": 21}
        }
        
        for component in components:
            if component in pin_priorities:
                priority = pin_priorities[component]
                
                if isinstance(priority, list):
                    # Single pin component
                    for pin in priority:
                        if pin not in used_pins:
                            suggestions[component] = {"pin": pin}
                            used_pins.add(pin)
                            break
                elif isinstance(priority, dict):
                    # Multi-pin component
                    component_pins = {}
                    for pin_type, pin_options in priority.items():
                        if isinstance(pin_options, list):
                            for pin in pin_options:
                                if pin not in used_pins:
                                    component_pins[pin_type] = pin
                                    used_pins.add(pin)
                                    break
                        else:
                            if pin_options not in used_pins:
                                component_pins[pin_type] = pin_options
                                used_pins.add(pin_options)
                    
                    if component_pins:
                        suggestions[component] = component_pins
        
        return suggestions
    
    def get_learning_path(self, current_skill_level: int = 1) -> List[Dict]:
        """Generate learning path based on skill level"""
        learning_paths = {
            1: [  # Beginner
                {"component": "LED", "description": "Basic output control"},
                {"component": "Button", "description": "Basic input reading"},
                {"component": "LED + Button", "description": "Input/output combination"}
            ],
            2: [  # Intermediate
                {"component": "RGBLED", "description": "Multi-channel output"},
                {"component": "ADC", "description": "Analog sensor reading"},
                {"component": "Motor", "description": "Movement control"}
            ],
            3: [  # Advanced
                {"component": "DistanceSensor", "description": "Sensor integration"},
                {"component": "DHT11", "description": "Environmental sensing"},
                {"component": "LCD1602", "description": "Display output"}
            ]
        }
        
        return learning_paths.get(current_skill_level, [])

# Example usage and testing
if __name__ == "__main__":
    completion = SmartCodeCompletion()
    
    # Test component detection
    test_code = """
    from gpiozero import LED, Button
    led = LED(17)
    button = Button(18)
    """
    
    print("Detected components:", completion.detect_components(test_code))
    print("Import suggestions:", completion.suggest_imports(test_code))
    
    # Test template generation
    template = completion.generate_code_template(["LED", "Button"])
    print("\nGenerated template:")
    print(template)
    
    # Test pin suggestions
    pins = completion.suggest_pin_assignments(["LED", "Button", "Motor"])
    print("\nPin suggestions:", pins)