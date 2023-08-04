from multiprocessing import Queue

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

class Lights:
    
    current_color_animation = None

    def __init__(self, message_q: Queue):
        self.message_q = message_q

    def animate(self):
        if self.current_color_animation is not None:
          if not current_color_animation.animate():
            current_color_animation = None