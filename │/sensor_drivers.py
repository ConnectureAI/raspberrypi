#!/usr/bin/env python3
"""
Sensor Drivers for 35+ Raspberry Pi Starter Kit Components
Handles all sensors, actuators, and displays in the kit
"""

import time
import logging
import threading
from datetime import datetime
from gpiozero import (
    LED, PWMLED, RGBLED, Button, MCP3008, Servo, Motor, 
    Buzzer, DigitalInputDevice, DigitalOutputDevice
)
import RPi.GPIO as GPIO
import smbus
import spidev

logger = logging.getLogger(__name__)

class SensorManager:
    def __init__(self):
        self.components = {}
        self.readings = {}
        self.last_readings = {}
        self.i2c_bus = None
        self.spi = None
        self.running_threads = {}
        
        # Initialize I2C and SPI
        self.init_communication()
        
    def init_communication(self):
        """Initialize I2C and SPI communication"""
        try:
            self.i2c_bus = smbus.SMBus(1)
            logger.info("I2C initialized")
        except Exception as e:
            logger.warning(f"I2C initialization failed: {e}")
            
        try:
            self.spi = spidev.SpiDev()
            self.spi.open(0, 0)
            self.spi.max_speed_hz = 1000000
            logger.info("SPI initialized")
        except Exception as e:
            logger.warning(f"SPI initialization failed: {e}")
    
    def initialize(self, detected_components):
        """Initialize components based on detection results"""
        logger.info(f"Initializing {len(detected_components)} detected components")
        
        for component_id, component_info in detected_components.items():
            try:
                self.init_component(component_id, component_info)
            except Exception as e:
                logger.error(f"Failed to initialize {component_id}: {e}")
    
    def init_component(self, component_id, component_info):
        """Initialize a single component"""
        comp_type = component_info.get('type')
        subtype = component_info.get('subtype')
        
        if component_id.startswith('gpio'):
            pin = int(component_id[4:])
            self.init_gpio_component(component_id, pin, comp_type, subtype)
        elif component_id.startswith('mcp'):
            channel = int(component_id[3:])
            self.init_analog_component(component_id, channel, comp_type, subtype)
        elif component_id.startswith('i2c'):
            address = int(component_id.split('_')[1], 16)
            self.init_i2c_component(component_id, address, comp_type, subtype)
        elif component_id.startswith('spi'):
            self.init_spi_component(component_id, comp_type, subtype)
    
    def init_gpio_component(self, component_id, pin, comp_type, subtype):
        """Initialize GPIO-based components"""
        try:
            if comp_type == 'button':
                self.components[component_id] = Button(pin)
                logger.info(f"Initialized button on pin {pin}")
                
            elif comp_type == 'sensor':
                if subtype in ['active_low', 'active_high']:
                    self.components[component_id] = DigitalInputDevice(pin)
                    logger.info(f"Initialized digital sensor on pin {pin}")
                    
            elif comp_type == 'output':
                self.components[component_id] = LED(pin)
                logger.info(f"Initialized LED on pin {pin}")
                
            elif comp_type == 'pwm':
                # Default to servo, can be changed based on actual device
                if pin in [12, 13, 18, 19]:  # Hardware PWM pins
                    self.components[component_id] = Servo(pin)
                    logger.info(f"Initialized servo on pin {pin}")
                else:
                    self.components[component_id] = PWMLED(pin)
                    logger.info(f"Initialized PWM LED on pin {pin}")
                    
        except Exception as e:
            logger.error(f"Error initializing GPIO component {component_id}: {e}")
    
    def init_analog_component(self, component_id, channel, comp_type, subtype):
        """Initialize analog components via MCP3008"""
        try:
            # All analog components use MCP3008
            self.components[component_id] = {
                'type': 'analog',
                'channel': channel,
                'subtype': subtype,
                'mcp': MCP3008(channel=channel)
            }
            logger.info(f"Initialized analog {subtype} on MCP3008 channel {channel}")
            
        except Exception as e:
            logger.error(f"Error initializing analog component {component_id}: {e}")
    
    def init_i2c_component(self, component_id, address, comp_type, subtype):
        """Initialize I2C components"""
        try:
            self.components[component_id] = {
                'type': 'i2c',
                'address': address,
                'subtype': subtype,
                'bus': self.i2c_bus
            }
            
            # Initialize specific I2C devices
            if subtype == 'i2c_display':
                self.init_lcd_display(component_id, address)
            elif subtype == 'ds1307':
                self.init_rtc(component_id, address)
            elif subtype == 'adxl345':
                self.init_accelerometer(component_id, address)
                
            logger.info(f"Initialized I2C {subtype} at address 0x{address:02x}")
            
        except Exception as e:
            logger.error(f"Error initializing I2C component {component_id}: {e}")
    
    def init_spi_component(self, component_id, comp_type, subtype):
        """Initialize SPI components"""
        try:
            self.components[component_id] = {
                'type': 'spi',
                'subtype': subtype,
                'spi': self.spi
            }
            logger.info(f"Initialized SPI {subtype}")
            
        except Exception as e:
            logger.error(f"Error initializing SPI component {component_id}: {e}")
    
    def init_lcd_display(self, component_id, address):
        """Initialize I2C LCD display"""
        try:
            # LCD initialization sequence for PCF8574
            self.i2c_bus.write_byte(address, 0x03)
            time.sleep(0.005)
            self.i2c_bus.write_byte(address, 0x03)
            time.sleep(0.005)
            self.i2c_bus.write_byte(address, 0x03)
            time.sleep(0.005)
            self.i2c_bus.write_byte(address, 0x02)
            time.sleep(0.005)
            
        except Exception as e:
            logger.error(f"LCD initialization failed: {e}")
    
    def init_rtc(self, component_id, address):
        """Initialize DS1307 RTC"""
        try:
            # Read the seconds register to check if RTC is running
            seconds = self.i2c_bus.read_byte_data(address, 0x00)
            if seconds & 0x80:
                # Clock is halted, start it
                self.i2c_bus.write_byte_data(address, 0x00, seconds & 0x7F)
                
        except Exception as e:
            logger.error(f"RTC initialization failed: {e}")
    
    def init_accelerometer(self, component_id, address):
        """Initialize ADXL345 accelerometer"""
        try:
            # Set to measurement mode
            self.i2c_bus.write_byte_data(address, 0x2D, 0x08)
            # Set data format to +/- 2g
            self.i2c_bus.write_byte_data(address, 0x31, 0x00)
            
        except Exception as e:
            logger.error(f"Accelerometer initialization failed: {e}")
    
    def read_all_sensors(self):
        """Read all sensor data"""
        current_readings = {}
        
        for component_id, component in self.components.items():
            try:
                reading = self.read_component(component_id, component)
                if reading is not None:
                    current_readings[component_id] = reading
                    
            except Exception as e:
                logger.error(f"Error reading {component_id}: {e}")
        
        self.last_readings = current_readings.copy()
        return current_readings
    
    def read_component(self, component_id, component):
        """Read data from a specific component"""
        if isinstance(component, dict):
            return self.read_complex_component(component_id, component)
        else:
            return self.read_simple_component(component_id, component)
    
    def read_simple_component(self, component_id, component):
        """Read simple gpiozero components"""
        try:
            if isinstance(component, Button):
                return {
                    'value': component.is_pressed,
                    'type': 'button',
                    'timestamp': datetime.now().isoformat()
                }
                
            elif isinstance(component, DigitalInputDevice):
                return {
                    'value': component.value,
                    'type': 'digital_sensor',
                    'timestamp': datetime.now().isoformat()
                }
                
            elif isinstance(component, (LED, PWMLED)):
                return {
                    'value': component.value,
                    'type': 'led_output',
                    'timestamp': datetime.now().isoformat()
                }
                
            elif isinstance(component, Servo):
                return {
                    'value': component.value,
                    'angle': component.value * 90 if component.value else 0,
                    'type': 'servo',
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error reading simple component {component_id}: {e}")
            
        return None
    
    def read_complex_component(self, component_id, component):
        """Read complex components (analog, I2C, SPI)"""
        comp_type = component.get('type')
        
        if comp_type == 'analog':
            return self.read_analog_component(component_id, component)
        elif comp_type == 'i2c':
            return self.read_i2c_component(component_id, component)
        elif comp_type == 'spi':
            return self.read_spi_component(component_id, component)
            
        return None
    
    def read_analog_component(self, component_id, component):
        """Read analog components via MCP3008"""
        try:
            mcp = component['mcp']
            raw_value = mcp.value
            voltage = raw_value * 3.3  # Convert to voltage
            
            subtype = component.get('subtype', 'unknown')
            
            # Convert based on sensor type
            if subtype == 'photoresistor':
                # Light level (inverted - higher voltage = more light)
                light_level = (1.0 - raw_value) * 100
                return {
                    'raw': raw_value,
                    'voltage': voltage,
                    'light_level': light_level,
                    'type': 'light_sensor',
                    'unit': 'percent',
                    'timestamp': datetime.now().isoformat()
                }
                
            elif subtype == 'potentiometer':
                # Rotation percentage
                rotation = raw_value * 100
                return {
                    'raw': raw_value,
                    'voltage': voltage,
                    'rotation': rotation,
                    'type': 'potentiometer',
                    'unit': 'percent',
                    'timestamp': datetime.now().isoformat()
                }
                
            elif subtype == 'thermistor':
                # Temperature calculation (simplified)
                # This is a basic calculation - real thermistors need calibration
                resistance = (raw_value * 10000) / (1 - raw_value) if raw_value < 1 else 10000
                temperature = 25 + (resistance - 10000) * 0.01  # Approximate
                return {
                    'raw': raw_value,
                    'voltage': voltage,
                    'temperature': temperature,
                    'type': 'temperature_sensor',
                    'unit': 'celsius',
                    'timestamp': datetime.now().isoformat()
                }
                
            elif subtype == 'joystick':
                # Joystick position
                position = (raw_value - 0.5) * 2  # Convert to -1 to +1 range
                return {
                    'raw': raw_value,
                    'voltage': voltage,
                    'position': position,
                    'type': 'joystick_axis',
                    'unit': 'normalized',
                    'timestamp': datetime.now().isoformat()
                }
                
            else:
                # Generic analog reading
                return {
                    'raw': raw_value,
                    'voltage': voltage,
                    'type': 'analog_sensor',
                    'unit': 'volts',
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error reading analog component {component_id}: {e}")
            
        return None
    
    def read_i2c_component(self, component_id, component):
        """Read I2C components"""
        try:
            address = component['address']
            subtype = component.get('subtype')
            bus = component['bus']
            
            if subtype == 'ds1307':
                return self.read_rtc(bus, address)
            elif subtype == 'adxl345':
                return self.read_accelerometer(bus, address)
            elif subtype == 'bmp280':
                return self.read_pressure_sensor(bus, address)
            else:
                # Generic I2C read
                try:
                    data = bus.read_byte(address)
                    return {
                        'data': data,
                        'type': 'i2c_device',
                        'address': address,
                        'timestamp': datetime.now().isoformat()
                    }
                except:
                    return None
                    
        except Exception as e:
            logger.error(f"Error reading I2C component {component_id}: {e}")
            
        return None
    
    def read_rtc(self, bus, address):
        """Read DS1307 RTC"""
        try:
            # Read time registers
            data = bus.read_i2c_block_data(address, 0x00, 7)
            
            # Convert BCD to decimal
            seconds = (data[0] & 0x0F) + ((data[0] & 0x70) >> 4) * 10
            minutes = (data[1] & 0x0F) + ((data[1] & 0x70) >> 4) * 10
            hours = (data[2] & 0x0F) + ((data[2] & 0x30) >> 4) * 10
            
            return {
                'hours': hours,
                'minutes': minutes,
                'seconds': seconds,
                'type': 'rtc',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error reading RTC: {e}")
            return None
    
    def read_accelerometer(self, bus, address):
        """Read ADXL345 accelerometer"""
        try:
            # Read acceleration data
            data = bus.read_i2c_block_data(address, 0x32, 6)
            
            # Convert to 16-bit signed values
            x = (data[1] << 8) | data[0]
            if x > 32767: x -= 65536
            
            y = (data[3] << 8) | data[2]
            if y > 32767: y -= 65536
            
            z = (data[5] << 8) | data[4]
            if z > 32767: z -= 65536
            
            # Convert to g-force (assuming +/- 2g range)
            scale = 2.0 / 32768.0
            
            return {
                'x': x * scale,
                'y': y * scale,
                'z': z * scale,
                'type': 'accelerometer',
                'unit': 'g',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error reading accelerometer: {e}")
            return None
    
    def read_pressure_sensor(self, bus, address):
        """Read BMP280 pressure sensor"""
        try:
            # This is a simplified reading - real BMP280 needs calibration
            temp_data = bus.read_i2c_block_data(address, 0xFA, 3)
            press_data = bus.read_i2c_block_data(address, 0xF7, 3)
            
            return {
                'temperature': 25.0,  # Placeholder
                'pressure': 1013.25,  # Placeholder
                'type': 'pressure_sensor',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error reading pressure sensor: {e}")
            return None
    
    def read_spi_component(self, component_id, component):
        """Read SPI components"""
        try:
            subtype = component.get('subtype')
            spi = component['spi']
            
            if subtype == 'interface_available':
                return {
                    'status': 'available',
                    'type': 'spi_interface',
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error reading SPI component {component_id}: {e}")
            
        return None
    
    # Control methods for outputs
    def control_led(self, pin, state):
        """Control LED"""
        component_id = f"gpio{pin}"
        if component_id in self.components:
            try:
                component = self.components[component_id]
                if isinstance(component, (LED, PWMLED)):
                    if isinstance(state, bool):
                        component.on() if state else component.off()
                    else:
                        component.value = float(state)
                    logger.info(f"LED on pin {pin} set to {state}")
            except Exception as e:
                logger.error(f"Error controlling LED on pin {pin}: {e}")
    
    def control_servo(self, pin, angle):
        """Control servo motor"""
        component_id = f"gpio{pin}"
        if component_id in self.components:
            try:
                component = self.components[component_id]
                if isinstance(component, Servo):
                    # Convert angle (0-180) to servo value (-1 to 1)
                    servo_value = (angle - 90) / 90.0
                    component.value = max(-1, min(1, servo_value))
                    logger.info(f"Servo on pin {pin} set to {angle} degrees")
            except Exception as e:
                logger.error(f"Error controlling servo on pin {pin}: {e}")
    
    def control_motor(self, pin, direction, speed=100):
        """Control DC motor"""
        component_id = f"gpio{pin}"
        if component_id in self.components:
            try:
                component = self.components[component_id]
                speed_value = speed / 100.0
                
                if direction == 'forward':
                    component.value = speed_value
                elif direction == 'backward':
                    component.value = -speed_value
                else:
                    component.value = 0
                    
                logger.info(f"Motor on pin {pin} set to {direction} at {speed}%")
            except Exception as e:
                logger.error(f"Error controlling motor on pin {pin}: {e}")
    
    def control_buzzer(self, pin, frequency=1000, duration=0.5):
        """Control buzzer"""
        def buzzer_thread():
            try:
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(pin, GPIO.OUT)
                
                pwm = GPIO.PWM(pin, frequency)
                pwm.start(50)  # 50% duty cycle
                time.sleep(duration)
                pwm.stop()
                GPIO.cleanup(pin)
                
                logger.info(f"Buzzer on pin {pin} played {frequency}Hz for {duration}s")
            except Exception as e:
                logger.error(f"Error controlling buzzer on pin {pin}: {e}")
        
        # Run buzzer in separate thread to avoid blocking
        thread = threading.Thread(target=buzzer_thread)
        thread.daemon = True
        thread.start()
    
    def update_components(self, detected_components):
        """Update component list when new components are detected"""
        # Remove components that are no longer detected
        for component_id in list(self.components.keys()):
            if component_id not in detected_components:
                self.cleanup_component(component_id)
        
        # Add new components
        for component_id, component_info in detected_components.items():
            if component_id not in self.components:
                try:
                    self.init_component(component_id, component_info)
                except Exception as e:
                    logger.error(f"Failed to initialize new component {component_id}: {e}")
    
    def cleanup_component(self, component_id):
        """Clean up a component"""
        try:
            component = self.components[component_id]
            if hasattr(component, 'close'):
                component.close()
            del self.components[component_id]
            logger.info(f"Cleaned up component {component_id}")
        except Exception as e:
            logger.error(f"Error cleaning up component {component_id}: {e}")
    
    def cleanup(self):
        """Clean up all components"""
        logger.info("Cleaning up all sensor components")
        for component_id in list(self.components.keys()):
            self.cleanup_component(component_id)
        
        try:
            GPIO.cleanup()
        except:
            pass
            
        if self.spi:
            try:
                self.spi.close()
            except:
                pass