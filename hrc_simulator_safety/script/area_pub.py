# #! /usr/bin/env python3

# import rospy
# from visualization_msgs.msg import Marker
# from geometry_msgs.msg import Pose
# import numpy as np
# GREEN = '\033[92m'
# YELLOW = '\033[93m'
# RED = '\033[91m'
# BOLD = '\033[1m'
# END = '\033[0m'

# PARAM_NOT_DEFINED_ERROR = "Parameter: {} not defined"
# TOPIC_NAME = "Parameter: {} not defined"

# def getMarker(area, id):
    
#     area = np.array(area["corners"])
#     x_min = min(area[:,0])
#     y_min = min(area[:,1])
#     x_max = max(area[:,0])
#     y_max = max(area[:,1])
#     delta_x = np.abs(x_max-x_min)
#     delta_y = np.abs(y_max-y_min)
    
#     area_marker = Marker()
#     area_marker.header.frame_id = "world"
#     area_marker.header.stamp = rospy.Time.now()
#     area_marker.ns = "area_plot"
#     area_marker.id = id
#     area_marker.type = area_marker.CUBE
#     area_marker.action = area_marker.ADD
#     area_marker.pose = Pose()
    
#     center_x = (x_max+x_min)/2
#     center_y = (y_max+y_min)/2
#     z_tot = 1
#     area_marker.pose.position.x = center_x
#     area_marker.pose.position.y = center_y
#     area_marker.pose.position.z = z_tot/2
#     area_marker.pose.orientation.x = 0
#     area_marker.pose.orientation.y = 0
#     area_marker.pose.orientation.z = 0
#     area_marker.pose.orientation.w = 1
#     area_marker.lifetime = rospy.Duration.from_sec(0)
    
#     if id == 0:
#         red = 1.0
#         green = 0
#         blue = 0
#         alfa = 1
#         z_tot = z_tot +0.1
#     elif id == 1:
#         red = 1.0
#         green = 0.65
#         blue = 0 
#         alfa = 0.8
#     else:
#         red = 0
#         green = 1.0
#         blue = 0         
#         alfa = 0.5    
#     area_marker.color.r = red
#     area_marker.color.g = green
#     area_marker.color.b = blue
#     area_marker.color.a = alfa
#     area_marker.scale.x = delta_x
#     area_marker.scale.y = delta_y
#     area_marker.scale.z = z_tot
#     print(area_marker)
#     return area_marker

# def main():

#     rospy.init_node("ssm_area_plot")
    
#     try:
#         areas=rospy.get_param("/ssm/areas")   
#     except KeyError:   
#         rospy.logerr(RED + PARAM_NOT_DEFINED_ERROR.format("ssm/areas") + END)
#         return 0

#     areas=sorted(areas,key=lambda area:area["override"])    
#     message_pub = rospy.Publisher("areas_plot", Marker, queue_size=10)
#     rospy.sleep(2.0)
#     for id,area in enumerate(areas):
#         marker = getMarker(area,id)
#         # while not rospy.is_shutdown():
#         #     print("pub")
#         message_pub.publish(marker)
#         rospy.sleep(0.5)
        
#     print(areas)
#     rospy.spin()

# if __name__ == "__main__":
#     main()
#! /usr/bin/env python3

import rospy
from visualization_msgs.msg import Marker
from geometry_msgs.msg import Pose
import numpy as np
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BOLD = '\033[1m'
END = '\033[0m'

PARAM_NOT_DEFINED_ERROR = "Parameter: {} not defined"
TOPIC_NAME = "Parameter: {} not defined"

def getMarker(area, id, override):

    area = np.array(area["corners"])
    x_min = min(area[:,0])
    y_min = min(area[:,1])
    x_max = max(area[:,0])
    y_max = max(area[:,1])
    delta_x = np.abs(x_max-x_min)
    delta_y = np.abs(y_max-y_min)

    area_marker = Marker()
    area_marker.header.frame_id = "world"
    area_marker.header.stamp = rospy.Time.now()
    area_marker.ns = "area_plot"
    area_marker.id = id
    area_marker.type = area_marker.CUBE
    area_marker.action = area_marker.ADD
    area_marker.pose = Pose()

    center_x = (x_max+x_min)/2
    center_y = (y_max+y_min)/2
    z_tot = 1
    area_marker.pose.position.x = center_x
    area_marker.pose.position.y = center_y
    area_marker.pose.position.z = z_tot/2
    area_marker.pose.orientation.x = 0
    area_marker.pose.orientation.y = 0
    area_marker.pose.orientation.z = 0
    area_marker.pose.orientation.w = 1
    area_marker.lifetime = rospy.Duration.from_sec(0)
    red = min(1,2*1*(1-override/100.0))
    green = min(1,2*1*(override/100.0))
    blue = 0
    alfa = min(1 * (1-override/100.0), 0.5)
    z_tot = z_tot + 0.2*(1-override/100.0)
    area_marker.color.r = red
    area_marker.color.g = green
    area_marker.color.b = blue
    area_marker.color.a = alfa
    area_marker.scale.x = delta_x
    area_marker.scale.y = delta_y
    area_marker.scale.z = z_tot
    print(area_marker)
    return area_marker

def main():

    rospy.init_node("ssm_area_plot")

    try:
        areas=rospy.get_param("/ssm/areas")
    except KeyError:
        rospy.logerr(RED + PARAM_NOT_DEFINED_ERROR.format("ssm/areas") + END)
        return 0

    areas=sorted(areas,key=lambda area:area["override"])
    message_pub = rospy.Publisher("areas_plot", Marker, queue_size=10)
    rospy.sleep(2.0)
    for id,area in enumerate(areas):
        marker = getMarker(area,id, area["override"]) #id
        # while not rospy.is_shutdown():
        #     print("pub")
        message_pub.publish(marker)
        rospy.sleep(0.5)

    print(areas)
    rospy.spin()

if __name__ == "__main__":
    main()