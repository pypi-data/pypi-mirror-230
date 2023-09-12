from setuptools import find_packages, setup

with open("app/readme.md", "r") as f:
    long_description = f.read()
setup(
    name="connectsrhft",                     # This is the name of the package
    version="0.0.13",                        # The initial release version
    description="Package to connect to SRHFT's API",
    package_dir = {"" : "app"},
    packages = find_packages(where="app"),
    long_description=long_description,      # Long description read from the the readme file
    long_description_content_type="text/markdown",
    author="SRHFT",                     # Full name of the author
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],                                      # Information to filter the project on PyPi website
    python_requires='>=3.8',                # Minimum version requirement of the package
    install_requires=[
        "websocket-client==1.6.1",
        "requests",

    ]            
)