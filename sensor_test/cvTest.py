import cv2
import numpy as np
import subprocess

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
    frame_count = 0
    while True:
        raw_frame = ffmpeg.stdout.read(640 * 480 * 3)
        if not raw_frame:
            print("프레임 수신 실패")
            break
        frame = np.frombuffer(raw_frame, dtype=np.uint8).reshape((480, 640, 3))

        avg_brightness = np.mean(frame)
        frame_count += 1
        print(f"[{frame_count:04d}] 프레임 수신: 크기={frame.shape}, 평균 밝기={avg_brightness:.2f}")

except KeyboardInterrupt:
    print("\n사용자 중단으로 종료합니다.")

finally:
    ffmpeg.terminate()
    cam_proc.terminate()

