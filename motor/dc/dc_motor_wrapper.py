import os

SPEED_FILE = "/tmp/fan_speed.txt"

class DCMotor:
    def __init__(self):
        self.speed = 0
        self.max_speed = 100
        self.min_speed = 0
        self.step = 10

    def _write_speed(self):
        with open(SPEED_FILE, 'w') as f:
            f.write(str(self.speed))

    def start(self):
        if self.speed == 0:
            self.speed = 30  # 초기 기본값
        self._write_speed()

    def stop(self):
        self.speed = 0
        self._write_speed()

    def increase_speed(self):
        self.speed = min(self.speed + self.step, self.max_speed)
        self._write_speed()

    def decrease_speed(self):
        self.speed = max(self.speed - self.step, self.min_speed)
        self._write_speed()
