import pigpio
import time
import os
from config import STEP_DIR, STEP_STEP

# 실제 드라이버의 마이크로스텝 설정을 확인해서 STEPS_PER_REV 값을 정확히 맞춰주세요.
# 예) 1/1 스텝이면 200, 1/8 스텝이면 200*8=1600
STEPS_PER_REV = 200
STEPS_PER_DEGREE = STEPS_PER_REV / 360.0

STATE_FILE = "/tmp/step_motor_state.txt"

# residual: 남은 소수점 스텝 오차 누적
residual_steps = 0.0

# 이동 폭을 몇 배로 할지 조정하는 상수 (기본 1.0, 2.0이면 두 배 이동)
MOVEMENT_SCALE = 2.0

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                angle, res = f.read().split(',')
                return float(angle), float(res)
        except:
            pass
    return 0.0, 0.0

def save_state(angle, residual):
    with open(STATE_FILE, "w") as f:
        f.write(f"{angle},{residual}")

current_angle, residual_steps = load_state()

def rotate_step_motor_to(target_angle, delay=0.005):
    global current_angle, residual_steps

    # 허용 범위로 클램프 (필요에 따라 ±180 등으로 확장 가능)
    target_angle = max(-90.0, min(90.0, float(target_angle)))

    # 원래 이동해야 할 각도 차이
    raw_delta = target_angle - current_angle

    # 이동 배율 적용
    scaled_delta = raw_delta * MOVEMENT_SCALE

    # 배율 적용된 각도를 스텝으로 변환 (소수점 포함)
    steps_float = scaled_delta * STEPS_PER_DEGREE + residual_steps
    direction   = 1 if steps_float > 0 else 0
    steps_to_move = int(abs(round(steps_float)))

    if steps_to_move == 0:
        return

    # 실제 이동한 스텝 수로 오차 및 누적 보정
    actual_moved_steps = steps_to_move if steps_float > 0 else -steps_to_move
    residual_steps = steps_float - actual_moved_steps

    # GPIO 초기화
    pi = pigpio.pi()
    if not pi.connected:
        print("[ERROR] pigpio 연결 실패")
        return
    pi.set_mode(STEP_DIR, pigpio.OUTPUT)
    pi.set_mode(STEP_STEP, pigpio.OUTPUT)
    pi.write(STEP_DIR, direction)

    # 스텝 펄스 발생
    for _ in range(abs(steps_to_move)):
        pi.write(STEP_STEP, 1)
        time.sleep(delay)
        pi.write(STEP_STEP, 0)
        time.sleep(delay)

    # 실제 이동한 각도(배율 포함)로 current_angle 갱신
    actual_moved_angle = actual_moved_steps / STEPS_PER_DEGREE
    current_angle += actual_moved_angle

    save_state(current_angle, residual_steps)
    pi.stop()
