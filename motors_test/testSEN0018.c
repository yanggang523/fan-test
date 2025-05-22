#include <stdio.h>
#include <pigpio.h>
#include <unistd.h>

#define IR_PIN   2    // 적외선 센서 DO 핀 입력용 (BCM 번호)
#define LED_PIN  13   // 감지 시 점등될 LED 핀 (BCM 번호)

int main() {
    if (gpioInitialise() < 0) {
        fprintf(stderr, "pigpio 초기화 실패\n");
        return 1;
    }

    gpioSetMode(IR_PIN, PI_INPUT);       // 센서 입력 핀
    gpioSetMode(LED_PIN, PI_OUTPUT);     // LED 출력 핀

    printf("SEN0018 장애물 감지 시작 (1초 간격)\n");

    while (1) {
        int value = gpioRead(IR_PIN);

        if (value == 0) {
            // 장애물 감지
            gpioWrite(LED_PIN, 1);
            printf("[감지됨] 장애물이 앞에 있습니다.\n");
        } else {
            // 감지 안됨
            gpioWrite(LED_PIN, 0);
            printf("[없음]    앞에 장애물이 없습니다.\n");
        }

        sleep(1);  // 1초 대기
    }

    gpioTerminate();
    return 0;
}
