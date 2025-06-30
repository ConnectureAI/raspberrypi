#!/usr/bin/env python3
"""
Advanced Real-Time Raspberry Pi Prototyping System
Demo Script

This script demonstrates the key capabilities of the system:
- Natural language project creation
- Smart component suggestions
- Code generation from analysis patterns
- Assembly guide creation
- Deployment pipeline
"""

import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from smart_code_completion import SmartCodeCompletion
    from advanced_nlp import AdvancedNLPProcessor
    from deployment_engine import DeploymentEngine, InstantCodeGenerator
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure you're running from the correct directory")
    sys.exit(1)

class SystemDemo:
    """Demonstrates the prototyping system capabilities"""
    
    def __init__(self):
        self.load_demo_data()
        self.setup_components()
    
    def load_demo_data(self):
        """Load component database for demo"""
        try:
            # Try to load real component database
            mapping_path = Path(__file__).parent.parent / 'component_code_mapping.json'
            if mapping_path.exists():
                with open(mapping_path, 'r') as f:
                    self.component_db = json.load(f)
            else:
                # Use demo data
                self.component_db = self.create_demo_component_db()
        except:
            self.component_db = self.create_demo_component_db()
    
    def create_demo_component_db(self):
        """Create demo component database"""
        return {
            "component_mapping": {
                "LED": {
                    "examples": ["01.1.1_Blink", "02.1.1_ButtonLED"],
                    "pins_used": ["GPIO17"],
                    "complexity": 1,
                    "libraries": ["gpiozero.LED"],
                    "common_patterns": ["led.on()", "led.off()", "led.blink()"]
                },
                "Button": {
                    "examples": ["02.1.1_ButtonLED"],
                    "pins_used": ["GPIO18"],
                    "complexity": 1,
                    "libraries": ["gpiozero.Button"],
                    "common_patterns": ["button.is_pressed", "button.wait_for_press()"]
                },
                "DHT11": {
                    "examples": ["21.1.1_DHT11"],
                    "pins_used": ["GPIO17"],
                    "complexity": 3,
                    "libraries": ["Freenove_DHT.DHT"],
                    "common_patterns": ["dht.readDHT11()", "dht.getTemperature()", "dht.getHumidity()"]
                },
                "LCD1602": {
                    "examples": ["20.1.1_I2CLCD1602"],
                    "pins_used": ["GPIO2", "GPIO3"],
                    "complexity": 4,
                    "libraries": ["LCD1602.LCD1602"],
                    "i2c_address": "0x27",
                    "common_patterns": ["lcd.write()", "lcd.clear()"]
                },
                "Ultrasonic_HC_SR04": {
                    "examples": ["24.1.1_UltrasonicRanging"],
                    "pins_used": ["GPIO20", "GPIO21"],
                    "complexity": 3,
                    "libraries": ["gpiozero.DistanceSensor"],
                    "common_patterns": ["sensor.distance", "distance measurement"]
                },
                "PIR_Sensor": {
                    "examples": ["23.1.1_SenseLED"],
                    "pins_used": ["GPIO17"],
                    "complexity": 2,
                    "libraries": ["gpiozero.MotionSensor"],
                    "common_patterns": ["pir.motion_detected", "pir.when_motion"]
                },
                "Motor_DC": {
                    "examples": ["13.1.1_Motor"],
                    "pins_used": ["GPIO18", "GPIO19"],
                    "complexity": 4,
                    "libraries": ["gpiozero.Motor"],
                    "common_patterns": ["motor.forward()", "motor.backward()", "motor.stop()"]
                },
                "Camera_Module": {
                    "examples": ["36.1.1_Camera"],
                    "pins_used": ["Camera connector"],
                    "complexity": 6,
                    "libraries": ["picamera"],
                    "common_patterns": ["camera.capture()", "camera.start_preview()"]
                }
            }
        }
    
    def setup_components(self):
        """Initialize system components"""
        print("🧠 Initializing system components...")
        
        self.code_completion = SmartCodeCompletion()
        self.nlp_processor = AdvancedNLPProcessor(self.component_db, self.code_completion)
        self.deployment_engine = DeploymentEngine(self.component_db, self.code_completion)
        self.code_generator = InstantCodeGenerator(self.component_db, self.code_completion)
        
        print("✅ System components ready!")
    
    def demo_natural_language_interface(self):
        """Demonstrate natural language project creation"""
        print("\n" + "="*60)
        print("🗣️  NATURAL LANGUAGE INTERFACE DEMO")
        print("="*60)
        
        test_projects = [
            "Build a temperature monitor with LCD display",
            "Create a motion detection alarm system", 
            "Make a distance sensor with LED indicator",
            "Build a robot car with obstacle avoidance"
        ]
        
        for project_description in test_projects:
            print(f"\n📝 Input: '{project_description}'")
            print("-" * 50)
            
            result = self.nlp_processor.process_natural_language(project_description)
            
            if result['success']:
                print("✅ Project understood!")
                print(f"🎯 Intent: {result['understood_intent'].action} {result['understood_intent'].target}")
                print(f"🔧 Components: {[c['name'] for c in result['selected_components']]}")
                print(f"📍 Pin assignments: {result['pin_assignments']}")
                print(f"⏱️  Estimated time: {result['estimated_time']}")
                print(f"📊 Difficulty: Level {result['difficulty_level']}")
            else:
                print("❌ Could not understand project")
                print(f"💡 Suggestions: {result.get('suggestions', [])}")
    
    def demo_smart_code_completion(self):
        """Demonstrate smart code completion"""
        print("\n" + "="*60)
        print("🧠 SMART CODE COMPLETION DEMO")
        print("="*60)
        
        # Test component detection
        test_code = '''
from gpiozero import LED, Button
led = LED(17)
button = Button(18)
'''
        
        print("📄 Analyzing code:")
        print(test_code)
        print("-" * 30)
        
        detected = self.code_completion.detect_components(test_code)
        print(f"🔍 Detected components: {detected}")
        
        imports = self.code_completion.suggest_imports(test_code)
        print(f"📦 Import suggestions: {imports}")
        
        # Test template generation
        print("\n🏗️  Generating template for LED + Button + DHT11:")
        template = self.code_completion.generate_code_template(['LED', 'Button', 'DHT11'])
        print("Generated template (first 20 lines):")
        print('-' * 40)
        for i, line in enumerate(template.split('\n')[:20]):
            print(f"{i+1:2d}: {line}")
        print("... (truncated)")
        
        # Test pin suggestions
        pin_suggestions = self.code_completion.suggest_pin_assignments(['LED', 'Button', 'DHT11'])
        print(f"\n📍 Pin suggestions: {pin_suggestions}")
    
    def demo_component_analysis(self):
        """Demonstrate component analysis capabilities"""
        print("\n" + "="*60)
        print("📊 COMPONENT ANALYSIS DEMO")
        print("="*60)
        
        print(f"📦 Total components in database: {len(self.component_db['component_mapping'])}")
        print("\n🏷️  Component complexity levels:")
        
        complexity_levels = {}
        for name, comp in self.component_db['component_mapping'].items():
            level = comp.get('complexity', 1)
            if level not in complexity_levels:
                complexity_levels[level] = []
            complexity_levels[level].append(name)
        
        for level in sorted(complexity_levels.keys()):
            components = complexity_levels[level]
            print(f"  Level {level}: {', '.join(components)}")
        
        print("\n🔌 Pin usage analysis:")
        pin_usage = {}
        for name, comp in self.component_db['component_mapping'].items():
            pins = comp.get('pins_used', [])
            for pin in pins:
                if pin not in pin_usage:
                    pin_usage[pin] = []
                pin_usage[pin].append(name)
        
        for pin in sorted(pin_usage.keys())[:5]:  # Show top 5
            components = pin_usage[pin]
            print(f"  {pin}: {', '.join(components)}")
    
    async def demo_deployment_pipeline(self):
        """Demonstrate deployment pipeline"""
        print("\n" + "="*60)
        print("🚀 DEPLOYMENT PIPELINE DEMO")
        print("="*60)
        
        # Demo Pi discovery
        print("🔍 Discovering Raspberry Pi devices...")
        try:
            devices = await self.deployment_engine.discover_pi_devices()
            if devices:
                print(f"✅ Found {len(devices)} devices:")
                for device in devices:
                    print(f"  • {device['address']} - {device.get('hostname', 'Unknown')}")
            else:
                print("ℹ️  No Pi devices found (this is normal if none are connected)")
        except Exception as e:
            print(f"⚠️  Discovery simulation (no network access): {e}")
        
        # Demo code generation
        print("\n🏗️  Generating deployment-ready code...")
        project_config = {
            'components': [
                {'name': 'LED', 'pins': {'pin': 17}},
                {'name': 'Button', 'pins': {'pin': 18}}
            ],
            'enable_logging': True,
            'enable_monitoring': True,
            'auto_run': True
        }
        
        code_result = await self.code_generator.generate_optimized_code(project_config)
        if code_result['success']:
            print("✅ Code generated successfully!")
            print(f"📄 Filename: {code_result['filename']}")
            print(f"📦 Dependencies: {code_result['dependencies']}")
            print(f"⏱️  Estimated runtime: {code_result['estimated_runtime']} seconds")
            print("\n🔍 Generated code preview (first 15 lines):")
            print("-" * 40)
            for i, line in enumerate(code_result['code'].split('\n')[:15]):
                print(f"{i+1:2d}: {line}")
            print("... (truncated)")
        else:
            print(f"❌ Code generation failed: {code_result['error']}")
    
    def demo_assembly_guides(self):
        """Demonstrate assembly guide generation"""
        print("\n" + "="*60)
        print("🔧 ASSEMBLY GUIDE DEMO")
        print("="*60)
        
        # Create a sample project
        project_description = "Build a temperature monitor with LCD display"
        result = self.nlp_processor.process_natural_language(project_description)
        
        if result['success'] and 'assembly_guide' in result:
            guide = result['assembly_guide']
            print(f"📋 Project: {guide['title']}")
            print(f"⏱️  Estimated time: {guide['estimated_time']}")
            print(f"📊 Difficulty: Level {guide['difficulty']}")
            print(f"🔧 Required components: {', '.join(guide['required_components'])}")
            print(f"🛠️  Tools needed: {', '.join(guide['tools_needed'])}")
            
            print("\n📝 Assembly steps:")
            for step in guide['steps'][:3]:  # Show first 3 steps
                print(f"\n  Step {step['step']}: {step['title']}")
                print(f"    Description: {step['description']}")
                if 'estimated_time' in step:
                    print(f"    Time: {step['estimated_time']}")
                if 'warnings' in step and step['warnings']:
                    print(f"    ⚠️  Warnings: {step['warnings'][0]}")
            
            if len(guide['steps']) > 3:
                print(f"    ... and {len(guide['steps']) - 3} more steps")
        else:
            print("❌ Could not generate assembly guide for demo project")
    
    def demo_learning_pathways(self):
        """Demonstrate learning pathway recommendations"""
        print("\n" + "="*60)
        print("🎓 LEARNING PATHWAYS DEMO")
        print("="*60)
        
        skill_levels = [1, 2, 3]
        level_names = ["Beginner", "Intermediate", "Advanced"]
        
        for level, name in zip(skill_levels, level_names):
            path = self.code_completion.get_learning_path(level)
            print(f"\n📚 {name} Path (Level {level}):")
            for item in path:
                print(f"  • {item['component']}: {item['description']}")
    
    def run_complete_demo(self):
        """Run the complete system demo"""
        print("🚀 ADVANCED RASPBERRY PI PROTOTYPING SYSTEM")
        print("🤖 COMPREHENSIVE DEMO")
        print("="*60)
        print("This demo showcases the advanced prototyping system built on")
        print("comprehensive analysis of 35+ components and 100+ code files.")
        print("="*60)
        
        try:
            # Component analysis
            self.demo_component_analysis()
            
            # Natural language interface
            self.demo_natural_language_interface()
            
            # Smart code completion
            self.demo_smart_code_completion()
            
            # Assembly guides
            self.demo_assembly_guides()
            
            # Learning pathways
            self.demo_learning_pathways()
            
            # Deployment pipeline (async)
            print("\n⏳ Running deployment pipeline demo...")
            asyncio.run(self.demo_deployment_pipeline())
            
            print("\n" + "="*60)
            print("✅ DEMO COMPLETED SUCCESSFULLY!")
            print("="*60)
            print("🎯 Key Capabilities Demonstrated:")
            print("  • Natural language project creation")
            print("  • Smart component suggestions")
            print("  • Intelligent code generation")
            print("  • Assembly guide creation")
            print("  • Pin conflict detection")
            print("  • Deployment pipeline")
            print("  • Learning pathway optimization")
            print("\n🚀 Ready to start building? Run: python start_system.py")
            print("🌐 Then open: http://localhost:5000")
            
        except Exception as e:
            print(f"\n❌ Demo error: {e}")
            print("This is likely due to missing dependencies.")
            print("Install with: pip install -r requirements.txt")

def main():
    """Main demo function"""
    demo = SystemDemo()
    demo.run_complete_demo()

if __name__ == '__main__':
    main()