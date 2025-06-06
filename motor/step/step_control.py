import pigpio
import time
import os
from config import STEP_DIR, STEP_STEP

STEPS_PER_DEGREE = 200 / 360
STATE_FILE = "/tmp/step_motor_angle.txt"

def load_current_angle():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return int(f.read())
        except:
            return 0
    return 0

def save_current_angle(angle):
    with open(STATE_FILE, "w") as f:
        f.write(str(angle))

current_angle = load_current_angle()

def rotate_step_motor_to(target_angle, delay=0.005):
    global current_angle

    target_angle = max(-90, min(90, target_angle))
    delta = target_angle - current_angle
    steps = int(abs(delta) * STEPS_PER_DEGREE)

    if steps == 0:
        return

    direction = 1 if delta > 0 else 0

    pi = pigpio.pi()
    if not pi.connected:
        print("[ERROR] pigpio 연결 실패")
        return

    pi.set_mode(STEP_DIR, pigpio.OUTPUT)
    pi.set_mode(STEP_STEP, pigpio.OUTPUT)
    pi.write(STEP_DIR, direction)

    for _ in range(steps):
        pi.write(STEP_STEP, 1)
        time.sleep(delay)
        pi.write(STEP_STEP, 0)
        time.sleep(delay)

    current_angle = target_angle
    save_current_angle(current_angle)
    pi.stop()
