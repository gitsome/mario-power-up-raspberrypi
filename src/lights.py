import multiprocessing
import threading
from enum import Enum, auto
from typing import Union
from time import sleep

from rpi_ws281x import *

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

from utils import empty_queue

NUM_PIXELS = 24

print(dir(board))
# pixels = neopixel.NeoPixel(board.D12, NUM_PIXELS, brightness=0.1, auto_write=False, pixel_order=neopixel.GRB)
pixels = neopixel_spi.NeoPixel_SPI(board.SPI(), NUM_PIXELS, brightness=0.8, auto_write=False, pixel_order=neopixel.GRB)

comet_yellow = Comet(pixels, speed=0.04, color=YELLOW, tail_length=6, bounce=False, ring=True)
comet_white = Comet(pixels, speed=0.02, color=WHITE, tail_length=6, bounce=False, ring=True)
pulse_black = Pulse(pixels, speed=0.1, color=BLACK, period=0.1)
solid_green = Solid(pixels, color=GREEN)
solid_black = Solid(pixels, color=BLACK)
solid_white = Solid(pixels, color=WHITE)
pulse_red = Pulse(pixels, speed=0.005, color=RED, period=0.5)
pulse_yellow = Pulse(pixels, speed=0.01, color=YELLOW, period=1)
pulse_white = Pulse(pixels, speed=0.05, color=WHITE, period=1)
pulse_green = Pulse(pixels, speed=0.05, color=GREEN, period=1.5)
pulse_purple = Pulse(pixels, speed=0.05, color=PURPLE, period=2)

idle_animation = AnimationSequence(pulse_white, pulse_black, advance_interval=1, auto_clear=True)
waiting_animation = comet_white

star_animation = ColorCycle(pixels, 0.3, colors=[ORANGE, YELLOW, WHITE])
coin_animation = pulse_yellow
pipe_animation = pulse_green
jump_animation = solid_white
fireball_animation = pulse_red

class AnimationConfig():
    def __init__(self, animation, repeat=False):
        self.animation = animation
        self.repeat = repeat


class LIGHT_ANIMATION(Enum):
    JUMP = auto()
    FIRE_BALL = auto()
    PIPE = auto()
    MARIO_COIN = auto()
    ADMIN = auto()
    WEIGHT_DETECTED = auto()

LIGHT_ANIMATION_MAP = {
    LIGHT_ANIMATION.JUMP: lambda : AnimationConfig(AnimateOnce(pulse_white)),
    LIGHT_ANIMATION.FIRE_BALL: lambda : AnimationConfig(AnimateOnce(fireball_animation)),
    LIGHT_ANIMATION.PIPE: lambda : AnimationConfig(AnimateOnce(pipe_animation)),
    LIGHT_ANIMATION.MARIO_COIN: lambda: AnimationConfig(AnimateOnce(coin_animation)),
    LIGHT_ANIMATION.ADMIN: lambda: AnimationConfig(Pulse(pixels, speed=0.01, color=TEAL, period=0.6),  True),
    LIGHT_ANIMATION.WEIGHT_DETECTED: lambda: AnimationConfig(Comet(pixels, speed=0.02, color=WHITE, tail_length=6, bounce=False, ring=True), True)
}


def animation_loop(q: multiprocessing.Queue, logger):

    current_light_animation = None

    while True:

        try:
            next_light_animation: Union[None, LIGHT_ANIMATION] = q.get_nowait()
            empty_queue(q)
        except:
            next_light_animation = None

        if next_light_animation is not None:

            if current_light_animation is not None:
                current_light_animation.animation.reset()

            current_light_animation = LIGHT_ANIMATION_MAP[next_light_animation]()
            current_light_animation.animation.reset()

        if current_light_animation is not None:

            animate_result = current_light_animation.animation.animate()

            if not current_light_animation.repeat and not animate_result:
                current_light_animation = None


class Lights:
    
    current_light_animation = None

    def __init__(self, logger):
        self.message_q = multiprocessing.Queue()

        # create and start the light animation process
        lights_listener_process = multiprocessing.Process(target=animation_loop, args=(self.message_q, logger))
        lights_listener_process.start()

    def run_animation(self, animation: LIGHT_ANIMATION):

        self.message_q.put(animation)