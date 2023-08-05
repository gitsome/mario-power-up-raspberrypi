import time
from time import sleep
import multiprocessing
from enum import Enum

from hx711 import HX711

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

class WEIGHT_THRESHOLD(Enum):
    LIGHT = 10
    MEDIUM = 30
    HEAVY = 80

def weight_loop(message_q, logger):

    global hx
    global did_detect_weight

    while True:

        weight = hx.get_weight_mean()

        if (weight > WEIGHT_THRESHOLD.HEAVY.value):
            # star
            message_q.put(WEIGHT_THRESHOLD.HEAVY)
        elif (weight > WEIGHT_THRESHOLD.MEDIUM.value):
            # just what i needed with power up
            message_q.put(WEIGHT_THRESHOLD.MEDIUM)
        elif (weight > WEIGHT_THRESHOLD.LIGHT.value):
            # yeahoo, coin
            message_q.put(WEIGHT_THRESHOLD.LIGHT)

class Scale:
    
    message_q: multiprocessing.Queue

    def __init__ (self, queue, logger):
      
        self.message_q = queue

        # create and start the scale listener
        scale_listener_process = multiprocessing.Process(target=weight_loop, args=(self.message_q, logger))
        scale_listener_process.start()