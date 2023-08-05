from adafruit_servokit import ServoKit

SERVO_FLAT_ANGLE = 40
SERVO_DROP_ANGLE = 130

servo_kit = ServoKit(channels=16)

class Servo:
    
    def __init__(self):
        servo_kit.servo[0].angle = SERVO_FLAT_ANGLE

    def reset_shelf():
        servo_kit.servo[0].angle = SERVO_FLAT_ANGLE

    def drop_shelf():
        servo_kit.servo[0].angle = SERVO_DROP_ANGLE