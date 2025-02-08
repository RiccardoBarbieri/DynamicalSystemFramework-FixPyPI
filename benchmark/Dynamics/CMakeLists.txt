cmake_minimum_required(VERSION 3.16.0)
project(BenchDynamics)

# Set the C++ standard
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Enable warnings and optimizations
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -O3")

# Find TBB
find_package(TBB REQUIRED CONFIG)

# Set output folder
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/../../)

# Include directories
include_directories(../../src/dsm/headers)
include_directories(../../src/dsm/utility/)

# Find source files
file(GLOB SOURCES "../../src/dsm/sources/*.cpp" "../../src/dsm/utility/*.cpp")

# Define the executable
add_executable(bench_dynamics.out BenchDynamics.cpp ${SOURCES})

# Link with TBB
target_link_libraries(bench_dynamics.out PRIVATE TBB::tbb)

