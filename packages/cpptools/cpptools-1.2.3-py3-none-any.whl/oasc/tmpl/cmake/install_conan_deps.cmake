if (NOT CONAN_BUILD_POLICY)
    set(CONAN_BUILD_POLICY missing)
endif()

if(CONAN_EXPORTED)
    set(CONAN_EXPORTED 0)
endif()

# this project is sub-project, and parent project use old conan.cmake
set(CONAN_CMAKE ${CMAKE_BINARY_DIR}/conan.cmake)
if(CONAN_SETUP)
    file(DOWNLOAD "https://artifactory.gz.cvte.cn/artifactory/binaries/1602/buildtool/cmake-conan-0.19.0.zip!/cmake-conan-develop/conan.cmake"
    "${CMAKE_CURRENT_SOURCE_DIR}/conan.cmake"
    TLS_VERIFY ON)
    set(CONAN_CMAKE ${CMAKE_CURRENT_SOURCE_DIR}/conan.cmake)
elseif(NOT EXISTS "${CMAKE_BINARY_DIR}/conan.cmake")
    file(DOWNLOAD "https://artifactory.gz.cvte.cn/artifactory/binaries/1602/buildtool/cmake-conan-0.19.0.zip!/cmake-conan-develop/conan.cmake"
    "${CMAKE_BINARY_DIR}/conan.cmake"
    TLS_VERIFY ON)
endif()

include(${CONAN_CMAKE})

conan_cmake_run(CONANFILE conanfile.txt
                BASIC_SETUP  CMAKE_TARGETS
                BUILD ${CONAN_BUILD_POLICY})
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
        file(COPY ${_BINARIES} DESTINATION "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/Debug")
        file(COPY ${_PDBS} DESTINATION "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/Debug")
    endforeach() 

    foreach(_DIR ${CONAN_LIB_DIRS_RELEASE})
        file(GLOB _PDBS "${_DIR}/*.pdb")
        file(COPY ${_PDBS} DESTINATION "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/Debug")
    endforeach()
else()
    foreach(_DIR ${CONAN_LIB_DIRS})
        file(GLOB _BINARIES "${_DIR}/*.so")
        file(COPY ${_BINARIES} DESTINATION "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}")
    endforeach()
endif()