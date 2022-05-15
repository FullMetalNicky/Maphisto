cmake_minimum_required(VERSION 3.16.0)
project(nmap)

set(CMAKE_CXX_FLAGS "-std=c++11 -O3 -fopenmp -Wall ${CMAKE_CXX_FLAGS}")
set(CMAKE_CXX_STANDARD 14)

find_package(Eigen3 REQUIRED)
find_package(OpenCV 4.5 REQUIRED)
if(OpenCV_FOUND)
  message(STATUS "Found OpenCV version ${OpenCV_VERSION}")
  message(STATUS "OpenCV directories: ${OpenCV_INCLUDE_DIRS}")
  include_directories(${OpenCV_INCLUDE_DIRS})
else()
  message(FATAL_ERROR "OpenCV not found, please read the README.md")
endif(OpenCV_FOUND)


find_package(Boost COMPONENTS serialization system filesystem)
if(Boost_FOUND)
  message(STATUS "Found Boost version ${Boost_VERSION}")
  message(STATUS "Boost directories: ${Boost_INCLUDE_DIRS}")
  include_directories(${Boost_INCLUDE_DIRS})
else()
  message(FATAL_ERROR "Boost not found, please read the README.md")
endif(Boost_FOUND)

find_package(nlohmann_json 3.2.0 REQUIRED)
if(nlohmann_json_FOUND)
  message(STATUS "Found nlohmann_json")
else()
  message(FATAL_ERROR "nlohmann_json not found, please read the README.md")
endif(nlohmann_json_FOUND)

if(BUILD_TESTING)
  enable_testing()
  find_package(GTest REQUIRED)
  if(GTEST_FOUND)
    message(STATUS "GTest directories: ${GTEST_INCLUDE_DIRS}")
    include_directories(${GTEST_INCLUDE_DIRS})
  else()
    message(FATAL_ERROR "GTEST_FOUND not found, please read the README.md")
  endif(GTEST_FOUND)
endif()

include_directories(${CMAKE_CURRENT_SOURCE_DIR}/src/)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/src/lib/)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include/)

set(RESULTS_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/build)
file(MAKE_DIRECTORY ${RESULTS_OUTPUT_DIRECTORY})
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${RESULTS_OUTPUT_DIRECTORY}/lib)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${RESULTS_OUTPUT_DIRECTORY}/lib)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${RESULTS_OUTPUT_DIRECTORY}/bin)

add_subdirectory("src")

# After all are setup is done, we can go to our src/ directory to build our
# files
if(BUILD_TESTING)
  add_subdirectory("tst")
endif()
