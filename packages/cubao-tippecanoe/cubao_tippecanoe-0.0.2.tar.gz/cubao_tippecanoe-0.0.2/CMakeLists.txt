cmake_minimum_required(VERSION 3.4...3.18)
project(cubao_tippecanoe)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

if(NOT CMAKE_BUILD_TYPE OR CMAKE_BUILD_TYPE STREQUAL "")
  set(CMAKE_BUILD_TYPE
      "Release"
      CACHE STRING "" FORCE)
  message(STATUS "Set build type to default: ${CMAKE_BUILD_TYPE}")
else()
  message(STATUS "Your build type: ${CMAKE_BUILD_TYPE}")
endif()
if(CMAKE_BUILD_TYPE STREQUAL "Debug")
  set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -O0 -ggdb")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O0 -ggdb")
elseif(CMAKE_BUILD_TYPE STREQUAL "Release")
  set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -O3")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3")
endif()

set(CMAKE_CXX_STANDARD 17)
set(PYBIND11_CPP_STANDARD -std=c++17)
include_directories(BEFORE ${PROJECT_BINARY_DIR} ${PROJECT_SOURCE_DIR})
include_directories(${PYBIND11_INCLUDE_DIR})

set(BUILD_SHARED_LIBS OFF)

include(FetchContent)
set(ZLIB_COMPAT ON)
set(ZLIB_ENABLE_TESTS OFF)
set(ZLIBNG_ENABLE_TESTS OFF)
set(WITH_GZFILEOP ON)
# set(WITH_NEW_STRATEGIES OFF)
set(WITH_GTEST OFF)
add_subdirectory(zlib-ng)

set(MAIN_SRCS decode.cpp enumerate.cpp jsontool.cpp main.cpp overzoom.cpp
              tile-join.cpp)

file(GLOB HEADERS *.hpp *.h jsonpull/*.h)
set(SOURCES
    clip.cpp
    compression.cpp
    csv.cpp
    dirtiles.cpp
    evaluator.cpp
    flatgeobuf.cpp
    geobuf.cpp
    geocsv.cpp
    geojson-loop.cpp
    geojson.cpp
    geometry.cpp
    json_logger.cpp
    jsonpull/jsonpull.c
    mbtiles.cpp
    memfile.cpp
    mvt.cpp
    plugin.cpp
    pmtiles_file.cpp
    pool.cpp
    projection.cpp
    read_json.cpp
    serial.cpp
    sqlite3.c
    text.cpp
    tile.cpp
    unit.cpp
    visvalingam.cpp
    write_json.cpp)

add_library(${PROJECT_NAME} ${SOURCES} ${HEADERS})
target_link_libraries(${PROJECT_NAME} zlib m dl pthread)
install(
  TARGETS ${PROJECT_NAME}
  LIBRARY DESTINATION lib
  ARCHIVE DESTINATION lib)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_LIBRARY_OUTPUT_DIRECTORY})

set(SRCS decode.cpp enumerate.cpp jsontool.cpp main.cpp overzoom.cpp
         tile-join.cpp)
foreach(src ${SRCS})
  string(REGEX REPLACE "(^.*/|.cpp$)" "" exe ${src})
  if(${src} STREQUAL "main.cpp")
    set(exe tippecanoe)
    add_executable(${exe} ${src})
    set_target_properties(${exe} PROPERTIES OUTPUT_NAME tippecanoe)
  else()
    add_executable(${exe} ${src})
  endif()
  target_link_libraries(${exe} ${PROJECT_NAME})
  set_target_properties(${exe} PROPERTIES PREFIX "__cubao_tippecanoe_")
  set_target_properties(${exe} PROPERTIES SUFFIX ".exe")
endforeach(src)

add_subdirectory(pybind11)
pybind11_add_module(_pybind11_tippecanoe pybind11.cpp)

target_compile_definitions(_pybind11_tippecanoe
                           PRIVATE VERSION_INFO=${TIPPECANOE_VERSION_INFO})
target_link_libraries(_pybind11_tippecanoe PRIVATE ${PROJECT_NAME})
