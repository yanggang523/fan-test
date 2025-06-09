# config.py
from enum import Enum
# Step 모터 GPIO 핀
STEP_DIR = 5
STEP_STEP = 6

# 거리 임계값 
DISTANCE_THRESHOLD = 40

# 3개 초음파 센서 GPIO 핀 (BCM 기준)
ULTRASONIC_SENSORS = {
    'left':   {'TRIG': 17, 'ECHO': 27},
    'center': {'TRIG': 22, 'ECHO': 10},
    'right':  {'TRIG': 9,  'ECHO': 11},
}

class Gesture(Enum):
    THUMBS_UP = "THUMBS_UP"
    THUMBS_DOWN = "THUMBS_DOWN"
    PALM = "PALM"
    FIST = "FIST"