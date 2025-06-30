#!/usr/bin/env python3
"""
Raspberry Pi Code Pattern Library
Extracted from Freenove Complete Starter Kit Analysis

This library contains reusable code patterns and best practices
identified from comprehensive analysis of 35+ projects.
"""

import time
import sys
from contextlib import contextmanager

class GPIOPatterns:
    """Common GPIO control patterns"""
    
    @staticmethod
    def basic_led_control():
        """Pattern: Basic LED on/off control"""
        from gpiozero import LED
        
        led = LED(17)
        try:
            while True:
                led.on()
                print("LED ON")
                time.sleep(1)
                led.off()
                print("LED OFF")
                time.sleep(1)
        except KeyboardInterrupt:
            print("Program stopped")
    
    @staticmethod
    def button_led_control():
        """Pattern: Button-controlled LED"""
        from gpiozero import LED, Button
        
        led = LED(17)
        button = Button(18)
        
        try:
            while True:
                if button.is_pressed:
                    led.on()
                    print("Button pressed - LED ON")
                else:
                    led.off()
                    print("Button released - LED OFF")
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("Program stopped")
    
    @staticmethod
    def rgb_led_control():
        """Pattern: RGB LED color control"""
        from gpiozero import RGBLED
        import random
        
        led = RGBLED(red=17, green=18, blue=27, active_high=False)
        
        def set_color(r, g, b):
            led.red = r / 100
            led.green = g / 100
            led.blue = b / 100
        
        try:
            while True:
                r = random.randint(0, 100)
                g = random.randint(0, 100)
                b = random.randint(0, 100)
                set_color(r, g, b)
                print(f"Color: R={r}, G={g}, B={b}")
                time.sleep(1)
        except KeyboardInterrupt:
            led.close()
            print("Program stopped")

class SensorPatterns:
    """Common sensor reading patterns"""
    
    @staticmethod
    def adc_auto_detect():
        """Pattern: Auto-detect ADC chip and read analog values"""
        from ADCDevice import ADCDevice, PCF8591, ADS7830
        
        adc = ADCDevice()
        
        # Auto-detection pattern
        if adc.detectI2C(0x48):
            adc = PCF8591()
            print("PCF8591 detected")
        elif adc.detectI2C(0x4b):
            adc = ADS7830()
            print("ADS7830 detected")
        else:
            print("No ADC found")
            return None
        
        return adc
    
    @staticmethod
    def sensor_with_threshold():
        """Pattern: Sensor reading with threshold detection"""
        adc = SensorPatterns.adc_auto_detect()
        if not adc:
            return
        
        threshold = 128  # Middle value
        
        try:
            while True:
                value = adc.analogRead(0)
                voltage = value / 255.0 * 3.3
                
                if value > threshold:
                    print(f"HIGH: {value} ({voltage:.2f}V)")
                else:
                    print(f"LOW: {value} ({voltage:.2f}V)")
                
                time.sleep(0.5)
        except KeyboardInterrupt:
            adc.close()
            print("Program stopped")
    
    @staticmethod
    def dht11_reliable_read():
        """Pattern: Reliable DHT11 reading with error handling"""
        from Freenove_DHT import DHT
        
        dht = DHT(17)
        max_retries = 15
        
        def read_dht11():
            for attempt in range(max_retries):
                result = dht.readDHT11()
                if result == 0:  # Success
                    return True, dht.getHumidity(), dht.getTemperature()
                time.sleep(0.1)
            return False, None, None
        
        try:
            while True:
                success, humidity, temperature = read_dht11()
                if success:
                    print(f"Humidity: {humidity:.2f}%, Temperature: {temperature:.2f}°C")
                else:
                    print("Failed to read DHT11")
                time.sleep(2)
        except KeyboardInterrupt:
            print("Program stopped")

class CommunicationPatterns:
    """Communication protocol patterns"""
    
    @staticmethod
    def i2c_device_scan():
        """Pattern: Scan for I2C devices"""
        import smbus
        
        bus = smbus.SMBus(1)
        devices = []
        
        print("Scanning I2C bus...")
        for addr in range(0x03, 0x78):
            try:
                bus.write_byte(addr, 0)
                devices.append(addr)
                print(f"Device found at address: 0x{addr:02X}")
            except:
                pass
        
        bus.close()
        return devices
    
    @staticmethod
    def safe_i2c_communication():
        """Pattern: Safe I2C communication with error handling"""
        import smbus
        
        @contextmanager
        def i2c_bus():
            bus = smbus.SMBus(1)
            try:
                yield bus
            finally:
                bus.close()
        
        def read_device(address, register):
            try:
                with i2c_bus() as bus:
                    return bus.read_byte_data(address, register)
            except Exception as e:
                print(f"I2C communication error: {e}")
                return None
        
        return read_device

class MotorPatterns:
    """Motor control patterns"""
    
    @staticmethod
    def dc_motor_control():
        """Pattern: DC motor with speed and direction control"""
        from gpiozero import Motor
        
        motor = Motor(forward=18, backward=19)
        
        def motor_test():
            print("Motor forward at 50% speed")
            motor.forward(0.5)
            time.sleep(2)
            
            print("Motor forward at 100% speed")
            motor.forward(1.0)
            time.sleep(2)
            
            print("Motor stop")
            motor.stop()
            time.sleep(1)
            
            print("Motor backward at 50% speed")
            motor.backward(0.5)
            time.sleep(2)
            
            print("Motor stop")
            motor.stop()
        
        try:
            motor_test()
        except KeyboardInterrupt:
            motor.stop()
            print("Motor stopped")
    
    @staticmethod
    def servo_sweep():
        """Pattern: Servo motor sweep movement"""
        from gpiozero import Servo
        
        servo = Servo(17)
        
        try:
            while True:
                print("Moving to minimum position")
                servo.min()
                time.sleep(1)
                
                print("Moving to middle position")
                servo.mid()
                time.sleep(1)
                
                print("Moving to maximum position")
                servo.max()
                time.sleep(1)
        except KeyboardInterrupt:
            servo.close()
            print("Servo stopped")

class DisplayPatterns:
    """Display control patterns"""
    
    @staticmethod
    def shift_register_control():
        """Pattern: 74HC595 shift register control"""
        from gpiozero import OutputDevice
        
        class ShiftRegister:
            def __init__(self, data_pin, clock_pin, latch_pin):
                self.data = OutputDevice(data_pin)
                self.clock = OutputDevice(clock_pin)
                self.latch = OutputDevice(latch_pin)
            
            def shift_out(self, value):
                self.latch.off()
                for i in range(7, -1, -1):
                    self.clock.off()
                    if (value >> i) & 1:
                        self.data.on()
                    else:
                        self.data.off()
                    self.clock.on()
                self.latch.on()
            
            def close(self):
                self.data.close()
                self.clock.close()
                self.latch.close()
        
        sr = ShiftRegister(17, 18, 27)
        
        try:
            # Light up LEDs in sequence
            for i in range(8):
                sr.shift_out(1 << i)
                time.sleep(0.5)
        except KeyboardInterrupt:
            pass
        finally:
            sr.close()

class ProjectTemplates:
    """Complete project templates"""
    
    @staticmethod
    def sensor_triggered_output():
        """Template: Sensor input triggers output device"""
        from gpiozero import LED, Button
        
        # Components
        sensor = Button(18)  # Any digital sensor
        output = LED(17)     # Any output device
        
        # Configuration
        trigger_active = True  # True for normally open, False for normally closed
        
        try:
            print("Sensor-triggered output system started")
            while True:
                if sensor.is_pressed == trigger_active:
                    output.on()
                    print("Sensor triggered - Output ON")
                else:
                    output.off()
                    print("Sensor inactive - Output OFF")
                time.sleep(0.1)
        except KeyboardInterrupt:
            output.off()
            print("System stopped")
    
    @staticmethod
    def data_logger_template():
        """Template: Sensor data logging with timestamp"""
        import datetime
        
        def log_sensor_data(sensor_name, value, unit=""):
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"{timestamp} - {sensor_name}: {value}{unit}"
            print(log_entry)
            
            # Write to file
            with open("sensor_data.log", "a") as f:
                f.write(log_entry + "\n")
        
        # Example usage
        adc = SensorPatterns.adc_auto_detect()
        if adc:
            try:
                while True:
                    value = adc.analogRead(0)
                    voltage = value / 255.0 * 3.3
                    log_sensor_data("Potentiometer", f"{value} ({voltage:.2f}V)")
                    time.sleep(10)  # Log every 10 seconds
            except KeyboardInterrupt:
                adc.close()
                print("Data logging stopped")

class BestPractices:
    """Best practices and common utilities"""
    
    @staticmethod
    def safe_gpio_cleanup():
        """Pattern: Safe GPIO cleanup with context manager"""
        from contextlib import contextmanager
        
        @contextmanager
        def gpio_manager(*components):
            try:
                yield components
            finally:
                for component in components:
                    if hasattr(component, 'close'):
                        component.close()
                    elif hasattr(component, 'stop'):
                        component.stop()
                print("GPIO cleanup completed")
    
    @staticmethod
    def error_handling_wrapper(func):
        """Decorator: Add error handling to any function"""
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except KeyboardInterrupt:
                print("\nProgram interrupted by user")
                return None
            except Exception as e:
                print(f"Error in {func.__name__}: {e}")
                return None
        return wrapper
    
    @staticmethod
    def retry_on_failure(max_retries=3, delay=1):
        """Decorator: Retry function on failure"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                for attempt in range(max_retries):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        if attempt == max_retries - 1:
                            raise e
                        print(f"Attempt {attempt + 1} failed: {e}")
                        time.sleep(delay)
            return wrapper
        return decorator

# Example usage and testing
if __name__ == "__main__":
    print("Raspberry Pi Code Pattern Library")
    print("Available pattern categories:")
    print("- GPIOPatterns: Basic GPIO control")
    print("- SensorPatterns: Sensor reading and processing")
    print("- CommunicationPatterns: I2C, SPI, UART")
    print("- MotorPatterns: Motor control")
    print("- DisplayPatterns: Display and LED control")
    print("- ProjectTemplates: Complete project templates")
    print("- BestPractices: Error handling and utilities")
    
    # Uncomment to test specific patterns:
    # GPIOPatterns.basic_led_control()
    # SensorPatterns.adc_auto_detect()
    # CommunicationPatterns.i2c_device_scan()