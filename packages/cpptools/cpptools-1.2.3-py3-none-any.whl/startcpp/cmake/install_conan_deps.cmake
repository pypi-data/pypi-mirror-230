if ("${CMAKE_CURRENT_SOURCE_DIR}" STREQUAL "${CMAKE_SOURCE_DIR}")
if (NOT CONAN_BUILD_POLICY)
    set(CONAN_BUILD_POLICY missing)
endif()

if(CONAN_EXPORTED)
    set(CONAN_EXPORTED 0)
endif()

set(CONAN_SETUP TRUE)

# this project is sub-project, and parent project use old conan.cmake
set(CONAN_CMAKE ${CMAKE_BINARY_DIR}/conan.cmake)
file(DOWNLOAD "https://artifactory.gz.cvte.cn/artifactory/binaries/1602/buildtool/cmake-conan-0.19.1.zip!/conan.cmake"
    "${CMAKE_BINARY_DIR}/conan.cmake"
    TLS_VERIFY ON)

include(${CONAN_CMAKE})

if(ANDROID)
conan_cmake_run(CONANFILE conan/conanfile.android.txt
                BASIC_SETUP  CMAKE_TARGETS
                BUILD ${CONAN_BUILD_POLICY}
                PROFILE ${CMAKE_CURRENT_SOURCE_DIR}/conan/android.profile
                SETTINGS build_type=${CMAKE_BUILD_TYPE})
elseif(WIN32)
conan_cmake_run(CONANFILE conan/conanfile.win.txt
                BASIC_SETUP  CMAKE_TARGETS
                BUILD ${CONAN_BUILD_POLICY})
else()
message(FATAL_ERROR "not support platform")
endif()

include_directories($<$<CONFIG:Debug>:${CONAN_INCLUDE_DIRS_DEBUG}>$<$<CONFIG:Release>:${CONAN_INCLUDE_DIRS_RELEASE}>) 
conan_global_flags()
if(MSVC)
    file(MAKE_DIRECTORY "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/Debug")
    file(MAKE_DIRECTORY "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/Release")
    
    foreach(_DIR ${CONAN_BIN_DIRS_DEBUG})
        file(GLOB _BINARIES "${_DIR}/*.dll")
        file(GLOB _PDBS "${_DIR}/*.pdb")
        file(COPY ${_BINARIES} DESTINATION "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/Debug")
        file(COPY ${_PDBS} DESTINATION "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/Debug")
    endforeach()

    foreach(_DIR ${CONAN_LIB_DIRS_DEBUG})
        file(GLOB _PDBS "${_DIR}/*.pdb")
        file(COPY ${_PDBS} DESTINATION "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/Debug")
    endforeach()


    foreach(_DIR ${CONAN_BIN_DIRS_RELEASE})
        file(GLOB _BINARIES "${_DIR}/*.dll")
        file(GLOB _PDBS "${_DIR}/*.pdb")
        file(COPY ${_BINARIES} DESTINATION "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/Release")
        file(COPY ${_PDBS} DESTINATION "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/Release")
    endforeach() 

    foreach(_DIR ${CONAN_LIB_DIRS_RELEASE})
        file(GLOB _PDBS "${_DIR}/*.pdb")
        file(COPY ${_PDBS} DESTINATION "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/Release")
    endforeach()
else()
    foreach(_DIR ${CONAN_LIB_DIRS})
        file(GLOB _BINARIES "${_DIR}/*.so")
        file(COPY ${_BINARIES} DESTINATION "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}")
    endforeach()
endif()
endif("${CMAKE_CURRENT_SOURCE_DIR}" STREQUAL "${CMAKE_SOURCE_DIR}")