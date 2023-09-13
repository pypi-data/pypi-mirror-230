#pragma once
#include <string>
#include <cstdint>

#if defined(_WIN32) && defined(@API@_DLL)
#if defined(@API@_EXPORTS)
#define @API@ __declspec(dllexport)
#else
#define @API@ __declspec(dllimport)
#endif
#endif


#if !defined(@API@)
#if defined (__GNUC__) && (__GNUC__ >= 4)
#define @API@ __attribute__ ((visibility ("default")))
#else
#define @API@
#endif
#endif

namespace @NSP@
{
    void @API@ setGlobalProxyConfig(const std::string &host, uint16_t port, const std::string &name, const std::string &pwd, const std::string &nonProxyHosts);
    void @API@ getGlobalProxyConfig(std::string &host, uint16_t& port, std::string &name, std::string &pwd, std::string &nonProxyHosts);
}