import RPi.GPIO as GPIO
import time
from config import ULTRASONIC_SENSORS

GPIO.setmode(GPIO.BCM)

def setup_ultrasonic_sensors():
    for sensor in ULTRASONIC_SENSORS.values():
        GPIO.setup(sensor['TRIG'], GPIO.OUT)
        GPIO.setup(sensor['ECHO'], GPIO.IN)


def get_distance(trig_pin, echo_pin):
    GPIO.output(trig_pin, True)
    time.sleep(0.00001)
    GPIO.output(trig_pin, False)

    pulse_start = None
    pulse_end = None
    timeout = time.time() + 0.04

    while GPIO.input(echo_pin) == 0:
        pulse_start = time.time()
        if time.time() > timeout:
            return -1

    timeout = time.time() + 0.04
    while GPIO.input(echo_pin) == 1:
        pulse_end = time.time()
        if time.time() > timeout:
            return -1

    if pulse_start is None or pulse_end is None:
        return -1

    pulse_duration = pulse_end - pulse_start
    return pulse_duration * 34300 / 2

def detect_direction():
    distances = {}
    for name, pins in ULTRASONIC_SENSORS.items():
        dist = get_distance(pins['TRIG'], pins['ECHO'])
        distances[name] = dist if dist != -1 else float('inf')

    closest = min(distances, key=distances.get)
    print(f"[INFO] 측정 거리: {distances}, 가장 가까운 방향: {closest.upper()}")
    return closest
