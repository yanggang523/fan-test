## This code controls a DC motor using the pigpio library.
from motor.dc.dc_motor_wrapper import DCMotor
from motor.step.step_control import rotate_step_motor
from sensor.sr04 import get_distance
from sensor.camera import detect_gesture
from config import DISTANCE_THRESHOLD

import time

if __name__ == '__main__':
    dc_motor = DCMotor()

    while True:
        distance = get_distance()

        # 거리 측정 실패한 경우 무시하고 다음 반복
        if distance == -1:
            print("[WARN] 거리 측정 실패. 다시 시도합니다.")
            time.sleep(0.2)
            continue

        print(f"[INFO] 거리 측정: {distance:.2f} cm")

        # 제스처 인식이 추가될 경우 아래 부분 활성화
        # gesture = detect_gesture()
        # if gesture == '1':
        #     dc_motor.start()
        # elif gesture == '2':
        #     dc_motor.stop()
        # elif gesture == '3':
        #     dc_motor.increase_speed()
        # elif gesture == '4':
        #     dc_motor.decrease_speed()

        if distance < DISTANCE_THRESHOLD:
            print("[INFO] 거리 기준치 이하 → 모터 동작")
            rotate_step_motor(200)
            dc_motor.increase_speed()

        time.sleep(0.5)