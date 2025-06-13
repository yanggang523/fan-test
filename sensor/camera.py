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
    관절 각도와 좌표 차이 모두 기준 이상일 때만 '펴짐'으로 간주
    """
    lm_tip = hand_landmarks.landmark[tip_id]
    lm_pip = hand_landmarks.landmark[pip_id]
    lm_mcp = hand_landmarks.landmark[mcp_id]

    ang = angle(lm_mcp, lm_pip, lm_tip)
    coord = (lm_pip.y - lm_tip.y)
    return (ang > angle_thresh) and (coord > coord_thresh)


def is_fist_by_distance(hand_landmarks, tip_ids=[4, 8, 12, 16, 20]):
    """
    손목과 손끝 거리 기반으로 완전 주먹(FIST) 판단
    """
    wrist = hand_landmarks.landmark[0]
    thresh = calc_dynamic_threshold(hand_landmarks) * 1.2
    for tid in tip_ids:
        tip = hand_landmarks.landmark[tid]
        dist = np.hypot(tip.x - wrist.x, tip.y - wrist.y)
        if dist > thresh:
            return False
    return True


def get_finger_states(hand_landmarks, handedness):
    """
    5개 손가락 상태(True=펴짐, False=구부림) 반환
    엄지는 x 좌표 차이 + 각도, 나머지는 angle + 동적 coord_thresh 사용
    """
    dynamic_thresh = calc_dynamic_threshold(hand_landmarks)
    is_right = handedness.classification[0].label == "Right"

    states = []
    # 엄지: TIP=4, PIP=2, MCP 대용으로 PIP(2) 사용
    lm_tip, lm_pip = hand_landmarks.landmark[4], hand_landmarks.landmark[2]
    coord_thumb = (lm_tip.x - lm_pip.x) if is_right else (lm_pip.x - lm_tip.x)
    ang_thumb = angle(
        hand_landmarks.landmark[1],  # MCP
        hand_landmarks.landmark[2],  # PIP
        hand_landmarks.landmark[4]   # TIP
    )
    states.append((coord_thumb > dynamic_thresh) and (ang_thumb > ANGLE_THRESHOLD))

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


def is_thumb_up(hand_landmarks):
    dynamic_thresh = calc_dynamic_threshold(hand_landmarks)
    tip = hand_landmarks.landmark[4]
    mcp = hand_landmarks.landmark[2]
    vertical_ok = tip.y < mcp.y - 0.1 * dynamic_thresh
    horizontal_ok = abs(tip.x - mcp.x) < dynamic_thresh
    return vertical_ok and horizontal_ok


def classify_gesture_from_states(states, hand_landmarks):
    """
    states = [thumb, index, middle, ring, pinky]
    """
    # 주먹(FIST) 검사 우선
    if is_fist_by_distance(hand_landmarks):
        return Gesture.FIST

    # 엄지만 폈을 때
    if states[0] and not any(states[1:]):
        if is_thumb_up(hand_landmarks):
            return Gesture.THUMBS_UP
        if is_thumb_down(hand_landmarks):
            return Gesture.THUMBS_DOWN

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

        # 디버그용 출력
        print(f"[DEBUG] Hand[{i}] {label} states={states}, FistByDist={is_fist_by_distance(lm)}")

        # 제스처 후보 분류
        if all(states):
            candidate = Gesture.PALM
        else:
            candidate = classify_gesture_from_states(states, lm)

        raw_gesture = candidate or raw_gesture

        if debug:
            drawing.draw_landmarks(frame, lm, mp_hands.HAND_CONNECTIONS)
            cv2.putText(frame, f"{label}:{states}",
                        (10, 30 + 30*i),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

    return smooth_gesture(raw_gesture)


if __name__ == "__main__":
    ffmpeg_proc, cam_proc = start_stream()
    try:
        while True:
            g = detect_gesture(ffmpeg_proc, debug=True)
            if g:
                print(f"[STABLE] 확정 제스처: {g.name}")
                # TODO: 여기에서 모터 제어 로직(팬 ON/OFF) 연결
    finally:
        ffmpeg_proc.terminate()
        cam_proc.terminate()
