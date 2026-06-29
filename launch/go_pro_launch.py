from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory 
import os

def generate_launch_description():
    latency_offset_ms = LaunchConfiguration('latency_offset_ms')

    return LaunchDescription([
        DeclareLaunchArgument(
            'latency_offset_ms',
            default_value='261.0',
            description='Latency offset in milliseconds to subtract from image timestamps'
        ),
        
        Node(
            package='camera_cpp',
            executable='go_pro',
            name="image_publisher",
            parameters=[{
                'latency_offset_ms': latency_offset_ms
            }]
        )
    ])
