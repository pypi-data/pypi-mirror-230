##############################################################################
# CMake
##############################################################################

cmake_minimum_required(VERSION 3.0.2)
project(mobile_message_service_generator)

##############################################################################
# Find Package
##############################################################################

find_package(catkin REQUIRED COMPONENTS genmsg mobile_catkin_modules_build_development_tools)

##############################################################################
# Catkin
##############################################################################

catkin_package(
  CATKIN_DEPENDS genmsg mobile_catkin_modules_build_development_tools
  CFG_EXTRAS
  mobile_message_service_generator-extras.cmake
  mobile_message_service_generator-catkin-api.cmake
)

catkin_python_setup()

##############################################################################
# Installs
##############################################################################

add_subdirectory(scripts)

file(WRITE ${CATKIN_DEVEL_PREFIX}/${GENMSG_LANGS_DESTINATION}/mobile_message_service_generator "Java")
install(
  FILES ${CATKIN_DEVEL_PREFIX}/${GENMSG_LANGS_DESTINATION}/mobile_message_service_generator
  DESTINATION ${GENMSG_LANGS_DESTINATION}
)

##############################################################################
# Tests
##############################################################################

#if(CATKIN_ENABLE_TESTING)
#  catkin_add_nosetests(test)
#endif()
