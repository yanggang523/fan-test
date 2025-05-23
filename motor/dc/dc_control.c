#include <stdio.h>
#include <pigpio.h>

#define DC_ENA 18
#define DC_DIR 23
static int duty_cycle = 128;

void setup_dc_motor() {
    gpioSetMode(DC_ENA, PI_OUTPUT);
    gpioSetMode(DC_DIR, PI_OUTPUT);
}

void start_motor() {
    gpioPWM(DC_ENA, duty_cycle);
    gpioWrite(DC_DIR, 1);
}

void stop_motor() {
    gpioPWM(DC_ENA, 0);
}

void increase_speed() {
    duty_cycle = duty_cycle + 32 > 255 ? 255 : duty_cycle + 32;
    gpioPWM(DC_ENA, duty_cycle);
}

void decrease_speed() {
    duty_cycle = duty_cycle - 32 < 0 ? 0 : duty_cycle - 32;
    gpioPWM(DC_ENA, duty_cycle);
}
