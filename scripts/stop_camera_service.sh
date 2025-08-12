#!/bin/bash

# # Searching for processes using v4l2loopback or ffmpeg
# PROCESS=$(ps aux | grep -E 'v4l2loopback|ffmpeg' | grep -v 'grep')

# # Check if there are any processes found
# if [ -n "$PROCESS" ]; then
#     echo "Found the following processes using v4l2loopback or ffmpeg:"
#     echo "$PROCESS"

#     # Extract the PIDs and kill them
#     PIDS=$(echo "$PROCESS" | awk '{print $2}')
    
#     for PID in $PIDS; do
#         echo "Killing process with PID: $PID"
#         sudo kill -9 $PID
#     done

#     echo "Processes killed. Now unloading v4l2loopback module."
    
#     # Unload v4l2loopback module
#     sudo modprobe -r v4l2loopback
    
#     echo "v4l2loopback module unloaded successfully."

# else
#     echo "No processes found using v4l2loopback or ffmpeg."
# fi


# Find all PIDs using any /dev/video* device
PIDS=$(lsof -t /dev/video* 2>/dev/null)

if [ -n "$PIDS" ]; then
    echo "Processes using /dev/video* found:"
    for PID in $PIDS; do
        ps -p $PID -o pid,cmd
        echo "Killing PID: $PID"
        sudo kill -9 $PID
    done

    echo "All processes killed. Unloading v4l2loopback..."
    sudo modprobe -r v4l2loopback
    echo "v4l2loopback module unloaded."

else
    echo "No processes are using /dev/video*. Nothing to kill."
fi