import os

from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():



    return LaunchDescription([

        Node(
            package='v4l2_camera',
            executable='v4l2_camera_node',
            output='screen',
            namespace='camera',
            parameters=[{
                'image_size': [1920,1080],
                'time_per_frame': [1, 3],
                'camera_frame_id': 'camera_link_optical'
                }]
    )
    ])
