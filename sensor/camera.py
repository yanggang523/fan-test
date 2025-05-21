import cv2
import mediapipe as mp

# 초기화
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# 카메라 열기
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("카메라를 열 수 없습니다.")
    exit()

def get_finger_states(hand_landmarks):
    """손가락이 펴졌는지 여부 (엄지, 검지, 중지, 약지, 새끼손가락)"""
    fingers = []

    # 손가락 끝(TIP)과 PIP의 상대적 y위치 비교
    TIP_IDS = [4, 8, 12, 16, 20]
    PIP_IDS = [3, 6, 10, 14, 18]

    for tip_id, pip_id in zip(TIP_IDS, PIP_IDS):
        tip = hand_landmarks.landmark[tip_id]
        pip = hand_landmarks.landmark[pip_id]
        if tip.y < pip.y:
            fingers.append(1)  # 핀 상태
        else:
            fingers.append(0)  # 접힌 상태

    return fingers

def classify_hand_sign(hand_landmarks, fingers):
    """손 모양을 해석하여 이모지 반환"""
    thumb_tip = hand_landmarks.landmark[4]
    index_tip = hand_landmarks.landmark[8]

    # 손바닥 펴짐
    if fingers == [1, 1, 1, 1, 1]:
        return "🖐️ 손바닥 인식"

    # 엄지만 핀 상태
    if fingers == [1, 0, 0, 0, 0]:
        if thumb_tip.x < index_tip.x:
            return "👍 엄지 왼쪽 (엄지 척)"
        elif thumb_tip.x > index_tip.x:
            return "👎 엄지 오른쪽 (엄지 아래)"

    # 나머지는 인식 안 함
    return None

with mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:

    while True:
        ret, frame = cap.read()
        if not ret:
            print("프레임을 읽을 수 없습니다.")
            break

        # BGR → RGB 변환
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                fingers = get_finger_states(hand_landmarks)
                gesture = classify_hand_sign(hand_landmarks, fingers)

                if gesture:
                    print(gesture)
                print("손가락 상태:", fingers)
                print("-" * 40)

        # ESC 키로 종료
        if cv2.waitKey(1) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()
