# asuraswrath - ReXGlue Recompiled Project
#
# SDK boilerplate lives in generated/rexglue.cmake.

cmake_minimum_required(VERSION 3.25)
project(asuraswrath LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(generated/rexglue.cmake)

# Sources
set(ASURASWRATH_SOURCES
    src/main.cpp
)

if(WIN32)
    add_executable(asuraswrath WIN32 ${ASURASWRATH_SOURCES})
else()
    add_executable(asuraswrath ${ASURASWRATH_SOURCES})
endif()

rexglue_setup_target(asuraswrath GPU_PLUGINS xenos)

# the linker map names the frames of falha.log (scripts/pilha.py)
target_link_options(asuraswrath PRIVATE "LINKER:/MAP:${CMAKE_CURRENT_BINARY_DIR}/asuraswrath.map")
