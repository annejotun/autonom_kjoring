import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from rosgraph_msgs.msg import Clock 
from cv_bridge import CvBridge
import cv2
import os
from ament_index_python.packages import get_package_share_directory
import cv2.aruco as aruco
from std_msgs.msg import Float32
import numpy as np
from .image_methods import ImageMethods
from .pid_controller_node import PidControllerNode
from geometry_msgs.msg import Twist


class PipelineImageNode(Node):
    def __init__(self):
        super().__init__('image_processor') 
        self.create_subscription(Image,'/camera/image_raw',  self.listener_callback,10)
        self.bridge = CvBridge()
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.Ids_list= []


    def send_movement(self,ang_vel):
        move_cmd = Twist()
        move_cmd.linear.x = 0.4
        move_cmd.angular.z =ang_vel
        self.publisher_.publish(move_cmd)
       

    def listener_callback(self, data):
        cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        image_edit =cv_image.copy()
        dimensions = cv_image.shape
       
        maskM = ImageMethods.color_filter(cv_image,[30,114,114],[30,255,238])
        
        maskM = cv2.line(maskM,(0,600),(dimensions[1],600),(0,0,0),10)
        Box_list = ImageMethods.find_boxes(maskM, image_edit, 1, True)
       
        The_box = ImageMethods.find_the_box(Box_list)
        
        Center_X,Center_Y = ImageMethods.find_Center(image_edit,The_box, True)
       
        maskM=cv2.cvtColor(maskM,cv2.COLOR_BAYER_BG2BGR)
        images=[cv_image,image_edit]
        image_show=ImageMethods.stack_images(images,0.4)
        Offsett_x = PidControllerNode.calculate_parameters(Center_X,dimensions)
        angle_vel=PidControllerNode.PID_controller(Offsett_x,(2/1920))
        self.send_movement(angle_vel)
        cv2.imshow("window",image_show)
        cv2.waitKey(1)
        self.Ids_list= ImageMethods.read_AruCo(cv_image,self.Ids_list)



        
def main(args=None):
    rclpy.init(args=args)
    image_processor = PipelineImageNode()
    rclpy.spin(image_processor)
    cv2.destroyAllWindows()
    image_processor.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
    
