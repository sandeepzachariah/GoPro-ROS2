import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import time
from datetime import datetime

class ImagePublisher(Node):
    def __init__(self):
        super().__init__('image_publisher')
        video_device_path = '/dev/video42' #video device path setup by go_pro_driver interface
        self.publisher_ = self.create_publisher(Image, 'go_pro_image', 10)
        timer_period = 0.0  # seconds
        self.img_count = 0
        print("Going for a 5 sec sleep")
        time.sleep(5)
        print("Done with the sleep")
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.cap = cv2.VideoCapture(video_device_path)
        self.br = CvBridge()
        self.file = open("/home/uav/catkin_ws/src/camera/data/timestamps.txt","w")

    def timer_callback(self):
        ret, frame = self.cap.read()
        if ret == True:
            captured_time = datetime.now().strftime("%H:%M:%S.%f")[:-5]
            self.file.write(captured_time + "\n")
            self.img_count += 1
            write_pth = "/home/uav/catkin_ws/src/camera/data/images/frame_" + str(self.img_count) + ".jpg"
            cv2.imwrite(write_pth, frame)
            self.publisher_.publish(self.br.cv2_to_imgmsg(frame))
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
