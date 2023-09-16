##############################################################################
# Installs
##############################################################################

# Rosrunnable installation of scripts
catkin_install_python(
  PROGRAMS
  mobile_message_service_generator_gradle_project.py
  mobile_message_service_generator_message_artifacts
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
