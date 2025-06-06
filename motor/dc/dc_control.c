#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <pigpio.h>

#define DC_ENA 18  // PWM 핀
#define DC_DIR 23  // 방향 제어 핀
#define SPEED_FILE "/tmp/fan_speed.txt"

static int duty_cycle = 0;

int read_speed_from_file() {
    FILE *fp = fopen(SPEED_FILE, "r");
    if (fp == NULL) return -1;

    int speed;
    if (fscanf(fp, "%d", &speed) != 1) {
        fclose(fp);
        return -1;
    }
    fclose(fp);
    return speed;
}

int main() {
    if (gpioInitialise() < 0) {
        fprintf(stderr, "[C] pigpio 초기화 실패\n");
        return 1;
    }

    gpioSetMode(DC_ENA, PI_OUTPUT);
    gpioSetMode(DC_DIR, PI_OUTPUT);
    gpioWrite(DC_DIR, 1);  // 기본 방향 설정

    printf("[C] DC 모터 제어 시작\n");

    int current_duty = -1;

    while (1) {
        int new_speed = read_speed_from_file();  // 0~100
        if (new_speed >= 0 && new_speed <= 100) {
            int new_duty = (int)(255.0 * new_speed / 100.0);  // 0~255 변환
            if (new_duty != current_duty) {
                gpioPWM(DC_ENA, new_duty);  // 소프트 PWM 사용
                current_duty = new_duty;
                printf("[C] 속도 갱신: %d%% (%d/255)\n", new_speed, new_duty);
            }
        }
        usleep(200000);  // 200ms 간격
    }

    gpioTerminate();
    return 0;
}
