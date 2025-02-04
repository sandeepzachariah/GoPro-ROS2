# GoPro-ROS2
ROS2 Python package for integrating the GoPro camera with the ROS2 framework.

## Install
Clone and build this repository inside the `src` folder of a ROS2 workspace.
```bash
cd <ros2_ws>/src/
git clone https://github.com/sandeepzachariah/GoPro-ROS2.git
cd ..
colcon build
source install/setup.sh
```

## Usage
1. Turn on the GoPro camera and connect it to the PC via USB.
2. Run the script to set the GoPro camera to webcam mode (courtesy of [gopro_as_webcam_on_linux](https://github.com/jschmid1/gopro_as_webcam_on_linux)).
```bash
sh camera/scripts/webcam_service.sh
```
Press 'Enter' when prompted.
3. Open a new terminal and launch the go_pro_launch file.
```bash
ros2 launch camera go_pro_launch.py
```

## Configuration
Calibrate the camera and place the calibrated camera parameter files in the `config/camera_params.yaml` file. ROS2 provides a camera calibration package. 
