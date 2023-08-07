from adafruit_servokit import ServoKit
from time import sleep

SERVO_FLAT_ANGLE = 36
SERVO_DROP_ANGLE = 122

servo_kit = ServoKit(channels=16)

class Servo:
    
    def __init__(self):
        servo_kit.servo[0].angle = SERVO_FLAT_ANGLE

    def reset_shelf(self):
        servo_kit.servo[0].angle = SERVO_FLAT_ANGLE

    def drop_shelf(self):
        servo_kit.servo[0].angle = SERVO_DROP_ANGLE

    def drop_and_reset_shelf(self):
        self.drop_shelf()
        sleep(0.75)
        self.reset_shelf()