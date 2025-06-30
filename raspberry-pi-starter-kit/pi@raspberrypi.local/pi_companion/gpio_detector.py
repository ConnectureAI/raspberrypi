#!/usr/bin/env python3
"""
GPIO Component Auto-Detection System
Automatically detects connected components on Raspberry Pi GPIO pins
"""

import time
import logging
from gpiozero import Device, DigitalInputDevice, DigitalOutputDevice, MCP3008
from gpiozero.pins.pigpio import PiGPIOFactory
import RPi.GPIO as GPIO

logger = logging.getLogger(__name__)

class GPIODetector:
    def __init__(self):
        self.detected_components = {}
        self.last_scan = 0
        self.scan_interval = 5.0  # seconds
        
        # Pin mappings for common components
        self.pin_patterns = {
            # Digital input devices (sensors)
            'button': {'type': 'digital_input', 'pull_up': True},
            'pir_sensor': {'type': 'digital_input', 'pull_up': False},
            'reed_switch': {'type': 'digital_input', 'pull_up': True},
            'tilt_switch': {'type': 'digital_input', 'pull_up': True},
            'touch_sensor': {'type': 'digital_input', 'pull_up': False},
            'flame_sensor': {'type': 'digital_input', 'pull_up': False},
            'collision_sensor': {'type': 'digital_input', 'pull_up': True},
            'magnetic_sensor': {'type': 'digital_input', 'pull_up': True},
            'shock_sensor': {'type': 'digital_input', 'pull_up': True},
            'sound_sensor': {'type': 'digital_input', 'pull_up': False},
            'line_tracking': {'type': 'digital_input', 'pull_up': False},
            'obstacle_avoidance': {'type': 'digital_input', 'pull_up': False},
            
            # Digital output devices
            'led': {'type': 'digital_output'},
            'buzzer': {'type': 'digital_output'},
            'relay': {'type': 'digital_output'},
            'laser': {'type': 'digital_output'},
            
            # PWM devices
            'servo': {'type': 'pwm'},
            'motor': {'type': 'pwm'},
            'rgb_led': {'type': 'pwm_multi', 'pins': 3},
            
            # Analog devices (via MCP3008)
            'potentiometer': {'type': 'analog'},
            'photoresistor': {'type': 'analog'},
            'thermistor': {'type': 'analog'},
            'gas_sensor': {'type': 'analog'},
            'alcohol_sensor': {'type': 'analog'},
            'joystick': {'type': 'analog_multi', 'pins': 2},
            
            # I2C devices (addresses)
            'lcd_i2c': {'type': 'i2c', 'address': 0x27},
            'rtc': {'type': 'i2c', 'address': 0x68},
            'accelerometer': {'type': 'i2c', 'address': 0x53},
            
            # SPI devices
            'rfid': {'type': 'spi'},
            'matrix_display': {'type': 'spi'},
        }
        
        # GPIO pins to scan (BCM numbering)
        self.gpio_pins = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27]
        
        # MCP3008 channels for analog detection
        self.analog_channels = [0, 1, 2, 3, 4, 5, 6, 7]
        
    def detect_digital_input(self, pin):
        """Detect if a digital input device is connected to a pin"""
        try:
            # Test with pull-up
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            time.sleep(0.01)
            state_up = GPIO.input(pin)
            
            # Test with pull-down
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            time.sleep(0.01)
            state_down = GPIO.input(pin)
            
            # Test floating
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_OFF)
            time.sleep(0.01)
            state_float = GPIO.input(pin)
            
            # Analyze results
            if state_up != state_down:
                # Pin responds to pull resistors - likely a button or sensor
                if state_up == 1 and state_down == 0:
                    return self.identify_input_type(pin, 'floating')
                else:
                    return self.identify_input_type(pin, 'active_pull')
            elif state_float != state_up:
                # Pin state changes when floating
                return self.identify_input_type(pin, 'sensor')
                
        except Exception as e:
            logger.debug(f"Error testing digital input on pin {pin}: {e}")
            
        return None
    
    def identify_input_type(self, pin, behavior):
        """Identify the type of input device based on behavior"""
        # Sample multiple readings to detect patterns
        readings = []
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        for _ in range(10):
            readings.append(GPIO.input(pin))
            time.sleep(0.01)
            
        stable = all(r == readings[0] for r in readings)
        
        if stable:
            if behavior == 'floating':
                return {'type': 'button', 'subtype': 'momentary'}
            elif readings[0] == 1:
                return {'type': 'sensor', 'subtype': 'active_low'}
            else:
                return {'type': 'sensor', 'subtype': 'active_high'}
        else:
            # Changing signal - could be sensor
            return {'type': 'sensor', 'subtype': 'dynamic'}
    
    def detect_digital_output(self, pin):
        """Test if pin can be used as digital output"""
        try:
            GPIO.setup(pin, GPIO.OUT)
            
            # Test output capability
            GPIO.output(pin, GPIO.HIGH)
            time.sleep(0.01)
            GPIO.output(pin, GPIO.LOW)
            time.sleep(0.01)
            
            return {'type': 'output', 'subtype': 'digital'}
            
        except Exception as e:
            logger.debug(f"Error testing digital output on pin {pin}: {e}")
            
        return None
    
    def detect_pwm_device(self, pin):
        """Detect PWM-capable devices"""
        try:
            # Only certain pins support hardware PWM
            if pin in [12, 13, 18, 19]:
                return {'type': 'pwm', 'subtype': 'hardware'}
            else:
                return {'type': 'pwm', 'subtype': 'software'}
                
        except Exception as e:
            logger.debug(f"Error testing PWM on pin {pin}: {e}")
            
        return None
    
    def detect_analog_devices(self):
        """Detect analog devices connected via MCP3008"""
        analog_devices = {}
        
        try:
            # Try to initialize MCP3008
            mcp = MCP3008()
            
            for channel in self.analog_channels:
                try:
                    # Take multiple readings
                    readings = []
                    for _ in range(10):
                        readings.append(mcp.read(channel))
                        time.sleep(0.01)
                    
                    avg_reading = sum(readings) / len(readings)
                    variance = sum((r - avg_reading) ** 2 for r in readings) / len(readings)
                    
                    # Analyze the signal
                    if avg_reading > 0.01:  # Something connected
                        if variance > 0.001:  # Changing signal
                            device_type = self.classify_analog_signal(avg_reading, variance, readings)
                        else:  # Stable signal
                            device_type = self.classify_stable_analog(avg_reading)
                            
                        if device_type:
                            analog_devices[f"mcp{channel}"] = device_type
                            
                except Exception as e:
                    logger.debug(f"Error reading MCP3008 channel {channel}: {e}")
                    
        except Exception as e:
            logger.debug(f"MCP3008 not available: {e}")
            
        return analog_devices
    
    def classify_analog_signal(self, avg, variance, readings):
        """Classify analog signal based on characteristics"""
        if 0.4 < avg < 0.6 and variance > 0.01:
            return {'type': 'joystick', 'subtype': 'analog_stick'}
        elif avg > 0.8:
            return {'type': 'photoresistor', 'subtype': 'light_sensor'}
        elif 0.2 < avg < 0.8 and variance > 0.005:
            return {'type': 'potentiometer', 'subtype': 'variable_resistor'}
        elif avg < 0.3:
            return {'type': 'sensor', 'subtype': 'low_signal'}
        else:
            return {'type': 'sensor', 'subtype': 'unknown_analog'}
    
    def classify_stable_analog(self, value):
        """Classify stable analog signals"""
        if value > 0.9:
            return {'type': 'sensor', 'subtype': 'maxed_out'}
        elif value < 0.1:
            return {'type': 'sensor', 'subtype': 'minimal_signal'}
        else:
            return {'type': 'sensor', 'subtype': 'stable_analog'}
    
    def detect_i2c_devices(self):
        """Detect I2C devices"""
        i2c_devices = {}
        
        try:
            import smbus
            bus = smbus.SMBus(1)  # I2C bus 1
            
            # Common I2C addresses to scan
            addresses = [0x27, 0x3c, 0x48, 0x53, 0x68, 0x76]
            
            for addr in addresses:
                try:
                    bus.read_byte(addr)
                    device_type = self.identify_i2c_device(addr)
                    i2c_devices[f"i2c_{addr:02x}"] = device_type
                    logger.info(f"Found I2C device at address 0x{addr:02x}")
                except:
                    pass
                    
        except Exception as e:
            logger.debug(f"I2C scanning error: {e}")
            
        return i2c_devices
    
    def identify_i2c_device(self, address):
        """Identify I2C device by address"""
        device_map = {
            0x27: {'type': 'lcd', 'subtype': 'i2c_display'},
            0x3c: {'type': 'oled', 'subtype': 'ssd1306'},
            0x48: {'type': 'adc', 'subtype': 'ads1115'},
            0x53: {'type': 'accelerometer', 'subtype': 'adxl345'},
            0x68: {'type': 'rtc', 'subtype': 'ds1307'},
            0x76: {'type': 'pressure', 'subtype': 'bmp280'},
        }
        
        return device_map.get(address, {'type': 'unknown', 'subtype': f'i2c_{address:02x}'})
    
    def detect_spi_devices(self):
        """Detect SPI devices"""
        spi_devices = {}
        
        # SPI detection is more complex and device-specific
        # For now, we'll check if SPI is enabled
        try:
            with open('/boot/config.txt', 'r') as f:
                content = f.read()
                if 'dtparam=spi=on' in content:
                    spi_devices['spi0'] = {'type': 'spi', 'subtype': 'interface_available'}
        except:
            pass
            
        return spi_devices
    
    def detect_components(self):
        """Main component detection method"""
        current_time = time.time()
        
        # Throttle scanning
        if current_time - self.last_scan < self.scan_interval:
            return self.detected_components
            
        logger.info("Scanning for GPIO components...")
        new_components = {}
        
        # Initialize GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        try:
            # Scan digital pins
            for pin in self.gpio_pins:
                try:
                    # Try digital input detection
                    input_device = self.detect_digital_input(pin)
                    if input_device:
                        new_components[f"gpio{pin}"] = input_device
                        continue
                        
                    # Try digital output detection
                    output_device = self.detect_digital_output(pin)
                    if output_device:
                        new_components[f"gpio{pin}"] = output_device
                        
                except Exception as e:
                    logger.debug(f"Error scanning pin {pin}: {e}")
                finally:
                    try:
                        GPIO.cleanup(pin)
                    except:
                        pass
            
            # Detect analog devices
            analog_devices = self.detect_analog_devices()
            new_components.update(analog_devices)
            
            # Detect I2C devices
            i2c_devices = self.detect_i2c_devices()
            new_components.update(i2c_devices)
            
            # Detect SPI devices
            spi_devices = self.detect_spi_devices()
            new_components.update(spi_devices)
            
        finally:
            GPIO.cleanup()
        
        # Update detected components
        if new_components != self.detected_components:
            logger.info(f"Component changes detected: {len(new_components)} components found")
            for component, details in new_components.items():
                logger.info(f"  {component}: {details['type']} ({details.get('subtype', 'unknown')})")
        
        self.detected_components = new_components
        self.last_scan = current_time
        
        return self.detected_components
    
    def get_component_suggestions(self):
        """Get suggested component types based on detection patterns"""
        suggestions = {}
        
        for component, details in self.detected_components.items():
            if details['type'] == 'sensor' and details.get('subtype') == 'active_low':
                suggestions[component] = ['PIR sensor', 'Touch sensor', 'Flame sensor']
            elif details['type'] == 'button':
                suggestions[component] = ['Push button', 'Momentary switch']
            elif details['type'] == 'output':
                suggestions[component] = ['LED', 'Buzzer', 'Relay', 'Laser']
            elif details['type'] == 'photoresistor':
                suggestions[component] = ['Light sensor', 'Photoresistor']
            elif details['type'] == 'potentiometer':
                suggestions[component] = ['Rotary potentiometer', 'Slide potentiometer']
                
        return suggestions