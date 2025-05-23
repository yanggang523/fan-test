import pigpio
import time
from config import STEP_DIR, STEP_STEP

def rotate_step_motor(steps, delay=0.005):
    pi = pigpio.pi()
    pi.set_mode(STEP_DIR, pigpio.OUTPUT)
    pi.set_mode(STEP_STEP, pigpio.OUTPUT)
    pi.write(STEP_DIR, 1)
    for _ in range(steps):
        pi.write(STEP_STEP, 1)
        time.sleep(delay)
        pi.write(STEP_STEP, 0)
        time.sleep(delay)
