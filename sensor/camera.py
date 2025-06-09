import cv2
import numpy as np
import subprocess
import mediapipe as mp
from enum import Enum
from config import Gesture
# Mediapipe 초기화
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)


def get_finger_states(hand_landmarks):
    fingers = []
    TIP_IDS = [4, 8, 12, 16, 20]
    PIP_IDS = [3, 6, 10, 14, 18]

    for tip_id, pip_id in zip(TIP_IDS, PIP_IDS):
        tip = hand_landmarks.landmark[tip_id]
        pip = hand_landmarks.landmark[pip_id]
        fingers.append(tip.y < pip.y)
    return fingers

def is_thumb_down(hand_landmarks):
    # 엄지 tip과 MCP의 y값 비교로 아래로 향했는지 판단
    tip = hand_landmarks.landmark[4]  # Thumb tip
    mcp = hand_landmarks.landmark[2]  # Thumb MCP
    return tip.y > mcp.y
def detect_gesture(ffmpeg_proc):
    frame = read_frame(ffmpeg_proc)
    if frame is None:
        return None

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        fingers = get_finger_states(hand_landmarks)

        if fingers == [False, True, False, False, False]:
            print("[INFO] THUMBS_UP")
            return Gesture.THUMBS_UP
        elif fingers == [False, False, False, False, False]:
            if is_thumb_down(hand_landmarks):
                print("[INFO] THUMBS_DOWN")
                return Gesture.THUMBS_DOWN
            else:
                print("[INFO] FIST")
                return Gesture.FIST
        elif fingers == [True, True, True, True, True]:
            print("[INFO] PALM")
            return Gesture.PALM

    return None

