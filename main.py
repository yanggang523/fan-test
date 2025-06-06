from motor.dc.dc_motor_wrapper import DCMotor
from motor.step.step_control import rotate_step_motor
from sensor.sr04 import get_distance
from sensor.camera import detect_gesture
from config import DISTANCE_THRESHOLD

import time

if __name__ == '__main__':
    dc_motor = DCMotor()  # pigpio C 프로그램과 연결되는 wrapper
    prev_gesture = None
    hold_counter = 0

    while True:
        distance = get_distance()

        if distance == -1:
            print("[WARN] 거리 측정 실패. 다시 시도합니다.")
            time.sleep(0.2)
            continue

        print(f"[INFO] 거리 측정: {distance:.2f} cm")

        gesture = detect_gesture()

        if gesture == '1':  # start
            dc_motor.start()

        elif gesture == '2':  # stop
            dc_motor.stop()
            hold_counter = 0

        elif gesture == '3':  # 유지 시 속도 증가
            if prev_gesture == '3':
                hold_counter += 1
            else:
                hold_counter = 1

            if hold_counter % 5 == 0:
                dc_motor.increase_speed()

        elif gesture == '4':  # 속도 감소
            dc_motor.decrease_speed()
            hold_counter = 0

        else:
            # 손이 인식 안 된 경우 → 속도 유지
            hold_counter = 0

        prev_gesture = gesture

        if distance < DISTANCE_THRESHOLD:
            print("[INFO] 거리 기준치 이하 → 모터 동작")
            rotate_step_motor(200)
            dc_motor.increase_speed()

        time.sleep(0.2)
