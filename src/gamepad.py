from multiprocessing import Queue
from evdev import InputDevice, categorize, ecodes

gamepad = InputDevice('/dev/input/event0')
button_down = None
button_value = 0
print(gamepad)

def gamepad_loop():

  for event in gamepad.read_loop():
    
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

class Gamepad:
   def __init__ (self, message_q: Queue):
      self.message_q = message_q