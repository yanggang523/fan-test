// log_control.c
#include <stdio.h>

void setup_mock() {
    printf("[C] 시스템 준비 완료 (setup_mock)\n");
}

void start_log() {
    printf("[C] 모터 시작 로그 기록 (start_log)\n");
}

void stop_log() {
    printf("[C] 모터 정지 로그 기록 (stop_log)\n");
}
