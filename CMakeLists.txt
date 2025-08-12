cmake_minimum_required(VERSION 3.8)
project(camera_cpp)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(OpenCV REQUIRED)
find_package(cv_bridge REQUIRED)
find_package(ament_index_cpp REQUIRED)
find_package(yaml-cpp REQUIRED)


include_directories(
  ${OpenCV_INCLUDE_DIRS}
)



add_executable(go_pro src/go_pro.cpp)

target_link_libraries(go_pro
  ${rclcpp_LIBRARIES}
  ${OpenCV_LIBRARIES}
  ${cv_bridge_LIBRARIES}
  yaml-cpp  # <-- Make sure this line is added
)

ament_target_dependencies(go_pro
  rclcpp
  sensor_msgs
  cv_bridge
  OpenCV
  yaml-cpp
  ament_index_cpp
)

install(DIRECTORY
  launch 
  DESTINATION share/${PROJECT_NAME}
)

install(
  DIRECTORY config/
  DESTINATION share/${PROJECT_NAME}/config
)

install(TARGETS
  go_pro
  DESTINATION lib/${PROJECT_NAME}
)

# uncomment the following section in order to fill in
# further dependencies manually.
# find_package(<dependency> REQUIRED)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
