import cv2
import numpy as np
import subprocess
import mediapipe as mp

# Mediapipe 초기화
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)

GESTURES = {
    'THUMBS_UP': '1',
    'THUMBS_DOWN': '2',
    'PALM': '3',
    'FIST': '4'
}

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

def detect_gesture():
    ffmpeg = subprocess.Popen(
        [
            'ffmpeg',
            '-f', 'rawvideo',
            '-pix_fmt', 'yuv420p',
            '-s', '640x480',
            '-i', '-',
            '-f', 'rawvideo',
            '-pix_fmt', 'bgr24',
            '-'
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE
    )

    cam_proc = subprocess.Popen(
        [
            'libcamera-vid',
            '-t', '0',
            '--width', '640',
            '--height', '480',
            '--codec', 'yuv420',
            '--nopreview',
            '-o', '-'
        ],
        stdout=ffmpeg.stdin
    )

    try:
        raw_frame = ffmpeg.stdout.read(640 * 480 * 3)
        if not raw_frame:
            return None

        frame = np.frombuffer(raw_frame, dtype=np.uint8).reshape((480, 640, 3))
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            fingers = get_finger_states(hand_landmarks)

            if fingers == [False, True, False, False, False]:
                return GESTURES['THUMBS_UP']
            elif fingers == [False, False, False, False, False]:
                if is_thumb_down(hand_landmarks):
                    return GESTURES['THUMBS_DOWN']
                else:
                    return GESTURES['FIST']
            elif fingers == [True, True, True, True, True]:
                return GESTURES['PALM']

    finally:
        ffmpeg.terminate()
        cam_proc.terminate()

    return None
