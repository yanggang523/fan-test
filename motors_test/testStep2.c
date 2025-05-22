#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <pigpio.h>
#include <unistd.h>

#define DIR_PIN         5     // BCM5
#define STEP_PIN        6     // BCM6
#define STEPS_PER_REV   200
#define DIR_CW          1
#define DIR_CCW         0

// 1분(μs) / (스텝 수 * RPM * 2)
static int calcDelayUs(int rpm) {
    return 60000000 / (STEPS_PER_REV * rpm * 2);
}

void cleanupMotor() {
    gpioTerminate();
}

void onSignal(int sig) {
    cleanupMotor();
    exit(0);
}

void stepMotor(int direction, int steps, int delay_us) {
    gpioWrite(DIR_PIN, direction);
    for (int i = 0; i < steps; i++) {
        gpioWrite(STEP_PIN, 1);
        gpioDelay(delay_us);
        gpioWrite(STEP_PIN, 0);
        gpioDelay(delay_us);
    }
}

void initMotor() {
    if (gpioInitialise() < 0) {
        fprintf(stderr, "pigpio 초기화 실패\n");
        exit(1);
    }
    if (gpioSetMode(DIR_PIN, PI_OUTPUT) != 0 ||
        gpioSetMode(STEP_PIN, PI_OUTPUT) != 0) {
        fprintf(stderr, "핀 모드 설정 실패\n");
        cleanupMotor();
        exit(1);
    }
    signal(SIGINT, onSignal);
    signal(SIGTERM, onSignal);
}

int main() {
    initMotor();

    printf("시계방향 회전\n");
    stepMotor(DIR_CW, STEPS_PER_REV, calcDelayUs(60));

    gpioDelay(50000);  // 50ms 휴지

    printf("반시계방향 회전\n");
    stepMotor(DIR_CCW, STEPS_PER_REV, calcDelayUs(60));

    printf("정지 및 종료\n");
    cleanupMotor();
    return 0;
}
