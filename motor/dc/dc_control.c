#include <pigpio.h>
#include <stdio.h>

#define DC_ENA 18
#define DC_DIR 23 

static int duty_cycle = 128;

void setup_dc_motor() {
    if (gpioInitialise() < 0) {
        printf("[C] pigpio 초기화 실패\n");
        return;
    }
    gpioSetMode(DC_ENA, PI_OUTPUT);
    gpioSetMode(DC_DIR, PI_OUTPUT);
    printf("[C] DC 모터 GPIO 설정 완료\n");
}

void start_motor() {
    gpioPWM(DC_ENA, duty_cycle);
    gpioWrite(DC_DIR, 1);
    printf("[C] DC 모터 시작\n");
}

void stop_motor() {
    gpioPWM(DC_ENA, 0);
    printf("[C] DC 모터 정지\n");
}

void increase_speed() {
    duty_cycle += 32;
    if (duty_cycle > 255) duty_cycle = 255;
    gpioPWM(DC_ENA, duty_cycle);
    printf("[C] 속도 증가: %d\n", duty_cycle);
}

void decrease_speed() {
    duty_cycle -= 32;
    if (duty_cycle < 0) duty_cycle = 0;
    gpioPWM(DC_ENA, duty_cycle);
    printf("[C] 속도 감소: %d\n", duty_cycle);
}

