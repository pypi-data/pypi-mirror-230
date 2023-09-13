""" In this file you can find a main class with some methods """

import RPi.GPIO as g      
from smbus import SMBus                #Import the smbus module and SMBus class for the i2c conection to MPU6050

class ServoControl:
    """This one is the main class and here are defined some methods"""
    
    def __init__(self , servo_pin , i2c_port):               #This method was created to initialize attributes
        """Initialize"""
        g.setup(servo_pin , g.OUT)                           #Here I set up the pin for servomotor with out direction
        self.sm = g.PWM(servo_pin , 50)                      #Here I created an instance of PWM class to control the motor
        self.sm.start(0)                                     #Initialize duty cycle with 0%
        self.bus = SMBus(i2c_port)                           #Create an instance for i2c conection
    
    def setup_mpu(self):                                     #This method was created to setup the mpu sensor
        """Initialize mpu sensor"""
        #Registers addresses
        INT_ENABLE = 0x38
        CONFIG = 0x1A
        PWR_MGMT_1 = 0x6B
        SMPLRT_DIV = 0x19
        device_address = 0x68
        
        #Setup the bits of registers
        self.bus.write_byte_data(device_address , PWR_MGMT_1 , 0x01)     # Power management | 1 on position 0
        self.bus.write_byte_data(device_address , SMPLRT_DIV , 0x07)     # Sample rate divider | 1 on position 0,1,2
        self.bus.write_byte_data(device_address , CONFIG , 0x00)         # Configuration
        self.bus.write_byte_data(device_address , INT_ENABLE , 0x01)     # Interrupt enable | 1 on position 0
        
    def read_data_x(self):                     
        """Reading from the sensor's x axis"""
        ACCEL_XOUT_H = 0x3B
        ACCEL_XOUT_L = 0x3C
        device_address = 0x68
        
        #Get the highs and lows values
        high = self.bus.read_byte_data(device_address , ACCEL_XOUT_H)
        low = self.bus.read_byte_data(device_address , ACCEL_XOUT_L)
    
        #Concatenate 2 registers of 8 bits each to one of 16 bits
        value = ( (high << 8) | low )
    
        #Get the signed value
        if value > 32768:
            value = value - 65536
        
        #Divide the signed value with the sensivity
        value2 = value/16384
        return value2

    def read_data_y(self):
        """Reading from the sensor's y axis"""
        ACCEL_YOUT_H = 0x3D
        ACCEL_YOUT_L = 0x3E
        device_address = 0x68
        
        high = self.bus.read_byte_data(device_address , ACCEL_YOUT_H)
        low = self.bus.read_byte_data(device_address , ACCEL_YOUT_L)
    
        value = ( (high << 8) | low )
    
        if value > 32768:
            value = value - 65536
    
        value2 = value/16384
        return value2

    def read_data_z(self):
        """Reading from the sensor's z axis"""
        ACCEL_ZOUT_H = 0x3F
        ACCEL_ZOUT_L = 0x40
        device_address = 0x68
        
        high = self.bus.read_byte_data(device_address , ACCEL_ZOUT_H)
        low = self.bus.read_byte_data(device_address , ACCEL_ZOUT_L)
    
        value = ( (high << 8) | low )
    
        if value > 32768:
            value = value - 65536
    
        value2 = value/16384
        return value2
    
    def start_control(self,data):
        """Start"""
        v = ((data - 1)*(180-0))/(((-1)-1)+0)         #Convert the values read from accelerometer between -1g and 1g 
                                                     #to 0 and 180 degrees
        v2 = 2 +(v/18)                               #Convert degrees in duty cycle percentage
        if v2 >= 2 and v2<= 12:
            self.sm.ChangeDutyCycle(v2)
            
    def stop_control(self):
        """Stop"""
        self.sm.stop()