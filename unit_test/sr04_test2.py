import RPi.GPIO as GPIO
import time

# 테스트할 핀 번호 설정 (BCM 모드 기준)
TRIG = 22
ECHO = 10

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)
    print("[INFO] 핀 설정 완료")

def get_distance():
    # 트리거 펄스 보내기
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
            print("[WARN] ECHO 신호 종료 타임아웃")
            return -1

    if pulse_start is None or pulse_end is None:
        return -1

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 34300 / 2
    return distance

def loop():
    try:
        while True:
            distance = get_distance()
            if distance != -1:
                print(f"[INFO] 측정 거리: {distance:.2f} cm")
            else:
                print("[WARN] 거리 측정 실패")
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n[INFO] 사용자 중단")
    finally:
        GPIO.cleanup()
        print("[INFO] GPIO 정리 완료")

if __name__ == '__main__':
    setup()
    loop()
