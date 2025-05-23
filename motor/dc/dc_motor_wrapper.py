import ctypes
import os

lib_path = os.path.join(os.path.dirname(__file__), "dc_control.so")
lib = ctypes.CDLL(lib_path)

class DCMotor:
    def __init__(self):
        lib.setup_dc_motor()

    def start(self):
        lib.start_motor()

    def stop(self):
        lib.stop_motor()

    def increase_speed(self):
        lib.increase_speed()

    def decrease_speed(self):
        lib.decrease_speed()
