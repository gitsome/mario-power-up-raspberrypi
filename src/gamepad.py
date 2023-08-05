from typing import Union
from datetime import datetime
import multiprocessing
import threading
from enum import Enum, auto
from evdev import InputDevice, categorize, ecodes

class GamePadButton(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    SELECT = auto()
    START = auto()
    A = auto()
    B = auto()

class ButtonPress:

    button: GamePadButton
    time: int

    def __init__(self, button: GamePadButton, time: int):
        self.button = button
        self.time = time

gamepad = InputDevice('/dev/input/event0')

def gamepad_loop(message_q: multiprocessing.Queue, logger):

    button_pressed:Union[None, GamePadButton] = None
    button_down:Union[None, int] = None
    button_value = 0

    for event in gamepad.read_loop():
    
        button_pressed = None

        # =========== BUTTON RIGHT

        if event.code == 16 and event.value == -1:
            button_down = 16
            button_value = event.value

        if event.code == 16 and event.value == 0 and button_down == 16 and button_value == 1:
            logger.debug('right')
            button_pressed = GamePadButton.RIGHT
            button_down = None


        # =========== BUTTON LEFT

        if event.code == 16 and event.value == 1:
            button_down = 16
            button_value = event.value

        if event.code == 16 and event.value == 0 and button_down == 16 and button_value == -1:
            logger.debug('left')
            button_pressed = GamePadButton.LEFT
            button_down = None


        # =========== BUTTON UP

        if event.code == 17 and event.value == -1:
            button_down = 17
            button_value = event.value

        if event.code == 17 and button_down == 17 and event.value == 0 and button_value == -1:
            logger.debug("up")
            button_pressed = GamePadButton.UP
            button_down = None


        # =========== BUTTON DOWN

        if event.code == 17 and event.value == 1:
            button_down = 17
            button_value = event.value

        if event.code == 17 and button_down == 17 and event.value == 0 and button_value == 1:
            logger.debug("down")
            button_pressed = GamePadButton.DOWN
            button_down = None


        # =========== BUTTON A

        if event.code == 305 and event.value == 1:
            button_down = 305

        if event.code == 305 and button_down == 305 and event.value == 0:
            logger.debug('buttonA')
            button_pressed = GamePadButton.A
            button_down = None


        # =========== BUTTON B

        if event.code == 304 and event.value == 1:
            button_down = 304

        if event.code == 304 and button_down == 304 and event.value == 0:
            logger.debug('buttonB')
            button_pressed = GamePadButton.B
            button_down = None


        # =========== BUTTON SELECT

        if event.code == 314 and event.value == 1:
            button_down = 314

        if event.code == 314 and button_down == 314 and event.value == 0:
            logger.debug("select")
            button_pressed = GamePadButton.SELECT
            button_down = None


        # =========== BUTTON START 

        if event.code == 315 and event.value == 1:
            button_down = 315

        if event.code == 315 and button_down == 315 and event.value == 0:
            logger.debug('start')
            button_pressed = GamePadButton.START
            button_down = None

        if button_pressed is not None:
            message_q.put(ButtonPress(button = button_pressed, time=datetime.now()))


class Gamepad:

   button_pressed: Union[str, None]
   message_q: multiprocessing.Queue

   def __init__ (self, queue, logger):
      
        self.message_q = queue
      
        gamepad_listener_process = multiprocessing.Process(target=gamepad_loop, args=(self.message_q, logger))
        gamepad_listener_process.start()
      
