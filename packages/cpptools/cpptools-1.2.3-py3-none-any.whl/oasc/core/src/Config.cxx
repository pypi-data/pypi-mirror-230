#include "@PROJECT@/core/Config.h"
#include <Poco/Net/HTTPClientSession.h>

namespace @NSP@
{
void @API@ setGlobalProxyConfig(const std::string & host, uint16_t port, const std::string & name, const std::string & pwd, const std::string & nonProxyHosts)
{
    Poco::Net::HTTPClientSession::ProxyConfig cfg;
    cfg.host = host;
    cfg.port = port;
    cfg.username = name;
    cfg.password = pwd;
    cfg.nonProxyHosts = nonProxyHosts;

    Poco::Net::HTTPClientSession::setGlobalProxyConfig(cfg);
}

void @API@ getGlobalProxyConfig(std::string & host, uint16_t & port, std::string & name, std::string & pwd, std::string & nonProxyHosts)
{
    const auto &cfg = Poco::Net::HTTPClientSession::getGlobalProxyConfig();

    host = cfg.host;
    port = cfg.port;
    name = cfg.username;
    pwd = cfg.password;
    nonProxyHosts = cfg.nonProxyHosts;
}
}