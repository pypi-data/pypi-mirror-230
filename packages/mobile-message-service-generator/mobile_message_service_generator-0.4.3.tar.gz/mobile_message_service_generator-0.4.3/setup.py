#!/usr/bin/env python

from setuptools import setup, find_packages

# Read the contents of README.md for long description
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="mobile_message_service_generator",
    version="0.4.3",  # Updated version
    description="ROS Mobile Message Service Generator",
    author="Ronaldson Bellande",
    author_email="ronaldsonbellande@gmail.com",
    long_description=long_description,  # Use the README.md contents as long description
    long_description_content_type="text/markdown",  # Specify the content type as Markdown
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    scripts=['scripts/mobile_message_service_generator_message_artifacts'],
    package_data = {'mobile_message_service_generator': [
           'templates/mobile_message_service_generator_project/*',
           'gradle/*',
        ]},
    include_package_data=True,
    install_requires=[
        'genmsg',  # Add your dependencies here
    ],    
    classifiers=[
        "License :: OSI Approved :: Apache Software License",  # Update the classifier here
        "Programming Language :: Python",
    ],
    keywords=["package", "setuptools"],
    python_requires=">=3.0",
    extras_require={
        "dev": ["pytest", "pytest-cov[all]", "mypy", "black"],
    },
    project_urls={
        "Home": "https://github.com/application-ui-ux/mobile_message_service_generator",
        "Homepage": "https://github.com/application-ui-ux/mobile_message_service_generator",
        "documentation": "https://github.com/application-ui-ux/mobile_message_service_generator",
        "repository": "https://github.com/application-ui-ux/mobile_message_service_generator",
    },
)
