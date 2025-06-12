import cv2
import numpy as np
from collections import deque
from config import Gesture
from sensor.camera_stream import start_stream, read_frame
import mediapipe as mp

# Mediapipe Hands 초기화
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.7
)
drawing = mp.solutions.drawing_utils

#— Temporal Smoothing 히스토리(최근 7프레임)
gesture_history = deque(maxlen=7)

#— 파라미터 설정
BASE_RATIO      = 0.15   # 동적 임계값 계산 시 비율
ANGLE_THRESHOLD = 60.0   # 관절 각도 기준(도)

def calc_dynamic_threshold(hand_landmarks, base_ratio=BASE_RATIO):
    """손바닥 너비 기반 동적 임계값 계산"""
    p1 = hand_landmarks.landmark[2]   # 엄지 PIP
    p2 = hand_landmarks.landmark[17]  # 새끼 PIP
    palm_width = np.hypot(p1.x - p2.x, p1.y - p2.y)
    return palm_width * base_ratio

def angle(a, b, c):
    """세 점 a–b–c 의 내각(도) 계산"""
    v1 = np.array([a.x - b.x, a.y - b.y])
    v2 = np.array([c.x - b.x, c.y - b.y])
    cosv = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
    return np.degrees(np.arccos(np.clip(cosv, -1, 1)))

def is_finger_open(hand_landmarks, tip_id, pip_id, mcp_id, angle_thresh=ANGLE_THRESHOLD, coord_thresh=0.0):
    """
    관절 각도 또는 좌표 차이 둘 중 하나라도 기준 이상이면 '펴짐'으로 간주
    coord_thresh: (pip.y - tip.y) 같은 좌표 차이 임계값
    """
    lm_tip = hand_landmarks.landmark[tip_id]
    lm_pip = hand_landmarks.landmark[pip_id]
    lm_mcp = hand_landmarks.landmark[mcp_id]

    ang = angle(lm_mcp, lm_pip, lm_tip)
    coord = (lm_pip.y - lm_tip.y)
    return (ang > angle_thresh) or (coord > coord_thresh)

def get_finger_states(hand_landmarks, handedness):
    """
    5개 손가락 상태(True=펴짐, False=구부림) 반환
    엄지는 x 좌표 차이 + 각도, 나머지는 angle + 동적 coord_thresh 사용
    """
    dynamic_thresh = calc_dynamic_threshold(hand_landmarks)
    is_right = handedness.classification[0].label == "Right"

    states = []
    # 엄지: TIP=4, PIP=2, MCP=2 (PIP 대신 MCP로 angle 계산)
    lm_tip, lm_pip = hand_landmarks.landmark[4], hand_landmarks.landmark[2]
    coord_thresh_thumb = dynamic_thresh
    # 엄지 좌표 차이
    coord_thumb = (lm_tip.x - lm_pip.x) if is_right else (lm_pip.x - lm_tip.x)
    # 엄지 각도: MCP(2)-PIP(2)-TIP(4)
    ang_thumb = angle(hand_landmarks.landmark[1],  # MCP
                    hand_landmarks.landmark[2],  # PIP
                    hand_landmarks.landmark[4])
    states.append((coord_thumb > coord_thresh_thumb) or (ang_thumb > ANGLE_THRESHOLD))

    # 검지~소지
    TIP_IDS = [8, 12, 16, 20]
    PIP_IDS = [6, 10, 14, 18]
    MCP_IDS = [5, 9, 13, 17]
    for tip, pip, mcp in zip(TIP_IDS, PIP_IDS, MCP_IDS):
        states.append(is_finger_open(
            hand_landmarks,
            tip_id=tip,
            pip_id=pip,
            mcp_id=mcp,
            angle_thresh=ANGLE_THRESHOLD,
            coord_thresh=dynamic_thresh
        ))
    return states  # [thumb, index, middle, ring, pinky]

def is_thumb_down(hand_landmarks):
    tip = hand_landmarks.landmark[4]
    mcp = hand_landmarks.landmark[2]
    return (tip.y > mcp.y) and (abs(tip.x - mcp.x) < 0.2)

def classify_gesture_from_states(states, hand_landmarks):
    """
    states = [thumb, index, middle, ring, pinky]
    엄지만 폈을 때:
      - thumbs up: 엄지 TIP.y < min(나머지 4 fingers TIP.y)
      - thumbs down: 엄지 TIP.y > max(나머지 4 fingers TIP.y)
    """
    # 오직 엄지만 폈는지 확인
    if states[0] and not any(states[1:]):
        tips = hand_landmarks.landmark
        thumb_y = tips[4].y
        other_ys = [tips[i].y for i in (8,12,16,20)]
        
        if thumb_y < min(other_ys):
            return Gesture.THUMBS_UP
        if thumb_y > max(other_ys):
            return Gesture.THUMBS_DOWN

    # 모두 접혔을 때만 완전 주먹(FIST)
    if sum(states) == 0:
        return Gesture.FIST

    return None

def smooth_gesture(raw):
    """히스토리 기반 다수결+연속 3회 안정화"""
    gesture_history.append(raw)
    most_common = max(set(gesture_history), key=gesture_history.count)
    if most_common is not None and gesture_history.count(most_common) >= 3:
        return most_common
    return None

def detect_gesture(ffmpeg_proc, debug=False):
    frame = read_frame(ffmpeg_proc)
    if frame is None:
        return None

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)
    if not results.multi_hand_landmarks:
        return None

    raw_gesture = None
    for i, (lm, handedness) in enumerate(zip(results.multi_hand_landmarks, results.multi_handedness)):
        label = handedness.classification[0].label
        states = get_finger_states(lm, handedness)

        # 👋 PALM 엄격 인식: 5개 모두 열려야
        if all(states):
            candidate = Gesture.PALM
        else:
            candidate = classify_gesture_from_states(states, lm)

        raw_gesture = candidate or raw_gesture

        # 로그
        print(f"[INFO] 손[{i}] 방향={label}, 상태={states}, 후보제스처={candidate}")

        if debug:
            drawing.draw_landmarks(frame, lm, mp_hands.HAND_CONNECTIONS)
            cv2.putText(frame, f"{label}:{states}",
                        (10, 30 + 30*i),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

    if debug:
        # cv2.imshow("Gesture Debug", frame)
        # cv2.waitKey(1)
        pass

    # Temporal smoothing 적용
    return smooth_gesture(raw_gesture)

if __name__ == "__main__":
    ffmpeg_proc, cam_proc = start_stream()
    try:
        while True:
            g = detect_gesture(ffmpeg_proc, debug=True)
            if g:
                print(f"[STABLE] 확정 제스처: {g.name}")
                # ⇒ 여기에 모터 제어 로직 연결
    finally:
        ffmpeg_proc.terminate()
        cam_proc.terminate()
