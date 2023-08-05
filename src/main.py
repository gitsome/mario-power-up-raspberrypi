#!/user/bin/env python
from typing import Union
from enum import Enum, auto
from time import sleep
import logging
import board
import sys
from multiprocessing import Queue

import RPi.GPIO as GPIO

from lights import Lights, LIGHT_ANIMATION
from gyro import Gyro
from gamepad import Gamepad, GamePadButton, ButtonPress
from sounds import Sounds, SoundEffect
from servo import Servo


# ============================= LOGGING ======================================

print("Initializing Logger")

logging.basicConfig(filename='main.log', level=logging.DEBUG)
logger = logging.getLogger('app_logger')
logger.addHandler(logging.StreamHandler(sys.stdout))

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
    FIRE_BALL = auto()

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


# ============================= PIN SETUP ======================================

logger.info("Setting up Raspberry Pi Pins")
GPIO.setmode(GPIO.BCM)


# ============= Helper Class Instantiation ============

lights = Lights(logger=logger)
gyro = Gyro()
sounds = Sounds()
gyro = Gyro()
servo = Servo()

gamepad_q = Queue()
gamepad = Gamepad(logger=logger, queue = gamepad_q)

# ============= MODE AND ACTION LOGIC ===================

def check_for_trick_or_treat_actions(buttonPress: Union[None, ButtonPress]) -> Union[Action, None]:
    
    if button_press is not None:

        if buttonPress.button == GamePadButton.A:
            return Action.JUMP
        elif buttonPress.button == GamePadButton.B:
            return Action.FIRE_BALL


def check_for_trick_or_treat_loaded_actions():
    # need to poll the scale for a final measurement to trigger candy actions
    pass

def check_admin_actions():
    # test gamepad for input
    pass


# ============= Main Loop ============

logger.info('Staring the main LOOP...')

sounds.play_sound(SoundEffect.FIRE_BALL)
lights.run_animation(LIGHT_ANIMATION.FIRE_BALL)

# the mode determines which actions are possible
mode = Mode.TRICK_OR_TREAT

# actions lock everything else from happening
current_action: Union[None, Action] = None

while True:

    try:
        button_press = gamepad_q.get_nowait()
    except:
        button_press = None

    # if we are allowed to do something else now then test for new conditions to trigger a new action
    if current_action is None:

        # Break up the business logic by mode
        if mode == Mode.TRICK_OR_TREAT:
            current_action = check_for_trick_or_treat_actions(button_press)

        elif mode == Mode.TRICK_OR_TREAT_LOADED:
            check_for_trick_or_treat_loaded_actions(button_press)

        elif mode == Mode.ADMIN:
            check_admin_actions()

        if current_action is not None:
            
            if current_action == Action.JUMP:
                lights.run_animation(LIGHT_ANIMATION.JUMP)
                sounds.play_sound(SoundEffect.MARIO_JUMP)

            if current_action == Action.FIRE_BALL:
                lights.run_animation(LIGHT_ANIMATION.FIRE_BALL)  
                sounds.play_sound(SoundEffect.FIRE_BALL)

            if current_action == Action.PIPE:
                lights.run_animation(LIGHT_ANIMATION.PIPE)  
                sounds.play_sound(SoundEffect.PIPE)
                
            
            current_action = None

    # otherwise we have an action going
    else:
        pass
  