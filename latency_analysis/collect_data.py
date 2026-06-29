import cv2
import time
import os
import signal
import sys
from datetime import datetime

IMAGE_DIR      = '/home/uav/catkin_ws/src/camera_cpp/latency_analysis/images'
TIMESTAMP_FILE = '/home/uav/catkin_ws/src/camera_cpp/latency_analysis/timestamps.txt'
VIDEO_DEVICE   = '/dev/video42'
LOG_INTERVAL   = 30
START_DELAY    = 5
CAPTURE_TIME   = 10

print(f'Starting capture in {START_DELAY}s — start display_time.py now')
time.sleep(START_DELAY)

os.makedirs(IMAGE_DIR, exist_ok=True)

cap = cv2.VideoCapture(VIDEO_DEVICE)
if not cap.isOpened():
    print(f'ERROR: Cannot open {VIDEO_DEVICE}')
    sys.exit(1)

# Minimize internal V4L2 buffer to avoid reading stale frames
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

frame_count    = 0
total_imwrite  = 0.0
session_start  = time.monotonic()
running        = True

def shutdown(*_):
    global running
    running = False

signal.signal(signal.SIGINT, shutdown)

print(f'Capturing from {VIDEO_DEVICE} for {CAPTURE_TIME}s — Ctrl+C to stop')

with open(TIMESTAMP_FILE, 'w') as ts_file:
    while running:
        if time.monotonic() - session_start >= CAPTURE_TIME:
            break

        ret, frame = cap.read()

        if not ret:
            print('cap.read() failed — retrying')
            continue

        # Record time immediately after cap.read() returns — this is T_orin
        captured_time = datetime.now().strftime('%H:%M:%S:%f')[:-3]

        frame_count += 1

        ts_file.write(captured_time + '\n')
        ts_file.flush()

        t1 = time.monotonic()
        cv2.imwrite(os.path.join(IMAGE_DIR, f'frame_{frame_count}.jpg'), frame)
        total_imwrite += time.monotonic() - t1

        if frame_count % LOG_INTERVAL == 0:
            elapsed  = time.monotonic() - session_start
            fps      = frame_count / elapsed
            avg_write = (total_imwrite / frame_count) * 1000
            print(f'Frames: {frame_count} | FPS: {fps:.1f} | avg imwrite: {avg_write:.1f} ms')

cap.release()
elapsed = time.monotonic() - session_start
fps = frame_count / elapsed if elapsed > 0 else 0.0
print(f'Done — {frame_count} frames in {elapsed:.1f}s ({fps:.1f} fps)')
