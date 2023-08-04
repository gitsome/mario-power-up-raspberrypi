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

def sensor_weight():

  global hx

  while True:

    reading = hx.get_weight_mean()
      
    if (reading > 80):
      play_mario_star()
      servo_kit.servo[0].angle = SERVO_DROP_ANGLE
    elif (reading > 30):
      play_mario_just_what_i_needed()
      time.sleep(1.25)
      play_mario_power_up()
      servo_kit.servo[0].angle = SERVO_DROP_ANGLE
    elif (reading > 10):
      play_mario_yeahoo()
      time.sleep(0.75)
      play_mario_coin()
      servo_kit.servo[0].angle = SERVO_DROP_ANGLE
    else:
       servo_kit.servo[0].angle = SERVO_FLAT_ANGLE

weight_thread = threading.Thread(target=sensor_weight, args=()) 
weight_thread.start()