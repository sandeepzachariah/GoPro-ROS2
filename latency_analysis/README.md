# Latency Analysis

This folder measures camera/display latency by showing a millisecond clock on a screen, capturing frames from the camera, OCR-reading the clock in each captured frame, and comparing the OCR time with the timestamp recorded when the frame was received.

## Files

- `display_time.py`: fullscreen clock display used as the visual timestamp source.
- `collect_data.py`: captures images from `/dev/video42` and writes receive timestamps.
- `ocr_timestamps.py`: extracts displayed timestamps from captured images using Tesseract OCR.
- `latency.py`: compares camera receive timestamps with OCR timestamps and prints latency statistics.
- `timestamps.txt`: raw receive timestamps from `collect_data.py`.
- `timestamp_img.txt`: OCR timestamps extracted from images.
- `timestamps_filtered.txt`: filtered copy of `timestamps.txt` aligned with successful OCR frames.
- `images/`: captured frames named `frame_1.jpg`, `frame_2.jpg`, etc.

## Dependencies

Install the Python and system dependencies:

```bash
sudo apt update
sudo apt install tesseract-ocr
pip3 install opencv-python pytesseract numpy
```

If `pytesseract` is already installed but OCR fails with `tesseract is not installed or it's not in your PATH`, install the system package:

```bash
sudo apt install tesseract-ocr
```

## Workflow

From this folder:

```bash
cd ~/catkin_ws/src/camera_cpp/latency_analysis
```

Start the fullscreen clock:

```bash
python3 display_time.py
```

In another terminal, collect camera frames:

```bash
python3 collect_data.py
```

`collect_data.py` waits 5 seconds before starting capture, so you have time to bring up the clock display. It then captures for 10 seconds and exits cleanly.

Run OCR on the captured images:

```bash
python3 ocr_timestamps.py
```

This writes:

- `timestamp_img.txt`: timestamps read from the displayed clock.
- `timestamps_filtered.txt`: a filtered copy of `timestamps.txt` with entries removed for frames where OCR failed or failed the sanity check.

The original `timestamps.txt` is not modified.

Calculate latency:

```bash
python3 latency.py
```

`latency.py` reads `timestamps_filtered.txt` and `timestamp_img.txt`, then prints:

- number of valid frames
- average latency in milliseconds
- standard deviation in milliseconds

## OCR Crop Check

If OCR failures are high, preview the crop region:

```bash
python3 ocr_timestamps.py --preview
```

This writes a preview image to:

```text
/tmp/ocr_crop_preview.jpg
```

Open that image and confirm it contains only the clock text. If the crop is wrong, adjust these values in `ocr_timestamps.py`:

```python
CROP_Y1, CROP_Y2 = 280, 590
CROP_X1, CROP_X2 = 455, 1530
```

## Notes

- Press `Escape` to close the fullscreen clock.
- Press `Ctrl+C` to stop `collect_data.py` early.
- Make sure the camera is publishing on `/dev/video42` before running collection.
- Keep the camera pointed clearly at the fullscreen clock for best OCR results.
