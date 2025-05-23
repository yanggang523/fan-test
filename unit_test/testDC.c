#include <stdio.h>
#include <pigpio.h>
#include <unistd.h>

#define PWM_PIN 18      // 하드웨어 PWM (GPIO 18)
#define DIR_PIN 23      // 방향 제어용 일반 출력

#define PWM_FREQ 10000  // 10kHz (MD10C는 최대 20kHz)
#define STEP_DELAY 100  // 각 단계 간 지연 (ms)
#define MAX_DUTY 1000000  // pigpio에서는 1,000,000이 100% duty

void rampUpDown(int direction) {
    gpioWrite(DIR_PIN, direction);  // 방향 설정

    // 천천히 속도 증가 (0% → 100%)
    for (int duty = 0; duty <= MAX_DUTY; duty += 50000) {
        gpioHardwarePWM(PWM_PIN, PWM_FREQ, duty);
        time_sleep(STEP_DELAY / 1000.0);
    }

    // 잠시 유지
    sleep(2);

    // 천천히 속도 감소 (100% → 0%)
    for (int duty = MAX_DUTY; duty >= 0; duty -= 50000) {
        gpioHardwarePWM(PWM_PIN, PWM_FREQ, duty);
        time_sleep(STEP_DELAY / 1000.0);
    }
}

int main() {
    if (gpioInitialise() < 0) {
        printf("pigpio 초기화 실패\n");
        return 1;
    }

    gpioSetMode(DIR_PIN, PI_OUTPUT);

    printf("모터 전진 (방향: LOW)\n");
    rampUpDown(0);  // 전진

    sleep(1);

    printf("모터 후진 (방향: HIGH)\n");
    rampUpDown(1);  // 후진

    gpioHardwarePWM(PWM_PIN, 0, 0);  // PWM 정지
    gpioTerminate();
    printf("모터 정지\n");
    return 0;
}
