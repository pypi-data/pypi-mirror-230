cmake_minimum_required(VERSION 3.8)

project(@api@ DESCRIPTION  "Generator XPACK-based C++ client of OpenAPI")

include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/config.cmake)
include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/install_conan_deps.cmake)


include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/core/include)
include_directories($<$<CONFIG:Debug>:${CONAN_INCLUDE_DIRS_DEBUG}>$<$<CONFIG:Release>:${CONAN_INCLUDE_DIRS_RELEASE}>)

add_subdirectory(core)

aux_source_directory(${CMAKE_CURRENT_SOURCE_DIR}/include/@PROJECT@  PUB_HEADERS)
aux_source_directory(${CMAKE_CURRENT_SOURCE_DIR}/src @API@_SOURCES)

if(BUILD_SHARED)
add_definitions(-D@API@_DLL -D@API@_EXPORTS)
add_library(@api@ SHARED ${PUB_HEADERS} ${@API@_SOURCES})
target_link_libraries(@api@ @api@_core CONAN_PKG::Poco)
else()
add_library(@api@ STATIC ${PUB_HEADERS} ${@API@_SOURCES})
endif()

add_dependencies(@api@ @api@_core)
target_link_libraries(@api@ CONAN_PKG::Poco)

@TESTS_SECTION@

install(DIRECTORY  ${CMAKE_CURRENT_SOURCE_DIR}/core/include DESTINATION include)
install(DIRECTORY  ${CMAKE_CURRENT_SOURCE_DIR}/include DESTINATION include)

if(BUILD_SHARED)
install(TARGETS @api@_core DESTINATION bin)
install(TARGETS @api@ DESTINATION bin)
else()
install(TARGETS @api@_core DESTINATION lib)
install(TARGETS @api@ DESTINATION lib)
endif()

