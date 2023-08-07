#!/user/bin/env python
from typing import Union
from enum import Enum, auto
import time
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
from scale import Scale, WEIGHT_THRESHOLD, SCALE_LOADED_WEIGHTS
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
    CLEAR = auto()

    # MODE SWITCHING ACTIONS

    GO_TRICK_OR_TREAT = auto()

    # TRICK OR TREAT ACTIONS

    JUMP = auto()
    PIPE = auto()
    WORLD_CLEAR = auto()
    UNDERGROUND = auto()
    PLAY = auto()
    FIRE_BALL = auto()
    WEIGHT_DETECTED = auto()
    DUMP_CANDY_LIGHT = auto()
    DUMP_CANDY_MEDIUM = auto()
    DUMP_CANDY_HEAVY = auto()


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
    PLATE_UP = auto()
    PLATE_DOWN = auto()
    REBOOT = auto()
    EXIT_ADMIN = auto()


# ============================= PIN SETUP ======================================

logger.info("Setting up Raspberry Pi Pins")
GPIO.setmode(GPIO.BCM)


# ============= Helper Class Instantiation ============

lights = Lights(logger=logger)
sounds = Sounds()
servo = Servo()

gyro_q = Queue()
gyro = Gyro(logger=logger, queue=gyro_q)

gamepad_q = Queue()
gamepad = Gamepad(logger=logger, queue=gamepad_q)

scale_q = Queue()
scale = Scale(logger=logger, queue=scale_q)

# ============= HELPER METHODS ============

def calibrate_scale():
    # move the servo into position and calibrate the scale
    servo.reset_shelf()
    sleep(1)
    scale.calibrate()


# ============= MODE AND ACTION LOGIC ===================

def check_for_trick_or_treat_actions(buttonPress: ButtonPress) -> Union[Action, None]:
    
    if buttonPress.button == GamePadButton.A:
        return Action.JUMP
    elif buttonPress.button == GamePadButton.B:
        return Action.FIRE_BALL
    elif buttonPress.button == GamePadButton.DOWN:
        return Action.PIPE
    elif buttonPress.button == GamePadButton.START:
        return Action.DUMP_CANDY_LIGHT
    elif buttonPress.button == GamePadButton.SELECT:
        return Action.GO_ADMIN
    elif button_press.button == GamePadButton.UP:
        return Action.WORLD_CLEAR
    elif button_press.button == GamePadButton.LEFT:
        return Action.UNDERGROUND
    elif button_press.button == GamePadButton.RIGHT:
        return Action.PLAY
    
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
    elif buttonPress.button == GamePadButton.LEFT:
        return Action.PLATE_UP
    elif buttonPress.button == GamePadButton.RIGHT:
        return Action.PLATE_DOWN
    
    return None


# ============= Main Loop ============

logger.info('Staring the main LOOP...')

# the mode determines which actions are possible
mode = Mode.TRICK_OR_TREAT

# actions lock everything else from happening
current_action: Union[None, Action] = Action.START_UP

weigh_start_time:int = 0
weigh_start_threshold: WEIGHT_THRESHOLD = WEIGHT_THRESHOLD.NONE
dump_candy_start_time:int = 0

current_weight: Union[WEIGHT_THRESHOLD, None] = None

calibrate_scale()

while True:

    # ========== GET GAMEPAD INPUT ===========

    try:
        button_press = gamepad_q.get_nowait()
        empty_queue(gamepad_q)
    except:
        button_press = None

    # ========== GET GYRO INPUT ============

    did_jump = False

    try:
        did_jump = gyro_q.get_nowait()
        empty_queue(gyro_q)
    except:
        pass

    # ========== GET WEIGHT INPUT ============

    try:
        next_weight = scale_q.get_nowait()
        current_weight = current_weight if next_weight is None else next_weight
    except:
        pass
    

    # ========== GET ACTIONS BASED ON MODE ONLY IF ONE IS NOT ALREADY SET ============

    if current_action is None:

        if current_weight in SCALE_LOADED_WEIGHTS and not mode == Mode.TRICK_OR_TREAT_LOADED:
            # give the scale some time to reset after dumping because it will likely read weird while the servo motor is moving
            if (time.time() - dump_candy_start_time) > 6:
                mode = Mode.TRICK_OR_TREAT_LOADED
                weigh_start_time = time.time()
                weigh_start_threshold = current_weight
                current_action = Action.WEIGHT_DETECTED

        elif current_weight in SCALE_LOADED_WEIGHTS and mode == Mode.TRICK_OR_TREAT_LOADED:
            
            # give a little time on the scale, let the weight detected animation run
            if (time.time() - weigh_start_time) > 2:
                
                if current_weight == WEIGHT_THRESHOLD.LIGHT:
                    current_action = Action.DUMP_CANDY_LIGHT
                elif current_weight == WEIGHT_THRESHOLD.MEDIUM:
                    current_action = Action.DUMP_CANDY_MEDIUM
                elif current_weight == WEIGHT_THRESHOLD.HEAVY:
                    current_action = Action.DUMP_CANDY_HEAVY
                
                mode = Mode.TRICK_OR_TREAT
                dump_candy_start_time = time.time()

        elif current_weight not in SCALE_LOADED_WEIGHTS and mode == Mode.TRICK_OR_TREAT_LOADED:
            mode = Mode.TRICK_OR_TREAT
            current_action = Action.CLEAR

        elif did_jump:
            current_action = Action.JUMP

        elif button_press is not None:

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

        if current_action == Action.CLEAR:
            lights.run_animation(LIGHT_ANIMATION.CLEAR)

        if current_action == Action.JUMP:
            lights.run_animation(LIGHT_ANIMATION.JUMP)
            sounds.play_sound(SoundEffect.MARIO_JUMP)

        if current_action == Action.FIRE_BALL:
            lights.run_animation(LIGHT_ANIMATION.FIRE_BALL)  
            sounds.play_sound(SoundEffect.FIRE_BALL)

        if current_action == Action.PIPE:
            lights.run_animation(LIGHT_ANIMATION.PIPE)  
            sounds.play_sound(SoundEffect.PIPE)

        if current_action == Action.WORLD_CLEAR:
            lights.run_animation(LIGHT_ANIMATION.WORLD_CLEAR)
            sounds.play_sound(SoundEffect.WORLD_CLEAR)
            sleep(1.7)
            lights.run_animation(LIGHT_ANIMATION.WORLD_CLEAR)
            sleep(1.7)
            lights.run_animation(LIGHT_ANIMATION.WORLD_CLEAR)
            sleep(1.7)
            lights.run_animation(LIGHT_ANIMATION.WORLD_CLEAR)
            sleep(1.7)
            lights.run_animation(LIGHT_ANIMATION.FIRE_BALL)  
            sounds.play_sound(SoundEffect.FIREWORK)
            sleep(0.5)
            lights.run_animation(LIGHT_ANIMATION.FIRE_BALL)  
            sounds.play_sound(SoundEffect.FIREWORK)
            sleep(0.5)
            lights.run_animation(LIGHT_ANIMATION.FIRE_BALL)  
            sounds.play_sound(SoundEffect.FIREWORK)

        if current_action == Action.UNDERGROUND:
            sounds.play_sound(SoundEffect.UNDERGROUND)
            sleep(0.5)
            lights.run_animation(LIGHT_ANIMATION.UNDERGROUND)
            sleep(1.5)
            lights.run_animation(LIGHT_ANIMATION.UNDERGROUND)
            sleep(2)
            lights.run_animation(LIGHT_ANIMATION.UNDERGROUND)
            sleep(2)
            lights.run_animation(LIGHT_ANIMATION.UNDERGROUND)
            sleep(1.5)
            lights.run_animation(LIGHT_ANIMATION.UNDERGROUND_END)
            sleep(4)
            current_action = Action.CLEAR
            continue

        if current_action == Action.PLAY:
            sounds.play_sound(SoundEffect.PLAY)
            lights.run_animation(LIGHT_ANIMATION.PLAY)
            sleep(12)            
            current_action = Action.CLEAR
            continue

        if current_action == Action.DUMP_CANDY_LIGHT:
            lights.run_animation(LIGHT_ANIMATION.MARIO_COIN)  
            sounds.play_sound(SoundEffect.MARIO_COIN)
            sleep(1)
            servo.drop_and_reset_shelf()
            sleep(0.30)
            lights.run_animation(LIGHT_ANIMATION.POWER_UP)
            sounds.play_sound(SoundEffect.POWER_UP)  
            sleep(1.5)

        if current_action == Action.DUMP_CANDY_MEDIUM:
            lights.run_animation(LIGHT_ANIMATION.MARIO_COIN)  
            sounds.play_sound(SoundEffect.JUST_WHAT_I_NEEDED)
            sleep(1.5)
            servo.drop_and_reset_shelf()
            sleep(0.30)
            lights.run_animation(LIGHT_ANIMATION.FREE_GUY)  
            sounds.play_sound(SoundEffect.FREE_GUY)
            sleep(1.5)

        if current_action == Action.DUMP_CANDY_HEAVY:
            lights.run_animation(LIGHT_ANIMATION.MARIO_COIN)  
            sounds.play_sound(SoundEffect.MAMA_MIA)
            sleep(0.75)
            servo.drop_and_reset_shelf()
            sleep(0.30)
            lights.run_animation(LIGHT_ANIMATION.STAR_POWER)  
            sounds.play_sound(SoundEffect.STAR_POWER)
            sleep(12.5)
            lights.run_animation(LIGHT_ANIMATION.CLEAR)  

        if current_action == Action.WEIGHT_DETECTED:
            lights.run_animation(LIGHT_ANIMATION.WEIGHT_DETECTED)  
            sleep(1)

        if current_action == Action.GO_ADMIN:
            lights.run_animation(LIGHT_ANIMATION.ADMIN)
            sounds.play_sound(SoundEffect.MAMA_MIA)
            mode = Mode.ADMIN
        
        if current_action == Action.REBOOT:
            lights.run_animation(LIGHT_ANIMATION.FIRE_BALL)
            sounds.play_sound(SoundEffect.MARIO_DIE)
            sleep(3)
            reboot()

        if current_action == Action.VOLUME_UP:
            sounds.volume_up()

        if current_action == Action.VOLUME_DOWN:
            sounds.volume_down()

        if current_action == Action.PLATE_UP:
            servo.reset_shelf()
        
        if current_action == Action.PLATE_DOWN:
            servo.drop_shelf()

        if current_action == Action.CALIBRATE_SCALE:
            lights.run_animation(LIGHT_ANIMATION.WEIGHT_DETECTED)
            calibrate_scale()
            lights.run_animation(LIGHT_ANIMATION.ADMIN)
            sounds.play_sound(SoundEffect.YEAHOO)

        if current_action == Action.EXIT_ADMIN:
            servo.reset_shelf()
            mode = Mode.TRICK_OR_TREAT
            current_action = Action.START_UP
            continue
            
        current_action = None

    # otherwise we have an action going
    else:
        pass
  