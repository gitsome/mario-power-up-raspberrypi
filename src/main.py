#!/user/bin/env python
from typing import Union
from enum import Enum, auto
import multiprocessing
import smbus
import time
from time import sleep
import logging
import board

import RPi.GPIO as GPIO

from lights import Lights
from gyro import Gyro
from gamepad import Gamepad
from sounds import Sounds, SoundEffect


print("Initializing...")

# ============================= CONSTANTS ======================================

class Mode(Enum):
    TRICK_OR_TREAT = auto()
    TRICK_OR_TREAT_LOADED = auto()
    ADMIN = auto()

class Action(Enum):
    
    # MODE SWITCHING ACTIONS

    GO_TRICK_OR_TREAT = auto()

    # TRICK OR TREAT ACTIONS

    JUMP = auto()
    PIPE = auto()

    GO_ADMIN = auto()
    GO_TRICK_OR_TREAT_LOADED = auto()

    # TRICK OR TREAT LOADED

    CANDY = auto()
    CANDY_MEDIUM = auto()
    CANDY_HEAVY = auto()

    # ADMIN ACTIONS

    CALIBRATE_SCALE = auto()
    VOLUME_UP = auto()
    VOLUME_DOWN = auto()


# ============================= LOGGING ======================================

logging.basicConfig(filename='main.log',level=logging.DEBUG)
logger = logging.getLogger('app_logger')


# ============================= PIN SETUP ======================================

print("Setting up Raspberry Pi Pins")
GPIO.setmode(GPIO.BCM)


# ============= Helper Class Instantiation ============

q_lights = multiprocessing.Queue()
lights = Lights(q_lights)

q_gyro = multiprocessing.Queue()
gyro = Gyro(q_gyro)

q_sounds = multiprocessing.Queue()
sounds = Sounds(q_sounds)

q_gyro = multiprocessing.Queue()
gyro = Gyro(q_gyro)


# ============= Main Loop ============

current_action: Union[None, Action] = None
mode = Mode.TRICK_OR_TREAT

while True:

    # if we are allowed to do something else now then test for new conditions to trigger a new action
    if current_action is not None:

        # test gamepad for input

        # We have two different modes
        if mode == Mode.TRICK_OR_TREAT:
            pass
        elif mode == Mode.TRICK_OR_TREAT_LOADED:
            pass
        elif mode == Mode.TRICK_OR_TREAT:
            pass

    # otherwise we have an action going on 
    else:
        lights.animate()


    if did_jump:
        did_jump = False
        sounds.play_sound(SoundEffect.MARIO_JUMP)
  