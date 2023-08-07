import time
from time import sleep
import multiprocessing
from multiprocessing import Queue
from enum import Enum, auto
from utils import empty_queue

from hx711 import HX711

# ========== CALIBRATION ============
# input('Place weight then press Enter: ')
# reading = hx.get_data_mean(readings = 100)
# known_weight_grams_str = input('Tell me how many grams and press Enter: ')
# known_weight_grams = float(known_weight_grams_str)
# calibration_ratio = reading / known_weight_grams
# print("calibration_ratio:", calibration_ratio)

# 20g: 720.2, 50g: 622.94, 100g: 659.03 ( took the average over the 3 different weights )
CALIBARTION_RATIO = 667 

class CALIBRATION_MESSAGES(Enum):
    CALIBRATE = auto()
    CALIBRATION_COMPLETE = auto()

class WEIGHT_THRESHOLD(Enum):
    NONE = 0
    LIGHT = 10
    MEDIUM = 30
    HEAVY = 80

# a list of the weights that are associated to the state of being "loaded"
SCALE_LOADED_WEIGHTS = [
    WEIGHT_THRESHOLD.LIGHT,
    WEIGHT_THRESHOLD.MEDIUM,
    WEIGHT_THRESHOLD.HEAVY
]

def scale_loop(message_q, request_q, response_q):

    global CALIBARTION_RATIO
    hx = HX711(dout_pin=6, pd_sck_pin=5)
    is_calibrated = False

    while True:

        if is_calibrated:

            weight = hx.get_weight_mean(readings=10)

            # make sure only the latest is in the q
            empty_queue(message_q)

            if (weight > WEIGHT_THRESHOLD.HEAVY.value):
                # star
                message_q.put(WEIGHT_THRESHOLD.HEAVY)
            elif (weight > WEIGHT_THRESHOLD.MEDIUM.value):
                # just what i needed with power up
                message_q.put(WEIGHT_THRESHOLD.MEDIUM)
            elif (weight > WEIGHT_THRESHOLD.LIGHT.value):
                # yeahoo, coin
                message_q.put(WEIGHT_THRESHOLD.LIGHT)
            else:
                message_q.put(WEIGHT_THRESHOLD.NONE)

        # get our calibration state
        try:
            do_calibration = request_q.get_nowait()
        except:
            do_calibration = False

        if do_calibration == CALIBRATION_MESSAGES.CALIBRATE:

            is_calibrated = False

            # zero and calibrate the scale
            hx.zero()
            hx.set_scale_ratio(CALIBARTION_RATIO)

            response_q.put(CALIBRATION_MESSAGES.CALIBRATION_COMPLETE)
            is_calibrated = True
        
class Scale:
    
    message_q: multiprocessing.Queue
    calibrated = False

    def __init__ (self, logger, queue):
      
        self.message_q = queue
        self.logger = logger

        # create a separate q for sending messages into the process
        self.request_q = Queue()
        self.response_q = Queue()

        # create and start the scale listener
        scale_listener_process = multiprocessing.Process(target=scale_loop, args=(self.message_q, self.request_q, self.response_q))
        scale_listener_process.start()

    def calibrate(self):

        self.calibrated = False
        self.logger.info("calibrating scale....")

        # first clear the response_q and send out the resquest for calibration
        empty_queue(self.response_q)
        self.request_q.put(CALIBRATION_MESSAGES.CALIBRATE)

        # now wait for the calibration response
        calibration_message_received = False
        while not calibration_message_received:
            try:
                if self.response_q.get_nowait() == CALIBRATION_MESSAGES.CALIBRATION_COMPLETE:
                    calibration_message_received = True
            except:
                pass
    

        self.logger.info("calibration complete")
        self.calibrated = True
