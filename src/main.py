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
from utils import empty_queue, reboot

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
    
    START_UP = auto()

    # MODE SWITCHING ACTIONS

    GO_TRICK_OR_TREAT = auto()

    # TRICK OR TREAT ACTIONS

    JUMP = auto()
    PIPE = auto()
    FIRE_BALL = auto()
    DUMP_CANDY = auto()

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
    REBOOT = auto()
    EXIT_ADMIN = auto()


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

def check_for_trick_or_treat_actions(buttonPress: ButtonPress) -> Union[Action, None]:
    
    if buttonPress.button == GamePadButton.A:
        return Action.JUMP
    elif buttonPress.button == GamePadButton.B:
        return Action.FIRE_BALL
    elif buttonPress.button == GamePadButton.DOWN:
        return Action.PIPE
    elif buttonPress.button == GamePadButton.START:
        return Action.DUMP_CANDY
    elif buttonPress.button == GamePadButton.SELECT:
        return Action.GO_ADMIN
    
    return None


def check_for_trick_or_treat_loaded_actions(buttonPress: Union[None, ButtonPress]) -> Union[Action, None]:
    # need to poll the scale for a final measurement to trigger candy actions
    pass


def check_admin_actions(buttonPress: ButtonPress) -> Union[Action, None]:

    if buttonPress.button == GamePadButton.UP:
        return Action.VOLUME_UP
    elif buttonPress.button == GamePadButton.DOWN:
        return Action.VOLUME_DOWN
    elif buttonPress.button == GamePadButton.START:
        return Action.REBOOT
    elif buttonPress.button == GamePadButton.A:
        return Action.CALIBRATE_SCALE
    elif buttonPress.button == GamePadButton.SELECT:
        return Action.EXIT_ADMIN
    
    return None


# ============= Main Loop ============

logger.info('Staring the main LOOP...')

# the mode determines which actions are possible
mode = Mode.TRICK_OR_TREAT

# actions lock everything else from happening
current_action: Union[None, Action] = Action.START_UP

while True:

    try:
        button_press = gamepad_q.get_nowait()
        empty_queue(gamepad_q)
    except:
        button_press = None

    # ========== GET ACTIONS BASED ON MODE ONLY IF ONE IS NOT ALREADY SET ============

    if current_action is None:

        if button_press is not None:

            if mode == Mode.TRICK_OR_TREAT:
                current_action = check_for_trick_or_treat_actions(button_press)
            elif mode == Mode.TRICK_OR_TREAT_LOADED:
                current_action = check_for_trick_or_treat_loaded_actions(button_press)
            elif mode == Mode.ADMIN:
                current_action = check_admin_actions(button_press)

        
    # ========== ACTIONS ============

    if current_action is not None:
        
        if current_action == Action.START_UP:
            lights.run_animation(LIGHT_ANIMATION.MARIO_COIN)
            sounds.play_sound(SoundEffect.LETSA_GO)

        if current_action == Action.JUMP:
            lights.run_animation(LIGHT_ANIMATION.JUMP)
            sounds.play_sound(SoundEffect.MARIO_JUMP)

        if current_action == Action.FIRE_BALL:
            lights.run_animation(LIGHT_ANIMATION.FIRE_BALL)  
            sounds.play_sound(SoundEffect.FIRE_BALL)

        if current_action == Action.PIPE:
            lights.run_animation(LIGHT_ANIMATION.PIPE)  
            sounds.play_sound(SoundEffect.PIPE)

        if current_action == Action.DUMP_CANDY:
            lights.run_animation(LIGHT_ANIMATION.MARIO_COIN)  
            sounds.play_sound(SoundEffect.MARIO_COIN)
            sleep(1)
            servo.drop_shelf()

        if current_action == Action.GO_ADMIN:
            lights.run_animation(LIGHT_ANIMATION.ADMIN)
            sounds.play_sound(SoundEffect.MAMA_MIA)
            mode = Mode.ADMIN
        
        if current_action == Action.REBOOT:
            sounds.play_sound(SoundEffect.MARIO_DIE)
            sleep(3)
            reboot()

        if current_action == Action.VOLUME_UP:
            sounds.volume_up()

        if current_action == Action.VOLUME_DOWN:
            sounds.volume_down()

        if current_action == Action.EXIT_ADMIN:
            mode = Mode.TRICK_OR_TREAT
            current_action = Action.START_UP
            continue
            
        current_action = None

    # otherwise we have an action going
    else:
        pass
  