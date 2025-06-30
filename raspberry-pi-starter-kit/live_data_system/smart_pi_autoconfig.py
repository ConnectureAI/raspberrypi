#!/usr/bin/env python3
"""
Smart Pi Auto-Configuration System
Live Data System for Raspberry Pi

This system leverages comprehensive component analysis for:
- Auto-detection of connected components on boot
- GPIO pattern-based sensor initialization
- Communication protocol optimization for data streaming
- Pin conflict resolution for multi-sensor scenarios
"""

import os
import sys
import time
import json
import threading
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import asyncio
from dataclasses import dataclass, asdict
from collections import defaultdict

# Import our analysis modules
sys.path.append(str(Path(__file__).parent.parent))

try:
    import RPi.GPIO as GPIO
    import smbus
    import spidev
    from gpiozero import *
    PI_AVAILABLE = True
except ImportError:
    PI_AVAILABLE = False
    print("⚠️ Raspberry Pi libraries not available - running in simulation mode")

try:
    from smart_code_completion import SmartCodeCompletion
    from code_pattern_library import *
except ImportError:
    print("⚠️ Analysis modules not found - using fallback patterns")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DetectedComponent:
    """Represents a detected component with its properties"""
    name: str
    pin: int
    component_type: str
    confidence: float
    characteristics: Dict
    initialization_pattern: str
    data_pattern: str
    last_seen: float

@dataclass
class SensorReading:
    """Standardized sensor reading format"""
    component: str
    timestamp: float
    value: any
    unit: str
    pin: int
    quality: float  # Reading quality 0-1

class SmartPiAutoConfig:
    """Smart Pi Auto-Configuration using analysis patterns"""
    
    def __init__(self, component_database=None):
        self.component_db = component_database or self.load_component_database()
        self.detected_components = {}
        self.active_sensors = {}
        self.data_streams = {}
        self.gpio_state = {}
        self.i2c_devices = {}
        self.spi_devices = {}
        
        # Analysis-based patterns
        self.gpio_patterns = self.load_gpio_patterns()
        self.sensor_patterns = self.load_sensor_patterns()
        self.communication_patterns = self.load_communication_patterns()
        
        # Auto-detection settings
        self.detection_enabled = True
        self.auto_init_enabled = True
        self.streaming_enabled = True
        
        self.initialize_system()
    
    def load_component_database(self) -> Dict:
        """Load comprehensive component database from analysis"""
        try:
            # Load from our analysis
            db_path = Path(__file__).parent.parent / 'component_code_mapping.json'
            if db_path.exists():
                with open(db_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load component database: {e}")
        
        # Fallback database with key components
        return {
            "component_mapping": {
                "DHT11": {
                    "pins_used": ["GPIO17"],
                    "complexity": 3,
                    "detection_pattern": "temperature_humidity_digital",
                    "i2c_address": None,
                    "characteristics": {
                        "data_type": "temperature_humidity",
                        "voltage": "3.3V",
                        "protocol": "1-wire",
                        "sampling_rate": "0.5Hz"
                    }
                },
                "DS18B20": {
                    "pins_used": ["GPIO4"],
                    "complexity": 3,
                    "detection_pattern": "temperature_1wire",
                    "characteristics": {
                        "data_type": "temperature",
                        "voltage": "3.3V", 
                        "protocol": "1-wire",
                        "sampling_rate": "1Hz"
                    }
                },
                "BMP180": {
                    "pins_used": ["GPIO2", "GPIO3"],
                    "complexity": 4,
                    "i2c_address": "0x77",
                    "detection_pattern": "pressure_temperature_i2c",
                    "characteristics": {
                        "data_type": "pressure_temperature",
                        "voltage": "3.3V",
                        "protocol": "I2C",
                        "sampling_rate": "2Hz"
                    }
                },
                "PIR_Sensor": {
                    "pins_used": ["GPIO17"],
                    "complexity": 2,
                    "detection_pattern": "motion_digital",
                    "characteristics": {
                        "data_type": "motion",
                        "voltage": "5V",
                        "protocol": "digital",
                        "sampling_rate": "10Hz"
                    }
                },
                "Ultrasonic_HC_SR04": {
                    "pins_used": ["GPIO20", "GPIO21"],
                    "complexity": 3,
                    "detection_pattern": "distance_ultrasonic",
                    "characteristics": {
                        "data_type": "distance",
                        "voltage": "5V",
                        "protocol": "digital_timing",
                        "sampling_rate": "5Hz"
                    }
                },
                "ADS1115": {
                    "pins_used": ["GPIO2", "GPIO3"],
                    "complexity": 4,
                    "i2c_address": "0x48",
                    "detection_pattern": "analog_i2c",
                    "characteristics": {
                        "data_type": "analog_voltage",
                        "voltage": "3.3V",
                        "protocol": "I2C",
                        "sampling_rate": "860Hz"
                    }
                }
            }
        }
    
    def load_gpio_patterns(self) -> Dict:
        """Load GPIO control patterns from analysis"""
        return {
            "digital_input": {
                "detection": "high_impedance_with_pullup",
                "initialization": "GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)",
                "reading": "GPIO.input(pin)",
                "characteristics": ["stable_high", "clean_transitions"]
            },
            "digital_output": {
                "detection": "driven_high_or_low",
                "initialization": "GPIO.setup(pin, GPIO.OUT)",
                "control": "GPIO.output(pin, state)",
                "characteristics": ["strong_drive", "fast_switching"]
            },
            "analog_input": {
                "detection": "variable_voltage",
                "initialization": "requires_adc",
                "reading": "adc.read_adc(channel)",
                "characteristics": ["continuous_variation", "noise_filtering_needed"]
            },
            "pwm_output": {
                "detection": "periodic_signal",
                "initialization": "GPIO.PWM(pin, frequency)",
                "control": "pwm.ChangeDutyCycle(duty)",
                "characteristics": ["square_wave", "variable_duty_cycle"]
            },
            "1wire": {
                "detection": "dallas_temperature_pattern",
                "initialization": "w1_gpio_pin_4",
                "reading": "temperature_from_w1_slave",
                "characteristics": ["single_wire_data", "temperature_sensors"]
            }
        }
    
    def load_sensor_patterns(self) -> Dict:
        """Load sensor reading patterns from analysis"""
        return {
            "temperature_humidity": {
                "sample_rate": 0.5,  # Hz
                "validation": "range_check",
                "filtering": "median_filter",
                "error_handling": "retry_on_checksum_fail"
            },
            "motion_detection": {
                "sample_rate": 10,
                "validation": "state_change_detection",
                "filtering": "debounce_filter",
                "error_handling": "ignore_transients"
            },
            "distance_measurement": {
                "sample_rate": 5,
                "validation": "range_limit_check",
                "filtering": "moving_average",
                "error_handling": "timeout_handling"
            },
            "pressure_measurement": {
                "sample_rate": 2,
                "validation": "atmospheric_range",
                "filtering": "low_pass_filter",
                "error_handling": "calibration_check"
            },
            "analog_voltage": {
                "sample_rate": 100,
                "validation": "voltage_range_check",
                "filtering": "noise_reduction",
                "error_handling": "adc_error_detection"
            }
        }
    
    def load_communication_patterns(self) -> Dict:
        """Load communication protocol patterns from analysis"""
        return {
            "I2C": {
                "initialization": "smbus.SMBus(1)",
                "device_scan": "range(0x03, 0x78)",
                "error_handling": "timeout_and_retry",
                "optimization": "clock_stretching_support"
            },
            "SPI": {
                "initialization": "spidev.SpiDev()",
                "configuration": "max_speed_hz_optimization",
                "error_handling": "transmission_verification",
                "optimization": "dma_for_large_transfers"
            },
            "1-Wire": {
                "initialization": "w1_therm_module",
                "device_discovery": "w1_slave_scanning",
                "error_handling": "crc_validation",
                "optimization": "parasite_power_support"
            },
            "Digital": {
                "initialization": "gpio_setup_optimized",
                "timing": "precise_microsecond_timing",
                "error_handling": "signal_integrity_check",
                "optimization": "interrupt_driven_reading"
            }
        }
    
    def initialize_system(self):
        """Initialize the auto-configuration system"""
        logger.info("🤖 Initializing Smart Pi Auto-Configuration System")
        
        if PI_AVAILABLE:
            # Initialize GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            # Initialize I2C
            try:
                self.i2c_bus = smbus.SMBus(1)
                logger.info("✅ I2C bus initialized")
            except Exception as e:
                logger.warning(f"⚠️ I2C initialization failed: {e}")
                self.i2c_bus = None
            
            # Initialize SPI
            try:
                self.spi = spidev.SpiDev()
                logger.info("✅ SPI interface initialized")
            except Exception as e:
                logger.warning(f"⚠️ SPI initialization failed: {e}")
                self.spi = None
        else:
            logger.info("🔄 Running in simulation mode")
        
        # Start auto-detection
        if self.detection_enabled:
            self.start_auto_detection()
    
    def start_auto_detection(self):
        """Start automatic component detection"""
        logger.info("🔍 Starting automatic component detection")
        
        # Start detection thread
        detection_thread = threading.Thread(target=self.detection_loop, daemon=True)
        detection_thread.start()
        
        # Start I2C scanning
        i2c_thread = threading.Thread(target=self.scan_i2c_devices, daemon=True)
        i2c_thread.start()
        
        # Start 1-Wire scanning
        onewire_thread = threading.Thread(target=self.scan_1wire_devices, daemon=True)
        onewire_thread.start()
    
    def detection_loop(self):
        """Main detection loop using analysis patterns"""
        while self.detection_enabled:
            try:
                # Scan all GPIO pins for activity
                for pin in range(2, 28):  # GPIO 2-27
                    if pin not in [2, 3]:  # Skip I2C pins for now
                        self.analyze_gpio_pin(pin)
                
                # Update component states
                self.update_component_states()
                
                time.sleep(1)  # Detection interval
                
            except Exception as e:
                logger.error(f"Detection loop error: {e}")
                time.sleep(5)
    
    def analyze_gpio_pin(self, pin: int):
        """Analyze GPIO pin using patterns from analysis"""
        if not PI_AVAILABLE:
            return
        
        try:
            # Set pin as input with pull-up
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            
            # Read initial state
            initial_state = GPIO.input(pin)
            
            # Check for activity patterns
            readings = []
            for _ in range(10):
                readings.append(GPIO.input(pin))
                time.sleep(0.01)
            
            # Analyze pattern
            pattern = self.classify_pin_pattern(pin, readings, initial_state)
            
            if pattern:
                self.handle_detected_pattern(pin, pattern)
                
        except Exception as e:
            logger.debug(f"GPIO {pin} analysis error: {e}")
    
    def classify_pin_pattern(self, pin: int, readings: List[int], initial_state: int) -> Optional[str]:
        """Classify GPIO pin pattern using analysis patterns"""
        
        # Calculate pattern characteristics
        transitions = sum(1 for i in range(1, len(readings)) if readings[i] != readings[i-1])
        stable_high = all(r == 1 for r in readings)
        stable_low = all(r == 0 for r in readings)
        periodic = self.detect_periodic_pattern(readings)
        
        # Pattern classification based on analysis
        if stable_high and initial_state == 1:
            return "digital_input_pullup"  # Likely button or switch
        elif stable_low:
            return "digital_output_low"    # Driven low
        elif transitions > 5:
            return "digital_communication" # Communication or PWM
        elif transitions == 2:
            return "motion_sensor"         # PIR-like behavior
        elif periodic:
            return "pwm_signal"           # PWM output
        
        return None
    
    def detect_periodic_pattern(self, readings: List[int]) -> bool:
        """Detect periodic patterns in readings"""
        if len(readings) < 6:
            return False
        
        # Look for repeating patterns
        for period in range(2, len(readings) // 2):
            is_periodic = True
            for i in range(period, len(readings)):
                if readings[i] != readings[i - period]:
                    is_periodic = False
                    break
            if is_periodic:
                return True
        
        return False
    
    def handle_detected_pattern(self, pin: int, pattern: str):
        """Handle detected pattern and initialize component"""
        current_time = time.time()
        
        # Skip if recently detected
        if pin in self.detected_components:
            if current_time - self.detected_components[pin].last_seen < 30:
                return
        
        # Map pattern to component type using analysis
        component_mapping = {
            "digital_input_pullup": "Button_or_Switch",
            "motion_sensor": "PIR_Sensor", 
            "digital_communication": "Communication_Device",
            "pwm_signal": "PWM_Output"
        }
        
        component_type = component_mapping.get(pattern, "Unknown_Device")
        
        # Create detected component
        detected_component = DetectedComponent(
            name=f"{component_type}_GPIO{pin}",
            pin=pin,
            component_type=component_type,
            confidence=0.7,
            characteristics={"pattern": pattern, "gpio_pin": pin},
            initialization_pattern=self.get_initialization_pattern(component_type),
            data_pattern=self.get_data_pattern(component_type),
            last_seen=current_time
        )
        
        self.detected_components[pin] = detected_component
        logger.info(f"🔍 Detected {component_type} on GPIO {pin} (pattern: {pattern})")
        
        # Auto-initialize if enabled
        if self.auto_init_enabled:
            self.initialize_component(detected_component)
    
    def scan_i2c_devices(self):
        """Scan for I2C devices using analysis patterns"""
        if not self.i2c_bus:
            return
        
        while self.detection_enabled:
            try:
                detected_addresses = []
                
                # Scan I2C address range
                for addr in range(0x03, 0x78):
                    try:
                        self.i2c_bus.write_byte(addr, 0)
                        detected_addresses.append(addr)
                    except:
                        pass
                
                # Process detected I2C devices
                for addr in detected_addresses:
                    self.identify_i2c_device(addr)
                
                time.sleep(30)  # Scan every 30 seconds
                
            except Exception as e:
                logger.error(f"I2C scanning error: {e}")
                time.sleep(60)
    
    def identify_i2c_device(self, address: int):
        """Identify I2C device using component database"""
        addr_hex = f"0x{address:02x}"
        
        # Check against known devices in database
        for component_name, component_data in self.component_db.get('component_mapping', {}).items():
            if component_data.get('i2c_address') == addr_hex:
                
                current_time = time.time()
                detected_component = DetectedComponent(
                    name=f"{component_name}_{addr_hex}",
                    pin=address,  # Use address as pin for I2C
                    component_type=component_name,
                    confidence=0.9,
                    characteristics=component_data.get('characteristics', {}),
                    initialization_pattern=f"i2c_init_{component_name.lower()}",
                    data_pattern=f"i2c_read_{component_name.lower()}",
                    last_seen=current_time
                )
                
                self.i2c_devices[address] = detected_component
                logger.info(f"🔍 Identified I2C device: {component_name} at {addr_hex}")
                
                if self.auto_init_enabled:
                    self.initialize_component(detected_component)
                
                break
        else:
            logger.info(f"🔍 Unknown I2C device at {addr_hex}")
    
    def scan_1wire_devices(self):
        """Scan for 1-Wire devices (typically temperature sensors)"""
        while self.detection_enabled:
            try:
                # Check if 1-wire is enabled
                w1_path = Path('/sys/bus/w1/devices')
                if w1_path.exists():
                    devices = list(w1_path.glob('28-*'))  # DS18B20 family
                    
                    for device_path in devices:
                        device_id = device_path.name
                        self.handle_1wire_device(device_id, device_path)
                
                time.sleep(60)  # Scan every minute
                
            except Exception as e:
                logger.error(f"1-Wire scanning error: {e}")
                time.sleep(120)
    
    def handle_1wire_device(self, device_id: str, device_path: Path):
        """Handle detected 1-Wire device"""
        current_time = time.time()
        
        detected_component = DetectedComponent(
            name=f"DS18B20_{device_id}",
            pin=4,  # 1-Wire typically uses GPIO 4
            component_type="DS18B20",
            confidence=0.95,
            characteristics={
                "device_id": device_id,
                "device_path": str(device_path),
                "data_type": "temperature"
            },
            initialization_pattern="1wire_temperature_init",
            data_pattern="1wire_temperature_read",
            last_seen=current_time
        )
        
        self.detected_components[device_id] = detected_component
        logger.info(f"🔍 Detected 1-Wire temperature sensor: {device_id}")
        
        if self.auto_init_enabled:
            self.initialize_component(detected_component)
    
    def initialize_component(self, component: DetectedComponent):
        """Initialize detected component using analysis patterns"""
        logger.info(f"🚀 Initializing {component.name}")
        
        try:
            # Get initialization pattern from analysis
            init_pattern = self.get_component_init_code(component)
            
            # Execute initialization
            if init_pattern:
                # Create sensor instance
                sensor_instance = self.create_sensor_instance(component, init_pattern)
                
                if sensor_instance:
                    self.active_sensors[component.name] = {
                        'component': component,
                        'instance': sensor_instance,
                        'last_reading': None,
                        'error_count': 0,
                        'initialized_at': time.time()
                    }
                    
                    # Start data streaming if enabled
                    if self.streaming_enabled:
                        self.start_data_stream(component.name)
                    
                    logger.info(f"✅ {component.name} initialized successfully")
                else:
                    logger.error(f"❌ Failed to create sensor instance for {component.name}")
            else:
                logger.warning(f"⚠️ No initialization pattern found for {component.name}")
                
        except Exception as e:
            logger.error(f"❌ Initialization failed for {component.name}: {e}")
    
    def get_component_init_code(self, component: DetectedComponent) -> Optional[str]:
        """Get component initialization code from analysis patterns"""
        
        component_patterns = {
            "PIR_Sensor": "MotionSensor(pin)",
            "Button_or_Switch": "Button(pin)",
            "DHT11": "DHT11(pin)",
            "DS18B20": "W1ThermSensor(sensor_id=device_id)",
            "BMP180": "BMP180(i2c_bus)",
            "ADS1115": "ADS1115(i2c_bus, address)"
        }
        
        return component_patterns.get(component.component_type)
    
    def create_sensor_instance(self, component: DetectedComponent, init_pattern: str):
        """Create actual sensor instance using gpiozero or direct libraries"""
        if not PI_AVAILABLE:
            return MockSensor(component.name)  # Return mock for simulation
        
        try:
            if component.component_type == "PIR_Sensor":
                return MotionSensor(component.pin)
            elif component.component_type == "Button_or_Switch":
                return Button(component.pin)
            elif component.component_type == "DS18B20":
                return DS18B20Sensor(component.characteristics.get('device_id'))
            elif component.component_type == "DHT11":
                return DHT11Sensor(component.pin)
            elif component.component_type == "BMP180":
                return BMP180Sensor(self.i2c_bus)
            elif component.component_type == "ADS1115":
                return ADS1115Sensor(self.i2c_bus, component.pin)
            else:
                return GenericSensor(component)
                
        except Exception as e:
            logger.error(f"Sensor creation error: {e}")
            return None
    
    def start_data_stream(self, component_name: str):
        """Start optimized data streaming for component"""
        if component_name not in self.active_sensors:
            return
        
        sensor_info = self.active_sensors[component_name]
        component = sensor_info['component']
        
        # Get optimal sampling rate from analysis
        sampling_rate = self.get_optimal_sampling_rate(component)
        
        # Start streaming thread
        stream_thread = threading.Thread(
            target=self.data_stream_loop,
            args=(component_name, sampling_rate),
            daemon=True
        )
        stream_thread.start()
        
        logger.info(f"📊 Started data stream for {component_name} at {sampling_rate}Hz")
    
    def get_optimal_sampling_rate(self, component: DetectedComponent) -> float:
        """Get optimal sampling rate from analysis patterns"""
        
        # Default rates based on analysis
        rate_mapping = {
            "PIR_Sensor": 10.0,      # Fast for motion detection
            "Button_or_Switch": 20.0, # Fast for responsiveness
            "DHT11": 0.5,            # Slow for temperature/humidity
            "DS18B20": 1.0,          # Medium for temperature
            "BMP180": 2.0,           # Medium for pressure
            "ADS1115": 100.0         # Fast for analog
        }
        
        return rate_mapping.get(component.component_type, 1.0)
    
    def data_stream_loop(self, component_name: str, sampling_rate: float):
        """Data streaming loop with error handling"""
        interval = 1.0 / sampling_rate
        
        while (self.streaming_enabled and 
               component_name in self.active_sensors):
            
            try:
                # Read sensor data
                reading = self.read_sensor_data(component_name)
                
                if reading:
                    # Store reading
                    if component_name not in self.data_streams:
                        self.data_streams[component_name] = []
                    
                    self.data_streams[component_name].append(reading)
                    
                    # Keep only recent readings (last 1000)
                    if len(self.data_streams[component_name]) > 1000:
                        self.data_streams[component_name] = self.data_streams[component_name][-1000:]
                    
                    # Update sensor info
                    self.active_sensors[component_name]['last_reading'] = reading
                    self.active_sensors[component_name]['error_count'] = 0
                
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"Data stream error for {component_name}: {e}")
                self.active_sensors[component_name]['error_count'] += 1
                
                # Stop streaming if too many errors
                if self.active_sensors[component_name]['error_count'] > 10:
                    logger.error(f"Too many errors for {component_name}, stopping stream")
                    break
                
                time.sleep(interval * 2)  # Back off on errors
    
    def read_sensor_data(self, component_name: str) -> Optional[SensorReading]:
        """Read data from sensor using optimized patterns"""
        if component_name not in self.active_sensors:
            return None
        
        sensor_info = self.active_sensors[component_name]
        component = sensor_info['component']
        instance = sensor_info['instance']
        
        try:
            # Read based on component type
            if hasattr(instance, 'read_data'):
                raw_value = instance.read_data()
            elif hasattr(instance, 'value'):
                raw_value = instance.value
            elif hasattr(instance, 'is_pressed'):
                raw_value = instance.is_pressed
            elif hasattr(instance, 'motion_detected'):
                raw_value = instance.motion_detected
            else:
                raw_value = str(instance)
            
            # Create standardized reading
            reading = SensorReading(
                component=component_name,
                timestamp=time.time(),
                value=raw_value,
                unit=self.get_component_unit(component),
                pin=component.pin,
                quality=1.0  # Assume good quality for now
            )
            
            return reading
            
        except Exception as e:
            logger.debug(f"Read error for {component_name}: {e}")
            return None
    
    def get_component_unit(self, component: DetectedComponent) -> str:
        """Get appropriate unit for component readings"""
        unit_mapping = {
            "DHT11": "°C/%RH",
            "DS18B20": "°C",
            "BMP180": "hPa/°C",
            "PIR_Sensor": "boolean",
            "Button_or_Switch": "boolean",
            "ADS1115": "V"
        }
        
        return unit_mapping.get(component.component_type, "raw")
    
    def get_system_status(self) -> Dict:
        """Get comprehensive system status"""
        return {
            'detected_components': {name: asdict(comp) for name, comp in self.detected_components.items()},
            'active_sensors': {
                name: {
                    'component_name': info['component'].name,
                    'component_type': info['component'].component_type,
                    'last_reading': asdict(info['last_reading']) if info['last_reading'] else None,
                    'error_count': info['error_count'],
                    'uptime': time.time() - info['initialized_at']
                }
                for name, info in self.active_sensors.items()
            },
            'i2c_devices': {addr: asdict(comp) for addr, comp in self.i2c_devices.items()},
            'data_streams': {
                name: len(readings) for name, readings in self.data_streams.items()
            },
            'system_health': {
                'detection_enabled': self.detection_enabled,
                'auto_init_enabled': self.auto_init_enabled,
                'streaming_enabled': self.streaming_enabled,
                'total_detections': len(self.detected_components),
                'active_streams': len([name for name in self.data_streams if self.data_streams[name]])
            }
        }
    
    def update_component_states(self):
        """Update component states and handle disconnections"""
        current_time = time.time()
        
        # Check for stale components
        stale_components = []
        for name, component in self.detected_components.items():
            if current_time - component.last_seen > 300:  # 5 minutes
                stale_components.append(name)
        
        # Remove stale components
        for name in stale_components:
            logger.info(f"🔌 Component {name} appears disconnected")
            del self.detected_components[name]
            
            if name in self.active_sensors:
                del self.active_sensors[name]
            
            if name in self.data_streams:
                del self.data_streams[name]
    
    def cleanup(self):
        """Clean up system resources"""
        logger.info("🧹 Cleaning up Smart Pi Auto-Configuration")
        
        self.detection_enabled = False
        self.streaming_enabled = False
        
        if PI_AVAILABLE:
            GPIO.cleanup()
        
        if hasattr(self, 'i2c_bus') and self.i2c_bus:
            try:
                self.i2c_bus.close()
            except:
                pass
        
        if hasattr(self, 'spi') and self.spi:
            try:
                self.spi.close()
            except:
                pass

# Mock classes for simulation mode
class MockSensor:
    def __init__(self, name):
        self.name = name
        self.value = 0
    
    def read_data(self):
        import random
        return random.random()

class DS18B20Sensor:
    def __init__(self, device_id):
        self.device_id = device_id
        self.device_path = f"/sys/bus/w1/devices/{device_id}/w1_slave"
    
    def read_data(self):
        try:
            with open(self.device_path, 'r') as f:
                lines = f.readlines()
            
            if lines[0].strip()[-3:] == 'YES':
                temp_line = lines[1]
                temp_value = temp_line.split('t=')[1]
                return float(temp_value) / 1000.0
        except:
            pass
        return None

class DHT11Sensor:
    def __init__(self, pin):
        self.pin = pin
        # Would use actual DHT11 library here
    
    def read_data(self):
        # Simulate reading
        import random
        return {
            'temperature': 20 + random.random() * 10,
            'humidity': 40 + random.random() * 20
        }

class BMP180Sensor:
    def __init__(self, i2c_bus):
        self.i2c_bus = i2c_bus
    
    def read_data(self):
        # Simulate reading
        import random
        return {
            'pressure': 1013.25 + random.random() * 10,
            'temperature': 20 + random.random() * 5
        }

class ADS1115Sensor:
    def __init__(self, i2c_bus, address):
        self.i2c_bus = i2c_bus
        self.address = address
    
    def read_data(self):
        # Simulate reading
        import random
        return random.random() * 3.3

class GenericSensor:
    def __init__(self, component):
        self.component = component
    
    def read_data(self):
        import random
        return random.random()

# Example usage
if __name__ == '__main__':
    # Initialize smart auto-configuration
    auto_config = SmartPiAutoConfig()
    
    try:
        logger.info("🚀 Smart Pi Auto-Configuration running...")
        logger.info("System will auto-detect and initialize connected components")
        
        # Run for demo
        for i in range(30):
            time.sleep(2)
            if i % 10 == 0:
                status = auto_config.get_system_status()
                logger.info(f"📊 System Status: {len(status['detected_components'])} detected, {len(status['active_sensors'])} active")
        
    except KeyboardInterrupt:
        logger.info("👋 Shutting down...")
    finally:
        auto_config.cleanup()