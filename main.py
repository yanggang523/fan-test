from motor.dc.dc_motor_wrapper import DCMotor
from motor.step.step_control import rotate_step_motor_to
from sensor.sr04 import detect_direction, get_distance
from sensor.camera import detect_gesture
from sensor.camera_stream import start_stream
from config import DISTANCE_THRESHOLD, ULTRASONIC_SENSORS, Gesture
from sensor.sr04 import setup_ultrasonic_sensors
import RPi.GPIO as GPIO

import time

if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)  
    setup_ultrasonic_sensors()  
    dc_motor = DCMotor()
    prev_gesture = None
    hold_counter = 0
    

    ffmpeg_proc, cam_proc = start_stream()

    try:
        while True:
            gesture = detect_gesture(ffmpeg_proc)
            direction = detect_direction()
            distance = get_distance(trig_pin=ULTRASONIC_SENSORS['center']['TRIG'],
                                    echo_pin=ULTRASONIC_SENSORS['center']['ECHO'])

            if distance != -1:
                print(f"[INFO] 거리 측정: {distance:.2f} cm")
            else:
                print("[WARN] 거리 측정 실패")

            # 제스처 기반 DC 모터 제어
            if gesture == Gesture.THUMBS_UP:
                dc_motor.start()
            elif gesture == Gesture.THUMBS_DOWN:
                dc_motor.stop()
                hold_counter = 0
            elif gesture == Gesture.PALM:
                if prev_gesture == Gesture.PALM:
                    hold_counter += 1
                else:
                    hold_counter = 1
                if hold_counter % 5 == 0:
                    dc_motor.increase_speed()
            elif gesture == Gesture.FIST:
                dc_motor.decrease_speed()
                hold_counter = 0
            else:
                hold_counter = 0

            prev_gesture = gesture

            # 스텝모터 방향 회전
            if direction == 'left':
                rotate_step_motor_to(-90)
            elif direction == 'right':
                rotate_step_motor_to(90)
            elif direction == 'center':
                rotate_step_motor_to(0)

            # 거리 기준 이하 → 팬 작동 강화
            if distance != -1 and distance < DISTANCE_THRESHOLD:
                print("[INFO] 거리 기준 이하 → 팬 반응")
                dc_motor.increase_speed()

            time.sleep(0.2)

    finally:
        ffmpeg_proc.terminate()
        cam_proc.terminate()
        GPIO.cleanup()
