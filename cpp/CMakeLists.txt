cmake_minimum_required(VERSION 3.20)
project(netpulse-core LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_executable(netpulse-core src/main.cpp)

target_compile_options(netpulse-core PRIVATE
    -Wall
    -Wextra
    -Wpedantic
    -Werror
)
