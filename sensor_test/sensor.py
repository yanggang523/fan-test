import RPi.GPIO as GPIO
import time

# 핀 번호 설정
TRIG = 23
ECHO = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

def get_distance():
    # 초음파 발생
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    # ECHO 핀에서 신호 받기 (펄스 시작 시간 측정)
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    # 펄스 끝 시간 측정
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    # 거리 계산 (속도: 34300 cm/s)
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150  # 왕복이므로 반 나눔
    distance = round(distance, 2)

    return distance

try:
    while True:
        dist = get_distance()
        print(f"Distance: {dist} cm")
        time.sleep(1)

except KeyboardInterrupt:
    print("측정 종료")
    GPIO.cleanup()
