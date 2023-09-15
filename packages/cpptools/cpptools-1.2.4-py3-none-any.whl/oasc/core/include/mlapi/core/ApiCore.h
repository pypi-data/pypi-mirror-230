#pragma once
#include <string>
#include <functional>
#include <thread>
#include <array>
#include <atomic>
#include <Poco/DynamicStruct.h>
#include <Poco/Net/HTTPClientSession.h>
#include <disruptor/sequencer.h>
#include <disruptor/wait_strategy.h>
#include <disruptor/claim_strategy.h>
#include "@PROJECT@/core/Config.h"

namespace Poco
{
    class Logger;
}


namespace @NSP@
{
class @API@ ApiCore
{
public:
    typedef std::function<void(int code, const std::string &reason, const std::string& rsp)> ResponseHandler;
    typedef Poco::Net::HTTPClientSession::ProxyConfig ProxyConfig;

    struct Request
    {
        std::string         url_;
        std::string         type_;
        std::string         mimeType_;
        Poco::DynamicStruct addtionHeaders_;
        std::string         body_;
        bool                cancel_ = false;                // just set it to true if you want to cancel the worker thread.
    };

    ApiCore();
    virtual ~ApiCore();

    void callMethod(const Request& method, ResponseHandler handler);

    void setupTimeout(int ms);
    int getTimeout() const;

    void addHeader(const std::string& key, const Poco::DynamicAny &value);
    void removeHeader(const std::string& key);
    void clearHeaders();
    void setupHeaders(const Poco::DynamicStruct& headers);

    void start();
    void stop();

    void setProxyConfig(const ProxyConfig &cfg);
    const ProxyConfig& getProxyConfig() const;

protected:
    virtual void doCallMethod(const Request& method, ResponseHandler handler);

protected:
    struct RequestPair
    {
        Request             request_;
        ResponseHandler     handler_;
    };

    using claimStrategy_ = disruptor::MultiThreadedStrategy<disruptor::kDefaultRingBufferSize>;
    using waitStrategy_ = disruptor::SleepingStrategy<>;

    typedef std::array<RequestPair, disruptor::kDefaultRingBufferSize>                                          RingBuffer;
    typedef disruptor::Sequencer<RequestPair, disruptor::kDefaultRingBufferSize, claimStrategy_, waitStrategy_> Sequencer;

    RingBuffer                          requests_;
    Sequencer                           *sequencer_;

    std::thread*                        tr_;
    std::atomic<bool>                   cancel_;

    Poco::DynamicStruct                 headers_;
    int                                 timeout_;

    Poco::Logger&                       logger_;
    ProxyConfig                         proxyCfg_;
};
}