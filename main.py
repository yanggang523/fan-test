from motor.dc.dc_motor_wrapper import DCMotor
from motor.step.step_control import rotate_step_motor_to
from sensor.sr04 import detect_direction, get_distance, setup_ultrasonic_sensors
from sensor.camera import detect_gesture
from sensor.camera_stream import start_stream
from config import DISTANCE_THRESHOLD, ULTRASONIC_SENSORS, Gesture

import RPi.GPIO as GPIO
import time

if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    setup_ultrasonic_sensors()
    dc_motor = DCMotor()
    prev_gesture = None
    prev_direction = None
    hold_counter = 0

    ffmpeg_proc, cam_proc = start_stream()

    try:
        while True:
            gesture = detect_gesture(ffmpeg_proc)
            direction = detect_direction()
            center_distance = get_distance(
                trig_pin=ULTRASONIC_SENSORS['center']['TRIG'],
                echo_pin=ULTRASONIC_SENSORS['center']['ECHO']
            )

            if center_distance != -1:
                print(f"[INFO] 거리 측정: {center_distance:.2f} cm")
            else:
                print("[WARN] 거리 측정 실패")

            # DC 모터 제어
            if gesture == Gesture.THUMBS_UP:
                dc_motor.start()
                hold_counter = 0
            elif gesture == Gesture.FIST:
                dc_motor.stop()
                hold_counter = 0
            elif gesture == Gesture.PALM:
                if prev_gesture == Gesture.PALM:
                    hold_counter += 1
                else:
                    hold_counter = 1

                # 1.5초마다 속도 증가 (0.3s × 5)
                if hold_counter % 5 == 0 and dc_motor.speed < dc_motor.max_speed:
                    dc_motor.increase_speed()
            elif gesture == Gesture.THUMBS_DOWN:
                dc_motor.decrease_speed()
                hold_counter = 0
            else:
                hold_counter = 0

            prev_gesture = gesture

            # 스텝모터 방향 회전 (중복 회전 방지)
            if direction != prev_direction:
                if direction == 'left':
                    rotate_step_motor_to(-90)
                elif direction == 'right':
                    rotate_step_motor_to(90)
                elif direction == 'center':
                    rotate_step_motor_to(0)
                prev_direction = direction

            # 거리 기반 자동 팬 반응 (단, 속도 제한)
            if center_distance != -1 and center_distance < DISTANCE_THRESHOLD:
                print("[INFO] 거리 기준 이하 → 팬 반응")
                if dc_motor.speed  < dc_motor.max_speed:
                    dc_motor.increase_speed()

            time.sleep(0.1)

    except Exception as e:
        print(f"[ERROR] 예외 발생: {e}")

    finally:
        ffmpeg_proc.terminate()
        cam_proc.terminate()
        GPIO.cleanup()
        print("[INFO] 시스템 안전 종료 완료")
