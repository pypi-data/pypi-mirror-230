#!/usr/bin/env python

"""
ROS message source code generation for Java, integration with ros' message_generation.

Converts ROS .msg files in a package into Java source code implementations.
"""
import os
import sys

import mobile_message_service_generator

if __name__ == "__main__":
    mobile_message_service_generator.main(sys.argv)

