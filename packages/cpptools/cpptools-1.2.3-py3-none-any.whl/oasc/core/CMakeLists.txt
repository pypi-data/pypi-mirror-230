include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)

list(APPEND @API@_CORE_HEADERS
					include/@PROJECT@/core/ApiCore.h
	                include/@PROJECT@/core/Config.h
)
list(APPEND @API@_CORE_SOURCES
					src/ApiCore.cxx
					src/Config.cxx
)

if(BUILD_SHARED)
	add_definitions(-D@API@_DLL -D@API@_EXPORTS)
	add_library(@api@_core SHARED ${@API@_CORE_SOURCES} ${@API@_CORE_HEADERS})
else()
	add_library(@api@_core STATIC ${@API@_CORE_SOURCES} ${@API@_CORE_HEADERS})
endif()
target_link_libraries(@api@_core CONAN_PKG::Poco)