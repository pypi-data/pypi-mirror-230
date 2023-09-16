  set(GENMOBILE_MESSAGE_ARTIFACTS_BIN_DIR "${mobile_message_service_generator_DIR}/../../../lib/mobile_message_service_generator")

set(GENMOBILE_MESSAGE_ARTIFACTS_BIN ${GENMOBILE_MESSAGE_ARTIFACTS_BIN_DIR}/mobile_message_service_generator_message_artifacts)
set(mobile_message_service_generator_INSTALL_DIR "maven/org/ros/rosmobile_messages")

include(CMakeParseArguments)

# Api for a a catkin metapackage rolls rosmobile messages for
# its dependencies. Accepts a list of package names attached
# to the PACKAGES arg (similar to the genmsg
# 'generate_messages' api.
#
#   generate_rosmobile_messages(
#     PACKAGES
#         std_msgs
#         geometry_msgs
#   )
macro(generate_rosmobile_messages)
  if( ${ARGC} EQUAL 0 )
    return() # Nothing to do (no packages specified)
  else()
    cmake_parse_arguments(ARG "" "" "PACKAGES" ${ARGN})
  endif()
  if(ARG_UNPARSED_ARGUMENTS)
    message(FATAL_ERROR "generate_rosmobile_messages() called with unused arguments: ${ARG_UNPARSED_ARGUMENTS}")
  endif()
  catkin_rosmobile_env_setup()
  set(ROS_GRADLE_VERBOSE $ENV{ROS_GRADLE_VERBOSE})
  if(ROS_GRADLE_VERBOSE)
      set(verbosity "--verbosity")
  else()
      set(verbosity "")
  endif()
  string(REPLACE ";" " " package_list "${ARG_PACKAGES}")

  add_custom_target(${PROJECT_NAME}_generate_artifacts
    ALL
    COMMAND ${CATKIN_ENV} ${PYTHON_EXECUTABLE} ${GENMOBILE_MESSAGE_ARTIFACTS_BIN}
        ${verbosity}
        --avoid-rebuilding
        -o ${CMAKE_CURRENT_BINARY_DIR}
        -p ${ARG_PACKAGES} # this has to be a list argument so it separates each arg (not a single string!)
    DEPENDS
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
    COMMENT "Compiling rosmobile message artifacts for [${package_list}]"
  )
  set(build_dir_to_be_cleaned_list)
  foreach(pkg ${ARG_PACKAGES})
    list(APPEND build_dir_to_be_cleaned_list "${CMAKE_CURRENT_BINARY_DIR}/${pkg}")
  endforeach()
  set_directory_properties(PROPERTY ADDITIONAL_MAKE_CLEAN_FILES "${build_dir_to_be_cleaned_list}")
endmacro()
