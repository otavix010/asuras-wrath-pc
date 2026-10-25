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

# made on the player's own PC (gerar.ps1): the translated code may use every instruction of that processor
option(PORT_CPU_NATIVO "Compile for this PC's processor (-march=native)" OFF)
if(PORT_CPU_NATIVO)
    target_compile_options(asuraswrath PRIVATE -march=native)
endif()
