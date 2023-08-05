import multiprocessing
from typing import Union
from time import sleep
import time

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

accel_start_time: Union[None, int] = None
time_since_last_jump = time.time()

def gyro_loop(message_q, logger):

    global did_jump
    global time_since_last_jump

    while True:

        acceleration_z = get_gyro_data()

        is_strong_accel = acceleration_z > 1.2

        if is_strong_accel and time.time() - time_since_last_jump > 1.5:
          
          if accel_start_time is not None and (time.time() - accel_start_time) > 0.05:
            did_jump = True
          elif accel_start_time is None:
            accel_start_time = time.time()

        else:
            accel_start_time = None
            did_jump = False

        if did_jump:
            did_jump = False
            time_since_last_jump = time.time()
            message_q.put(True)
            sleep(1.5)

class Gyro:
    
    message_q: multiprocessing.Queue

    def __init__ (self, queue, logger):
      
        self.message_q = queue

        # create and start the gyro listener
        gyro_listener_process = multiprocessing.Process(target=gyro_loop, args=(self.message_q, logger))
        gyro_listener_process.start()