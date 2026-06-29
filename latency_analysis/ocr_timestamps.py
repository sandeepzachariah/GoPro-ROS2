import cv2
import pytesseract
import numpy as np
import os
import re
import shutil
import sys

IMAGE_DIR      = '/home/uav/catkin_ws/src/camera_cpp/latency_analysis/images'
OUTPUT_FILE    = '/home/uav/catkin_ws/src/camera_cpp/latency_analysis/timestamp_img.txt'
TIMESTAMP_FILE = '/home/uav/catkin_ws/src/camera_cpp/latency_analysis/timestamps.txt'
FILTERED_TIMESTAMP_FILE = '/home/uav/catkin_ws/src/camera_cpp/latency_analysis/timestamps_filtered.txt'

# Crop region for the clock inside the captured frame.
# Adjust these if the camera position or screen layout changes.
# Run with --preview to visually verify the crop on the first image.
CROP_Y1, CROP_Y2 = 280, 590
CROP_X1, CROP_X2 = 455, 1530


def frame_number(filename):
    match = re.search(r'\d+', filename)
    return int(match.group()) if match else None


def check_tesseract():
    if shutil.which('tesseract'):
        return True

    print('ERROR: tesseract command not found.')
    print('Install it with:')
    print('  sudo apt update')
    print('  sudo apt install tesseract-ocr')
    print('Then rerun:')
    print('  python3 ocr_timestamps.py')
    return False


def extract_time(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return None, 'failed to load'

    crop = img[CROP_Y1:CROP_Y2, CROP_X1:CROP_X2]
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)

    # Upscale — tesseract works better on larger text
    up = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    # Isolate bright clock digits
    _, thresh = cv2.threshold(up, 180, 255, cv2.THRESH_BINARY)

    # Remove small noise blobs, keep decimal point (min_size=80)
    nb, output, stats, _ = cv2.connectedComponentsWithStats(thresh, connectivity=8)
    clean = np.zeros_like(thresh)
    for i in range(1, nb):
        if stats[i, cv2.CC_STAT_AREA] >= 80:
            clean[output == i] = 255

    # Tesseract prefers dark text on white background
    inverted = cv2.bitwise_not(clean)
    padded   = cv2.copyMakeBorder(inverted, 40, 40, 40, 40, cv2.BORDER_CONSTANT, value=255)

    raw = pytesseract.image_to_string(
        padded,
        config='--oem 1 --psm 7 -c tessedit_char_whitelist=0123456789:.'
    ).strip()

    # Match HH:MM:SS.mmm  (display_time.py uses a dot before milliseconds)
    match = re.search(r'(\d{1,2}):(\d{2}):(\d{2})\.(\d{3})', raw)
    if not match:
        return None, raw

    h, m, s, ms = match.groups()
    # Convert to seconds for sanity checking, return formatted string
    total_s = int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0
    # Write in HH:MM:SS:mmm format to match timestamps.txt used by latency.py
    formatted = f'{h}:{m}:{s}:{ms}'
    return total_s, formatted


def preview_crop(image_path):
    img = cv2.imread(image_path)
    if img is None:
        print(f'Cannot load {image_path}')
        return
    crop = img[CROP_Y1:CROP_Y2, CROP_X1:CROP_X2]
    preview_path = '/tmp/ocr_crop_preview.jpg'
    cv2.imwrite(preview_path, crop)
    print(f'Crop preview saved to {preview_path}')
    print(f'Crop region: y={CROP_Y1}:{CROP_Y2}, x={CROP_X1}:{CROP_X2}')


def filter_capture_timestamps(valid_filenames):
    if not os.path.exists(TIMESTAMP_FILE):
        print(f'WARNING: {TIMESTAMP_FILE} not found; cannot filter capture timestamps')
        return 0

    with open(TIMESTAMP_FILE, 'r') as f:
        timestamps = f.readlines()

    valid_frames = {frame_number(fname) for fname in valid_filenames}
    valid_frames.discard(None)

    filtered = [
        line for i, line in enumerate(timestamps, start=1)
        if i in valid_frames
    ]

    with open(FILTERED_TIMESTAMP_FILE, 'w') as f:
        f.writelines(filtered)

    removed = len(timestamps) - len(filtered)
    missing = len(valid_frames) - len(filtered)
    if missing > 0:
        print(f'WARNING: {missing} valid OCR frames had no matching line in {TIMESTAMP_FILE}')

    return removed


def main():
    if '--preview' in sys.argv:
        files = sorted(f for f in os.listdir(IMAGE_DIR) if f.endswith('.jpg'))
        if files:
            preview_crop(os.path.join(IMAGE_DIR, files[0]))
        return

    if not check_tesseract():
        sys.exit(1)

    files = sorted(
        (f for f in os.listdir(IMAGE_DIR) if f.endswith('.jpg')),
        key=lambda f: int(re.search(r'\d+', f).group())
    )

    if not files:
        print(f'No images found in {IMAGE_DIR}')
        return

    print(f'Processing {len(files)} images...')

    results   = []   # (filename, total_seconds, formatted_string)
    failures  = []
    suspects  = []

    for fname in files:
        path = os.path.join(IMAGE_DIR, fname)
        total_s, value = extract_time(path)

        if total_s is None:
            failures.append((fname, value))
            print(f'  FAIL  {fname}: raw={value!r}')
        else:
            results.append((fname, total_s, value))

    # Sanity check: timestamps must increase monotonically
    for i in range(1, len(results)):
        diff = results[i][1] - results[i - 1][1]
        if diff < 0 or diff > 2.0:
            suspects.append((results[i][0], diff))

    # Write output — only frames that parsed successfully and passed sanity check
    suspect_names = {s[0] for s in suspects}
    valid_filenames = []
    written = 0
    with open(OUTPUT_FILE, 'w') as f:
        for fname, _, formatted in results:
            if fname in suspect_names:
                print(f'  SKIP  {fname}: failed sanity check')
                continue
            f.write(formatted + '\n')
            valid_filenames.append(fname)
            written += 1

    removed_timestamps = filter_capture_timestamps(valid_filenames)

    print(f'\nResults:')
    print(f'  Total images   : {len(files)}')
    print(f'  Parsed OK      : {len(results)}')
    print(f'  OCR failures   : {len(failures)}')
    print(f'  Sanity failures: {len(suspects)}')
    print(f'  Written to file: {written}')
    print(f'  Removed from filtered timestamps: {removed_timestamps}')
    print(f'  OCR output     : {OUTPUT_FILE}')
    print(f'  Filtered timestamps: {FILTERED_TIMESTAMP_FILE}')

    if failures:
        print(f'\nFailed frames (re-run experiment if >10% fail):')
        for fname, raw in failures[:10]:
            print(f'  {fname}: {raw!r}')
        if len(failures) > 10:
            print(f'  ... and {len(failures) - 10} more')


if __name__ == '__main__':
    main()
