cmake_minimum_required(VERSION 2.8.3)
project(fake_people_detection)
 add_compile_options(-std=c++11)

find_package(catkin REQUIRED COMPONENTS
  geometry_msgs
  roscpp
  tf
  tf_conversions
  object_loader_msgs
)

catkin_package(
#  INCLUDE_DIRS include
#  LIBRARIES fake_people_detection
  CATKIN_DEPENDS geometry_msgs roscpp tf tf_conversions object_loader_msgs
  DEPENDS
)

include_directories(
# include
  ${catkin_INCLUDE_DIRS}
)

add_executable(node src/node.cpp)
add_dependencies(node ${${PROJECT_NAME}_EXPORTED_TARGETS} ${catkin_EXPORTED_TARGETS})
target_link_libraries(node
  ${catkin_LIBRARIES}
)


 install(TARGETS node
   RUNTIME DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
 )


 install(DIRECTORY include/${PROJECT_NAME}/
   DESTINATION ${CATKIN_PACKAGE_INCLUDE_DESTINATION}
   FILES_MATCHING PATTERN "*.h"
   PATTERN ".svn" EXCLUDE
 )

## Mark other files for installation (e.g. launch and bag files, etc.)
# install(FILES
#   # myfile1
#   # myfile2
#   DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
# )
