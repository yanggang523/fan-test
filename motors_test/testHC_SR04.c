#include <stdio.h>
#include <pigpio.h>
#include <unistd.h>

#define TRIG 23  // BCM23 (물리핀 16)
#define ECHO 24  // BCM24 (물리핀 18)

float getDistance() {
    gpioWrite(TRIG, 0);
    gpioDelay(2);

    // 트리거 핀에 10us HIGH 펄스
    gpioWrite(TRIG, 1);
    gpioDelay(10);
    gpioWrite(TRIG, 0);

    // Echo 핀이 HIGH가 될 때까지 대기
    uint32_t startTick = gpioTick();
    while (gpioRead(ECHO) == 0) {
        if (gpioTick() - startTick > 100000) return -1;  // 100ms 타임아웃
    }
    uint32_t echoStart = gpioTick();

    // Echo 핀이 LOW가 될 때까지 대기
    while (gpioRead(ECHO) == 1) {
        if (gpioTick() - echoStart > 30000) return -1;  // 30ms 타임아웃
    }
    uint32_t echoEnd = gpioTick();

    uint32_t travelTime = echoEnd - echoStart;  // μs
    float distance = travelTime * 0.0343f / 2.0f;

    return distance;
}

int main() {
    if (gpioInitialise() < 0) {
        fprintf(stderr, "pigpio 초기화 실패\n");
        return 1;
    }

    gpioSetMode(TRIG, PI_OUTPUT);
    gpioSetMode(ECHO, PI_INPUT);

    gpioWrite(TRIG, 0);
    gpioDelay(50000);  // 안정화 대기 50ms

    while (1) {
        float d = getDistance();
        if (d < 0) {
            printf("타임아웃 또는 센서 오류\n");
        } else {
            printf("거리: %.2f cm\n", d);
        }

        gpioDelay(500000);  // 0.5초 대기
    }

    gpioTerminate();
    return 0;
}
