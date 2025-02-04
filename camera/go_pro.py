import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge
from ament_index_python.packages import get_package_prefix, get_package_share_directory
import cv2
import os
import yaml

class ImagePublisher(Node):
    def __init__(self):
        super().__init__('image_publisher')

        # Load parameters from YAML file
        # get the path of the this python file
        
        package_prefix = get_package_prefix('camera')
        config_file_pth = package_prefix + "/share/camera/config/camera_params.yaml"
        self.declare_parameters(
            namespace='',
            parameters=[('camera_info_file', config_file_pth)]
        )

        camera_info_file = self.get_parameter('camera_info_file').get_parameter_value().string_value

        # Read the YAML file to load the parameters
        with open(camera_info_file, 'r') as f:
            camera_info_params = yaml.safe_load(f)

         # Initialize publishers
        self.param_publisher_ = self.create_publisher(CameraInfo, '/go_pro/camera_info', 10)
        self.img_publisher_ = self.create_publisher(Image, 'go_pro_image', 10)

        # Create CameraInfo message
        self.camera_info_msg = CameraInfo()

        # Set the parameters in the CameraInfo message
        self.camera_info_msg.width = camera_info_params['image_width']
        self.camera_info_msg.height = camera_info_params['image_height']
        self.camera_info_msg.k = camera_info_params['camera_matrix']['data']
        self.camera_info_msg.d = camera_info_params['distortion_coefficients']['data']
        self.camera_info_msg.distortion_model = camera_info_params['distortion_model']
        self.camera_info_msg.p = camera_info_params['projection_matrix']['data']
        

        # Set the device path (setup by go_pro_driver interface)
        video_device_path = '/dev/video42' 
        timer_period = 0.001  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.cap = cv2.VideoCapture(video_device_path)
        self.br = CvBridge()

    def timer_callback(self):
        """Function to read the image from stream and publish as ROS message
        """
        ret, frame = self.cap.read()
        if ret == True:
            self.img_publisher_.publish(self.br.cv2_to_imgmsg(frame, encoding="bgr8"))
            self.param_publisher_.publish(self.camera_info_msg)
        else:
            self.cap.release()

def main(args=None):
    rclpy.init(args=args)
    image_publisher = ImagePublisher()
    rclpy.spin(image_publisher)
    image_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
