## This code controls a DC motor using the pigpio library.
from motor.dc.dc_motor_wrapper import DCMotor
from motor.step.step_control import rotate_step_motor
from sensor.sr04 import get_distance
# from sensor.camera import detect_gesture
from config import DISTANCE_THRESHOLD

import time

if __name__ == '__main__':
    dc_motor = DCMotor()

    while True:
        # gesture = detect_gesture()
        distance = get_distance()

        # if gesture == '1':
        #     dc_motor.start()
        # elif gesture == '2':
        #     dc_motor.stop()
        # elif gesture == '3':
        #     dc_motor.increase_speed()
        # elif gesture == '4':
        #     dc_motor.decrease_speed()

        if distance < DISTANCE_THRESHOLD:
            rotate_step_motor(200)
            dc_motor.increase_speed()

        time.sleep(0.5)
