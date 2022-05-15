# Maphisto
Floor Maps for Robot Localization

## Installation

Required dependencies
```bash
sudo apt-get install nlohmann-json3-dev
sudo apt-get install libgtest-dev
sudo apt install libeigen3-dev
```
OpenCV 4 is also required. To save you some pain, please follow to OpenCV installation instructions in this [link](https://docs.opencv.org/4.x/d7/d9f/tutorial_linux_install.html). You'll need Boost but this should come with Ubuntu. 
To compile the code, run 
```bash
cd nmap
mkdir build
cd build
cmake .. -DBUILD_TESTING=1  
make
```
To make sure everything was built correctly, in the build directory, run the unit tests
```bash
./bin/NMapUnitTests
```
