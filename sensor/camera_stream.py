# sensor/camera_stream.py

import subprocess
import numpy as np
import cv2

FRAME_WIDTH = 640
FRAME_HEIGHT = 480

def start_stream():
    ffmpeg_proc = subprocess.Popen(
        [
            'ffmpeg',
            '-f', 'rawvideo',
            '-pix_fmt', 'yuv420p',
            '-s', f'{FRAME_WIDTH}x{FRAME_HEIGHT}',
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
            '--width', str(FRAME_WIDTH),
            '--height', str(FRAME_HEIGHT),
            '--codec', 'yuv420',
            '--nopreview',
            '-o', '-'
        ],
        stdout=ffmpeg_proc.stdin
    )

    return ffmpeg_proc, cam_proc

def read_frame(ffmpeg_proc):
    raw = ffmpeg_proc.stdout.read(FRAME_WIDTH * FRAME_HEIGHT * 3)
    if not raw:
        print("[DEBUG] FFmpeg로부터 프레임을 받지 못함")
        return None
    try:
        frame = np.frombuffer(raw, dtype=np.uint8).reshape((FRAME_HEIGHT, FRAME_WIDTH, 3))
        return frame
    except Exception as e:
        print(f"[ERROR] 프레임 변환 실패: {e}")
        return None
