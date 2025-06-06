#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <pigpio.h>

#define PWM_PIN 18             // GPIO 18번 (hardware PWM)
#define SPEED_FILE "/tmp/fan_speed.txt"
#define MAX_DUTY 1000000       // pigpio는 0~100만 (1,000,000)

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
        fprintf(stderr, "pigpio 초기화 실패\n");
        return 1;
    }

    printf("💨 모터 제어 시작 (pigpio)\n");

    int current_speed = -1;

    while (1) {
        int new_speed = read_speed_from_file();
        if (new_speed >= 0 && new_speed <= 100) {
            if (new_speed != current_speed) {
                int duty = (int)(MAX_DUTY * new_speed / 100.0);
                gpioHardwarePWM(PWM_PIN, 25000, duty);  // 25kHz PWM
                current_speed = new_speed;
                printf("PWM 속도 변경: %d%% (%d)\n", new_speed, duty);
            }
        }
        usleep(200000);  // 200ms 대기
    }

    gpioTerminate();
    return 0;
}
