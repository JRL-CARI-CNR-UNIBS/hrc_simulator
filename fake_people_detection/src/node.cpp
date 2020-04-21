#include <ros/ros.h>
#include <tf/transform_listener.h>
#include <geometry_msgs/PoseArray.h>
#include <tf_conversions/tf_eigen.h>
int main(int argc, char **argv)
{
  ros::init(argc, argv, "fake_people_detection");
  ros::NodeHandle nh;

  ros::Publisher pub=nh.advertise<geometry_msgs::PoseArray>("poses",1);
  std::string world="world";
  std::vector<std::string> frames;

  if (!nh.getParam("fake_body_link_name",frames))
  {
    ROS_ERROR("unable to load fake_body_link_name");
    return -1;
  }
  if (!nh.getParam("fake_people_detection_world_frame",world))
  {
    ROS_ERROR("unable to load fake_people_detection_world_frame");
    return -1;
  }
  ros::Rate rate(30.0);

  tf::TransformListener listener;

  geometry_msgs::Pose pose;
  tf::StampedTransform transform;

  while (nh.ok())
  {
    geometry_msgs::PoseArray msg;
    for (const std::string& frame: frames)
    {
      try
      {
        listener.lookupTransform(world, frame,
                                 ros::Time(0), transform);
        tf::poseTFToMsg(transform,pose);
        msg.poses.push_back(pose);
      }
      catch(...)
      {

      }
    }
    msg.header.frame_id=world;
    msg.header.stamp=ros::Time::now();
    pub.publish(msg);
    rate.sleep();
  }
  return 0;
}
