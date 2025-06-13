import pigpio
import time
import os
from config import STEP_DIR, STEP_STEP

# 실제 드라이버의 마이크로스텝 설정을 확인해서 STEPS_PER_REV 값을 정확히 맞춰주세요.
# 예) 1/1 스텝이면 200, 1/8 스텝이면 200*8=1600
STEPS_PER_REV = 200  
STEPS_PER_DEGREE = STEPS_PER_REV / 360.0

STATE_FILE = "/tmp/step_motor_state.txt"

# residual: 남은 소수점 스텝 오차를 누적 보관
residual_steps = 0.0

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

    # 허용 범위로 클램프
    target_angle = max(-90.0, min(90.0, float(target_angle)))
    delta = target_angle - current_angle

    # 방향과 필요한 총 스텝(소수 포함)
    steps_float = delta * STEPS_PER_DEGREE + residual_steps
    direction = 1 if steps_float > 0 else 0
    steps_to_move = int(abs(round(steps_float)))

    if steps_to_move == 0:
        return

    # 남은 소수점 오차 갱신
    actual_moved = steps_to_move if steps_float > 0 else -steps_to_move
    residual_steps = steps_float - actual_moved

    # GPIO 세팅
    pi = pigpio.pi()
    if not pi.connected:
        print("[ERROR] pigpio 연결 실패")
        return
    pi.set_mode(STEP_DIR, pigpio.OUTPUT)
    pi.set_mode(STEP_STEP, pigpio.OUTPUT)
    pi.write(STEP_DIR, direction)

    # 스텝 펄스
    for _ in range(abs(steps_to_move)):
        pi.write(STEP_STEP, 1)
        time.sleep(delay)
        pi.write(STEP_STEP, 0)
        time.sleep(delay)

    # 실제 각도 반영(정확히 맞춘 스텝으로)
    current_angle += actual_moved / STEPS_PER_DEGREE
    save_state(current_angle, residual_steps)
    pi.stop()
