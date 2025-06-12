import cv2
import numpy as np
from config import Gesture
from sensor.camera_stream import start_stream, read_frame
import mediapipe as mp

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.7
)
drawing = mp.solutions.drawing_utils

def get_finger_states(hand_landmarks, handedness, threshold=0.02):
    fingers = []
    TIP_IDS = [4, 8, 12, 16, 20]
    PIP_IDS = [2, 6, 10, 14, 18]
    is_right = handedness.classification[0].label == "Right"

    for i in range(5):
        tip = hand_landmarks.landmark[TIP_IDS[i]]
        pip = hand_landmarks.landmark[PIP_IDS[i]]

        if i == 0:  # 엄지
            if is_right:
                fingers.append((tip.x - pip.x) > threshold)
            else:
                fingers.append((pip.x - tip.x) > threshold)
        else:
            fingers.append((pip.y - tip.y) > threshold)
    return fingers

def is_thumb_down(hand_landmarks):
    tip = hand_landmarks.landmark[4]
    mcp = hand_landmarks.landmark[2]
    wrist = hand_landmarks.landmark[0]
    vertical = tip.y > mcp.y and tip.y > wrist.y
    horizontal = abs(tip.x - mcp.x) < 0.15
    return vertical and horizontal

def is_hand_small(hand_landmarks):
    wrist = hand_landmarks.landmark[0]
    tip = hand_landmarks.landmark[8]
    dx = tip.x - wrist.x
    dy = tip.y - wrist.y
    distance = np.sqrt(dx * dx + dy * dy)
    return distance < 0.15

def classify_finger_pattern(fingers, hand_landmarks):
    up_count = fingers.count(True)

    if fingers[0] and up_count <= 2:
        return Gesture.THUMBS_UP
    elif is_thumb_down(hand_landmarks) and up_count <= 1:
        return Gesture.THUMBS_DOWN
    elif up_count <= 1 and is_hand_small(hand_landmarks):
        return Gesture.FIST
    elif up_count >= 4:
        return Gesture.PALM
    else:
        return None

def detect_gesture(ffmpeg_proc, debug=False, threshold=0.02):
    frame = read_frame(ffmpeg_proc)
    if frame is None:
        print("[WARN] 프레임 없음")
        return None

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if not results.multi_hand_landmarks or not results.multi_handedness:
        print("[DEBUG] 손 미검출")
        return None

    gestures_detected = []

    for i, (hand_landmarks, handedness) in enumerate(zip(results.multi_hand_landmarks, results.multi_handedness)):
        label = handedness.classification[0].label
        fingers = get_finger_states(hand_landmarks, handedness, threshold)
        gesture = classify_finger_pattern(fingers, hand_landmarks)

        print(f"[INFO] 손[{i}] 방향: {label}, 손가락 상태: {fingers}")
        if gesture:
            print(f"[INFO] 손[{i}] 인식된 제스처: {gesture.name}")
            gestures_detected.append(gesture)
        else:
            print(f"[INFO] 손[{i}] 제스처 인식 실패")

        if debug:
            drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            cv2.putText(frame, f"{label}: {fingers}", (10, 30 + 30 * i),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    if debug:
        cv2.imshow("Gesture Debug", frame)
        cv2.waitKey(1)

    return gestures_detected[0] if gestures_detected else None
