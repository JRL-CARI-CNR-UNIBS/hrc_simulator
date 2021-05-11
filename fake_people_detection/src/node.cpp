#include <ros/ros.h>
#include <tf/transform_listener.h>
#include <geometry_msgs/PoseArray.h>
#include <tf_conversions/tf_eigen.h>
#include <object_loader_msgs/AddObjects.h>
#include <object_loader_msgs/RemoveObjects.h>

int main(int argc, char **argv)
{
  ros::init(argc, argv, "fake_people_detection");
  ros::NodeHandle nh;

  ros::ServiceClient add_obj_srv=nh.serviceClient<object_loader_msgs::AddObjects>("/add_object_to_scene");
  ros::ServiceClient remove_obj_srv=nh.serviceClient<object_loader_msgs::RemoveObjects>("/remove_object_from_scene");
  ros::Publisher pub=nh.advertise<geometry_msgs::PoseArray>("poses",1);
  std::string world="world";
  std::vector<std::string> frames;

  object_loader_msgs::RemoveObjects remove_srv;


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

  object_loader_msgs::AddObjects add_srv;
  object_loader_msgs::Object obj;
  obj.object_type="ball";
  obj.pose.header.frame_id=world;

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
        obj.pose.pose=pose;
        add_srv.request.objects.push_back(obj);
      }
      catch(...)
      {

      }
    }
    msg.header.frame_id=world;
    msg.header.stamp=ros::Time::now();
    pub.publish(msg);
    rate.sleep();

//    if (!remove_obj_srv.call(remove_srv))
//      ROS_ERROR("unable to remove objects");
//    remove_srv.request.obj_ids.clear();
//    add_obj_srv.call(add_srv);
//    remove_srv.request.obj_ids=add_srv.response.ids;
//    add_srv.request.objects.clear();
  }
  return 0;
}
