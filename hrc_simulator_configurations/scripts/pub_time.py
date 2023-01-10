#!/usr/bin/env python3
import rospy
from std_msgs.msg import Time
from rosgraph_msgs.msg import Clock
import time

def main():
    rospy.init_node('simulation_time_publisher', anonymous=True)


    pub = rospy.Publisher('/clock',Clock, queue_size=10)
    # rate = rospy.Rate(2000) # 2 kHz

    # time_now = rospy.Time(0,0)
    # dt = rospy.Duration(secs = 0, nsecs = 1e6)  #1ms
    time_zero = 0.0
    dt = 1e-2

    rospy.loginfo("Start Publishing Simulation Time")
    pub_clock = Clock()
    while not rospy.is_shutdown():
        time_zero += dt

        # time_now = time_now.__add__(dt)
        # pub_clock.clock = time_now
        time_now = rospy.Time(time_zero)
        # print(time_now)
        pub.publish(time_now)

        time.sleep(0.1*dt)

        # print(pub_clock)
        # rate.sleep()

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass

