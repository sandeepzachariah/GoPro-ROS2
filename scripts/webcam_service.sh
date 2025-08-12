#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR=$(dirname "$0")

# Run the stop_camera_service.sh script if the camera drive is already running
"$SCRIPT_DIR/stop_camera_service.sh"

# Start the camera as webcam mode
sudo gopro webcam -n -p enp*


# Publish the messages on a video device
ffmpeg -nostdin -threads 1 -i 'udp://@0.0.0.0:8554?overrun_nonfatal=1&fifo_size=50000000' -f:v mpegts -fflags nobuffer -vf format=yuv420p -f v4l2 /dev/video42
