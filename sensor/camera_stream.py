# sensor/camera_stream.py

import subprocess
import numpy as np

FRAME_WIDTH = 640
FRAME_HEIGHT = 480

def start_stream():
    ffmpeg_proc = subprocess.Popen(
        [
            'ffmpeg',
            '-f', 'mjpeg',
            '-i', '-',
            '-vf', f'scale={FRAME_WIDTH}:{FRAME_HEIGHT}',  # 명확한 리사이즈
            '-f', 'rawvideo',
            '-pix_fmt', 'bgr24',
            '-'
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,   # DEVNULL → PIPE로 잠시 변경해 디버깅 가능하게
        bufsize=10**8             # 충분히 큰 버퍼
    )

    cam_proc = subprocess.Popen(
        [
            'libcamera-vid',
            '-t', '0',
            '--width', str(FRAME_WIDTH),
            '--height', str(FRAME_HEIGHT),
            '--codec', 'mjpeg',
            '--framerate', '30',
            '--nopreview',
            '-o', '-'
        ],
        stdout=ffmpeg_proc.stdin,
        stderr=subprocess.DEVNULL
    )

    return ffmpeg_proc, cam_proc

def read_frame(ffmpeg_proc):
    expected_size = FRAME_WIDTH * FRAME_HEIGHT * 3
    raw = ffmpeg_proc.stdout.read(expected_size)
    if not raw or len(raw) != expected_size:
        print(f"[DEBUG] 프레임 크기 불일치: {len(raw)} bytes (예상: {expected_size})")
        return None
    try:
        frame = np.frombuffer(raw, dtype=np.uint8).reshape((FRAME_HEIGHT, FRAME_WIDTH, 3))
        return frame
    except Exception as e:
        print(f"[ERROR] 프레임 변환 실패: {e}")
        return None
