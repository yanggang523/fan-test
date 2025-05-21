#include <stdio.h>
#include <pigpio.h>
#include <unistd.h>
#include <time.h>

// DC 모터 핀 (L298N 기준)
#define DC_ENA 18  // PWM (GPIO18)
#define DC_IN1 23
#define DC_IN2 24

// 스텝 모터 핀 (ULN2003 기준)
#define ST_IN1 17
#define ST_IN2 27
#define ST_IN3 22
#define ST_IN4 5

// full-step dual-coil 시퀀스 (토크 최대화)
void stepSequence(int step) {
    const int seq[4][4] = {
        {1, 1, 0, 0},
        {0, 1, 1, 0},
        {0, 0, 1, 1},
        {1, 0, 0, 1}
    };
    gpioWrite(ST_IN1, seq[step][0]);
    gpioWrite(ST_IN2, seq[step][1]);
    gpioWrite(ST_IN3, seq[step][2]);
    gpioWrite(ST_IN4, seq[step][3]);
}

int main() {
    // pigpio 초기화
    if (gpioInitialise() < 0) {
        fprintf(stderr, "pigpio 초기화 실패\n");
        return 1;
    }

    // 핀 모드 설정
    gpioSetMode(DC_ENA, PI_OUTPUT);
    gpioSetMode(DC_IN1, PI_OUTPUT);
    gpioSetMode(DC_IN2, PI_OUTPUT);
    gpioSetMode(ST_IN1, PI_OUTPUT);
    gpioSetMode(ST_IN2, PI_OUTPUT);
    gpioSetMode(ST_IN3, PI_OUTPUT);
    gpioSetMode(ST_IN4, PI_OUTPUT);

    // DC 모터 정방향 회전: IN1=1, IN2=0, PWM 듀티 70%
    gpioWrite(DC_IN1, 1);
    gpioWrite(DC_IN2, 0);
    gpioPWM(DC_ENA, 180);  // 0~255

    printf("모터 테스트 시작 (20초간)\n");

    time_t start = time(NULL);
    int step = 0;

    // 20초 동안 스텝모터 구동
    while (time(NULL) - start < 20) {
        stepSequence(step);
        step = (step + 1) % 4;
        gpioDelay(5000);  // 5ms 지연 (토크 최적화 및 진동 완화)
    }

    // DC 모터 정지
    gpioPWM(DC_ENA, 0);
    gpioWrite(DC_IN1, 0);
    gpioWrite(DC_IN2, 0);

    // 스텝모터 핀 모두 LOW
    gpioWrite(ST_IN1, 0);
    gpioWrite(ST_IN2, 0);
    gpioWrite(ST_IN3, 0);
    gpioWrite(ST_IN4, 0);

    // 종료
    gpioTerminate();
    printf("모터 테스트 종료\n");
    return 0;
}
