#!/user/bin/env python
import threading 
import smbus
import time
from time import sleep
import os
import logging


from rpi_ws281x import *
import RPi.GPIO as GPIO
from hx711 import HX711
from evdev import InputDevice, categorize, ecodes

from adafruit_servokit import ServoKit

from adafruit_led_animation.animation.blink import Blink
from adafruit_led_animation.animation.comet import Comet
from adafruit_led_animation.animation.colorcycle import ColorCycle
from adafruit_led_animation.animation.pulse import Pulse
from adafruit_led_animation.animation.sparkle import Sparkle
from adafruit_led_animation.animation.solid import Solid
from adafruit_led_animation.sequence import AnimationSequence, AnimateOnce
from adafruit_led_animation.color import PURPLE, AMBER, JADE, MAGENTA, ORANGE, TEAL, GREEN, RED, YELLOW, BLACK, WHITE

import board
import neopixel
import neopixel_spi

logging.basicConfig(filename='itsame_log.log',level=logging.DEBUG)

logger = logging.getLogger('app_logger')


GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN)
GPIO.setup(27, GPIO.IN)
GPIO.setup(22, GPIO.IN)
GPIO.setup(23, GPIO.IN)
GPIO.setup(24, GPIO.IN)

print("starting up...")

# ============================= SERVO ==========================

servo_kit = ServoKit(channels=16)


# ============================= LIGHTING =======================================

NUM_PIXELS = 24
SERVO_FLAT_ANGLE = 40
SERVO_DROP_ANGLE = 130

print(dir(board))
# pixels = neopixel.NeoPixel(board.D12, NUM_PIXELS, brightness=0.1, auto_write=False, pixel_order=neopixel.GRB)
pixels = neopixel_spi.NeoPixel_SPI(board.SPI(), NUM_PIXELS, brightness=0.8, auto_write=False, pixel_order=neopixel.GRB)

comet_yellow = Comet(pixels, speed=0.04, color=YELLOW, tail_length=6, bounce=False, ring=True)
comet_white = Comet(pixels, speed=0.02, color=WHITE, tail_length=6, bounce=False, ring=True)
pulse_black = Pulse(pixels, speed=0.1, color=BLACK, period=0.1)
solid_green = Solid(pixels, color=GREEN)
solid_black = Solid(pixels, color=BLACK)
solid_white = Solid(pixels, color=WHITE)
pulse_red = Pulse(pixels, speed=0.005, color=RED, period=0.2)
pulse_yellow = Pulse(pixels, speed=0.01, color=YELLOW, period=1)
pulse_white = Pulse(pixels, speed=0.05, color=WHITE, period=1)
pulse_green = Pulse(pixels, speed=0.05, color=GREEN, period=1.5)

idle_animation = AnimationSequence(pulse_white, pulse_black, advance_interval=1, auto_clear=True)
waiting_animation = comet_white
star_animation = ColorCycle(pixels, 0.3, colors=[ORANGE, YELLOW, WHITE])
coin_animation = pulse_yellow
pipe_animation = pulse_green

jump_animation = solid_white
fireball_animation = pulse_red

current_color_animation = pulse_white

# animations = AnimationSequence(comet, sparkle, blink, pulse, colorcycle, advance_interval=5, auto_clear=True)


# ============================= LIGHTS AND SOUNDS ==========================

def set_current_animation(new_animation):
  global current_color_animation
   
  if current_color_animation is not None:
    current_color_animation.reset()
  
  current_color_animation = new_animation
  current_color_animation.reset()

def play_mario_star():
  print("mario star")
  set_current_animation(AnimationSequence(star_animation, star_animation, star_animation, star_animation, star_animation, star_animation, star_animation, advance_interval=None))
  os.system('mpg321 -g 6 /home/johnmartin/Documents/star_power.mp3 &')

def play_mario_die():
  print("mario_die")
  set_current_animation(star_animation)
  os.system('mpg321 -g 6 /home/johnmartin/Documents/mario_die.mp3 &')

def play_mario_jump():
  set_current_animation(AnimateOnce(pulse_white))
  os.system('mpg321 -g 2 /home/johnmartin/Documents/mario_jump.mp3 &')

def play_mario_fireball():
  set_current_animation(AnimateOnce(fireball_animation))
  os.system('mpg321 -g 2 /home/johnmartin/Documents/fireball.mp3 &')

def play_mario_coin():
  set_current_animation(AnimateOnce(pulse_yellow))
  os.system('mpg321 -g 6 /home/johnmartin/Documents/mario_coin.mp3 &')

def play_mario_waiting():
  set_current_animation(waiting_animation)
  os.system('mpg321 -g 25 /home/johnmartin/Documents/imawaiting.mp3 &')

def play_mario_letsa_go():
  set_current_animation(jump_animation)
  os.system('mpg321 -g 12 /home/johnmartin/Documents/mario_letsa_go.mp3 &')

def play_mario_pipe():
  set_current_animation(AnimateOnce(pipe_animation))
  os.system('mpg321 -g 3 /home/johnmartin/Documents/mario_pipe.mp3 &')

def play_mario_pipe():
  set_current_animation(AnimateOnce(pipe_animation))
  os.system('mpg321 -g 3 /home/johnmartin/Documents/mario_pipe.mp3 &')

def play_mario_just_what_i_needed():
  os.system('mpg321 -g 8 /home/johnmartin/Documents/mario_just_what_i_needed.mp3 &')

def play_mario_1up():
  set_current_animation(AnimateOnce(pulse_green))
  os.system('mpg321 -g 6 /home/johnmartin/Documents/mario_1up.mp3 &')

def play_mario_yeahoo():
  os.system('mpg321 -g 6 /home/johnmartin/Documents/yeahoo.mp3 &')

def play_mario_power_up():
  set_current_animation(AnimateOnce(pulse_white))
  os.system('mpg321 -g 4 /home/johnmartin/Documents/mario_power_up.mp3 &')


# ============================= GYRO =======================================

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


gyro_thread = threading.Thread(target=test_gyro, args=()) 
gyro_thread.start() 



# ============================= SCALE ======================================


hx = HX711(dout_pin=6, pd_sck_pin=5)
hx.zero()

# ========== CALIBRATION ============
# input('Place weight then press Enter: ')
# reading = hx.get_data_mean(readings = 100)
# known_weight_grams_str = input('Tell me how many grams and press Enter: ')
# known_weight_grams = float(known_weight_grams_str)
# calibration_ratio = reading / known_weight_grams
# print("calibration_ratio:", calibration_ratio)

calibration_ratio = 690.35

hx.set_scale_ratio(calibration_ratio)

def sensor_weight():

  global hx

  while True:

    reading = hx.get_weight_mean()
      
    if (reading > 80):
      play_mario_star()
      servo_kit.servo[0].angle = SERVO_DROP_ANGLE
    elif (reading > 30):
      play_mario_just_what_i_needed()
      time.sleep(1.25)
      play_mario_power_up()
      servo_kit.servo[0].angle = SERVO_DROP_ANGLE
    elif (reading > 10):
      play_mario_yeahoo()
      time.sleep(0.75)
      play_mario_coin()
      servo_kit.servo[0].angle = SERVO_DROP_ANGLE
    else:
       servo_kit.servo[0].angle = SERVO_FLAT_ANGLE

weight_thread = threading.Thread(target=sensor_weight, args=()) 
weight_thread.start()




# ============================= GAMEPAD CONTROLLER ======================================

gamepad = InputDevice('/dev/input/event0')
button_down = None
button_value = 0
print(gamepad)

def gamepad_loop():
  for event in gamepad.read_loop():
    # print("event: ", event)
    # print("type: ", event.type)
    # print("code: ", event.code)
    # print("value: ", event.value)
    if event.code == 16 and event.value == -1:
       button_down = 16
       button_value = event.value
       
    if event.code == 16 and event.value == 1:
       button_down = 16
       button_value = event.value

    if event.code == 16 and event.value == 0 and button_down == 16 and button_value == 1:
       print('left')
       button_down = None

    if event.code == 16 and event.value == 0 and button_down == 16 and button_value == -1:
       print('right')
       button_down = None

    if event.code == 17 and event.value == -1:
       button_down = 17
       button_value = event.value

    if event.code == 17 and event.value == 1:
       button_down = 17
       button_value = event.value

    if event.code == 17 and button_down == 17 and event.value == 0 and button_value == -1:
      print("up")
      button_down = None

    if event.code == 17 and button_down == 17 and event.value == 0 and button_value == 1:
      print("down")
      button_down = None
      play_mario_pipe()

    if event.code == 305 and event.value == 1:
       button_down = 305
    
    if event.code == 305 and button_down == 305 and event.value == 0:
       play_mario_jump()
       button_down = None


    if event.code == 304 and event.value == 1:
       button_down = 304
    
    if event.code == 304 and button_down == 304 and event.value == 0:
      play_mario_fireball()
      button_down = None

    
    if event.code == 314 and event.value == 1:
      button_down = 314
    
    if event.code == 314 and button_down == 314 and event.value == 0:
      print("select")
      play_mario_coin()
      servo_kit.servo[0].angle = SERVO_DROP_ANGLE
      button_down = None


    if event.code == 315 and event.value == 1:
      button_down = 315
    
    if event.code == 315 and button_down == 315 and event.value == 0:
      print('start')
      button_down = None
       
      

gamepad_thread = threading.Thread(target=gamepad_loop, args=()) 
gamepad_thread.start()

# ============= INITIALIZATION ============

logger.debug('starting...')
servo_kit.servo[0].angle = SERVO_FLAT_ANGLE
play_mario_power_up()

# ============= LOOP ============

while True:

  if ( GPIO.input(17) == True ):
    play_mario_waiting()

  if ( GPIO.input(27) == True ):
    play_mario_coin()

  if ( GPIO.input(22) == True ):
    play_mario_die()

  if ( GPIO.input(23) == True ):
    play_mario_jump()

  if ( GPIO.input(24) == True ):
    play_mario_letsa_go()
  
  if did_jump:
     did_jump = False
     play_mario_jump()  

  if current_color_animation is not None:
    if not current_color_animation.animate():
       current_color_animation = None
  
  # pulse.animate()
  # pixels.fill((0, 255, 0))
  # pixels.show()
  # sleep(1)
  # pixels.fill((255, 0, 0))
  # pixels.show()
  # sleep(1)
  # pixels.fill((0, 0, 255))
  # pixels.show()
  # sleep(1)



  

  
  