import ctypes
import time

# C 라이브러리 불러오기
log_lib = ctypes.CDLL('./log_control.so')

# 함수 호출
log_lib.setup_mock()
log_lib.start_log()
time.sleep(2)
log_lib.stop_log()
