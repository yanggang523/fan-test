import cv2
import numpy as np
import subprocess
import mediapipe as mp

mp_hands = mp.solutions.hands

def get_finger_states(hand_landmarks):
    fingers = []
    TIP_IDS = [4, 8, 12, 16, 20]
    PIP_IDS = [3, 6, 10, 14, 18]
    for tip_id, pip_id in zip(TIP_IDS, PIP_IDS):
        tip = hand_landmarks.landmark[tip_id]
        pip = hand_landmarks.landmark[pip_id]
        fingers.append(1 if tip.y < pip.y else 0)
    return fingers

def classify_hand_sign(hand_landmarks, fingers):
    thumb_tip = hand_landmarks.landmark[4]
    index_tip = hand_landmarks.landmark[8]
    if fingers == [1, 1, 1, 1, 1]:
        return "🖐️ 손바닥 인식"
    if fingers == [1, 0, 0, 0, 0]:
        if thumb_tip.x < index_tip.x:
            return "👍 엄지 왼쪽 (엄지 척)"
        elif thumb_tip.x > index_tip.x:
            return "👎 엄지 오른쪽 (엄지 아래)"
    return None

# ffmpeg + libcamera 연결
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

with mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as hands:

    try:
        frame_count = 0
        while True:
            raw_frame = ffmpeg.stdout.read(640 * 480 * 3)
            if not raw_frame:
                print("프레임 수신 실패")
                break
            frame = np.frombuffer(raw_frame, dtype=np.uint8).reshape((480, 640, 3))
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            results = hands.process(frame_rgb)

            frame_count += 1
            print(f"[{frame_count:04d}]", end=' ')
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    fingers = get_finger_states(hand_landmarks)
                    gesture = classify_hand_sign(hand_landmarks, fingers)
                    print("손가락 상태:", fingers, "| 제스처:", gesture if gesture else "없음")
            else:
                print("손 없음")

    except KeyboardInterrupt:
        print("\n사용자 중단으로 종료합니다.")
    finally:
        ffmpeg.terminate()
        cam_proc.terminate()
