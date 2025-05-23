import RPi.GPIO as GPIO
import time
from config import TRIG, ECHO, DISTANCE_THRESHOLD

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

def get_distance():
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    pulse_start = None
    pulse_end = None

    timeout = time.time() + 0.04
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
        if time.time() > timeout:
            print("[WARN] ECHO 신호 시작 타임아웃")
            return -1

    timeout = time.time() + 0.04
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
        if time.time() > timeout:
            print("[WARN] ECHO 신호 끝 타임아웃")
            return -1

    if pulse_start is None or pulse_end is None:
        print("[WARN] pulse 값이 비정상")
        return -1

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 34300 / 2
    return distance
