from multiprocessing import Queue
from time import sleep

import smbus
'''
  Read Gyro and Accelerometer by Interfacing Raspberry Pi with MPU6050 using Python
	http://www.electronicwings.com
  https://www.electronicwings.com/raspberry-pi/mpu6050-accelerometergyroscope-interfacing-with-raspberry-pi
'''

#some MPU6050 Registers and their Address
PWR_MGMT_1   = 0x6B
SMPLRT_DIV   = 0x19
CONFIG       = 0x1A
GYRO_CONFIG  = 0x1B
INT_ENABLE   = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H  = 0x43
GYRO_YOUT_H  = 0x45
GYRO_ZOUT_H  = 0x47


def MPU_Init():
	#write to sample rate register
	bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)
	
	#Write to power management register
	bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)
	
	#Write to Configuration register
	bus.write_byte_data(Device_Address, CONFIG, 0)
	
	#Write to Gyro configuration register
	bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)
	
	#Write to interrupt enable register
	bus.write_byte_data(Device_Address, INT_ENABLE, 1)

def read_raw_data(addr):
	#Accelero and Gyro value are 16-bit
        high = bus.read_byte_data(Device_Address, addr)
        low = bus.read_byte_data(Device_Address, addr+1)
    
        #concatenate higher and lower value
        value = ((high << 8) | low)
        
        #to get signed value from mpu6050
        if(value > 32768):
                value = value - 65536
        return value


bus = smbus.SMBus(1) 	# or bus = smbus.SMBus(0) for older version boards
Device_Address = 0x68   # MPU6050 device address

MPU_Init()

def get_gyro_data():
	
  #Read Accelerometer raw value
  acc_x = read_raw_data(ACCEL_XOUT_H)
  acc_y = read_raw_data(ACCEL_YOUT_H)
  acc_z = read_raw_data(ACCEL_ZOUT_H)

  #Read Gyroscope raw value
  gyro_x = read_raw_data(GYRO_XOUT_H)
  gyro_y = read_raw_data(GYRO_YOUT_H)
  gyro_z = read_raw_data(GYRO_ZOUT_H)

  #Full scale range +/- 250 degree/C as per sensitivity scale factor
  Ax = acc_x/16384.0
  Ay = acc_y/16384.0
  Az = acc_z/16384.0

  Gx = gyro_x/131.0
  Gy = gyro_y/131.0
  Gz = gyro_z/131.0

  return Az

did_jump = False
did_pipe = False

def test_gyro():

  global did_jump
  global did_pipe
  
  while True:
	
    acceleration_z = get_gyro_data()

    if acceleration_z > 1.3:
      did_jump = True
      did_pipe = False
    
    if acceleration_z < 0.4:
       did_jump = False

    if did_jump:
       current_color_animation = jump_animation
       sleep(1.5)
       current_color_animation = idle_animation


class Gyro:
    
    def __init__(self, message_q: Queue):
        self.message_q = message_q