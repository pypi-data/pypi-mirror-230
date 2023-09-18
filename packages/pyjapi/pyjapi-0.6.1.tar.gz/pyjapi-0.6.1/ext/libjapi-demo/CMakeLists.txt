cmake_minimum_required(VERSION 3.5)

project(libjapi-demo)
set(SOVERSION 1)
set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)

# 'cmake -DCMAKE_BUILD_TYPE=Debug ../' from build folder for debug output #
if(NOT CMAKE_BUILD_TYPE)
	set(CMAKE_BUILD_TYPE "Release")
endif()

add_subdirectory(libjapi)

include_directories(${PROJECT_SOURCE_DIR}/libjapi/include)

## Build with static library ##
add_executable(demo-static
   demo.c 
)
target_compile_options(demo-static PUBLIC "-pthread")

target_link_libraries(demo-static -pthread)
target_link_libraries(demo-static -lm) #lib math
target_link_libraries(demo-static japi-static)

add_custom_target(run-static COMMAND ./demo-static 1234 DEPENDS demo-static)

## Build with shared library ##
add_executable(demo-shared
   demo.c 
)
target_compile_options(demo-shared PUBLIC "-pthread")

target_link_libraries(demo-shared -pthread)
target_link_libraries(demo-shared -lm) #lib math
target_link_libraries(demo-shared japi)

add_custom_target(run-shared COMMAND ./demo-shared 1234 DEPENDS demo-shared)
