#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <sensor_msgs/msg/camera_info.hpp>
//#include <image_transport/image_transport.hpp>
#include <cv_bridge/cv_bridge.h>
#include <opencv2/opencv.hpp>
#include <ament_index_cpp/get_package_prefix.hpp>
#include <iostream>
#include <fstream>
#include <yaml-cpp/yaml.h>

class ImagePublisher : public rclcpp::Node
{
public:
    ImagePublisher()
    : Node("image_publisher")
    {
        // Load the camera parameters from YAML
        std::string package_prefix = ament_index_cpp::get_package_prefix("camera_cpp");
        std::string camera_info_file = package_prefix + "/share/camera_cpp/config/camera_params.yaml";

        this->declare_parameter<std::string>("camera_info_file", camera_info_file);
        this->get_parameter("camera_info_file", camera_info_file);

        // Parse YAML
        YAML::Node config = YAML::LoadFile(camera_info_file);

        // Fill CameraInfo message
        camera_info_msg_ = std::make_shared<sensor_msgs::msg::CameraInfo>();
        camera_info_msg_->width = config["image_width"].as<int>();
        camera_info_msg_->height = config["image_height"].as<int>();
        camera_info_msg_->distortion_model = config["distortion_model"].as<std::string>();
        // Fill K (camera_matrix)
        for (size_t i = 0; i < config["camera_matrix"]["data"].size(); ++i)
        {
            camera_info_msg_->k[i] = config["camera_matrix"]["data"][i].as<double>();
        }

        // Fill D (distortion_coefficients) — this one *is* a vector, so push_back is fine
        for (const auto& val : config["distortion_coefficients"]["data"])
        {
            camera_info_msg_->d.push_back(val.as<double>());
        }

        // Fill P (projection_matrix)
        for (size_t i = 0; i < config["projection_matrix"]["data"].size(); ++i)
        {
            camera_info_msg_->p[i] = config["projection_matrix"]["data"][i].as<double>();
        }

        // Publishers
        cam_info_pub_ = this->create_publisher<sensor_msgs::msg::CameraInfo>("/go_pro/camera_info", 10);
        img_pub_ = this->create_publisher<sensor_msgs::msg::Image>("go_pro/image", 10);

        // OpenCV video capture
        cap_.open("/dev/video42");

        if (!cap_.isOpened()) {
            RCLCPP_ERROR(this->get_logger(), "Could not open video device");
            return;
        }

        this->declare_parameter<double>("fps", 5.0);
        double fps = this->get_parameter("fps").as_double();
        if (fps <= 0.0) {
            RCLCPP_WARN(this->get_logger(), "FPS must be positive. Defaulting to 30.");
            fps = 10.0;
        }   

        RCLCPP_INFO(this->get_logger(), "Using FPS: %.2f", fps);
        auto timer_period = std::chrono::duration<double>(1.0 / fps);
        timer_ = this->create_wall_timer(
            timer_period,
            std::bind(&ImagePublisher::timer_callback, this)
        );
    }

private:
    void timer_callback()
    {
        cv::Mat frame;
        if (cap_.read(frame)) {
            rclcpp::Time now = this->now();
            std::string frame_id = "go_pro_camera";

            std_msgs::msg::Header header;
            header.stamp = now;
            header.frame_id = frame_id;

            auto msg = cv_bridge::CvImage(header, "bgr8", frame).toImageMsg();

            camera_info_msg_->header.stamp = now;
            camera_info_msg_->header.frame_id = frame_id;

            img_pub_->publish(*msg);
            cam_info_pub_->publish(*camera_info_msg_);
        } else {
            RCLCPP_WARN(this->get_logger(), "Failed to read frame from camera");
            cap_.release();
        }
    }

    rclcpp::Publisher<sensor_msgs::msg::Image>::SharedPtr img_pub_;
    rclcpp::Publisher<sensor_msgs::msg::CameraInfo>::SharedPtr cam_info_pub_;
    std::shared_ptr<sensor_msgs::msg::CameraInfo> camera_info_msg_;
    rclcpp::TimerBase::SharedPtr timer_;
    cv::VideoCapture cap_;
};

int main(int argc, char* argv[])
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<ImagePublisher>());
    rclcpp::shutdown();
    return 0;
}
