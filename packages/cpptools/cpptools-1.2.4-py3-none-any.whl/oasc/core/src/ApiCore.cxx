#include "@PROJECT@/core/ApiCore.h"
#include <Poco/Net/HTTPSClientSession.h>
#include <Poco/Net/HTTPRequest.h>
#include <Poco/Net/HTTPResponse.h>
#include <Poco/Net/NetException.h>
#include <Poco/URI.h>
#include <Poco/Logger.h>

using Poco::Net::HTTPRequest;
using Poco::Net::HTTPResponse;
using Poco::Net::HTTPClientSession;
using Poco::Net::HTTPSClientSession;
using Poco::Net::Context;

namespace @NSP@
{
ApiCore::ApiCore()
    : tr_(nullptr)
    , cancel_(true)
    , logger_(Poco::Logger::get("@NSP@"))
{
    sequencer_ = new Sequencer(requests_);
}

ApiCore::~ApiCore()
{
    stop();
}

void ApiCore::callMethod(const Request & method, ResponseHandler handler)
{
    const auto seq = sequencer_->Claim();
    (*sequencer_)[seq].request_ = method;
    (*sequencer_)[seq].handler_ = handler;
    sequencer_->Publish(seq);
}

void ApiCore::setupTimeout(int ms)
{
    timeout_ = ms;
}

int ApiCore::getTimeout() const
{
    return timeout_;
}

void ApiCore::addHeader(const std::string & key, const Poco::DynamicAny & value)
{
    headers_.insert(key, value);
}

void ApiCore::removeHeader(const std::string & key)
{
    headers_.erase(key);
}

void ApiCore::clearHeaders()
{
    headers_.clear();
}

void ApiCore::setupHeaders(const Poco::DynamicStruct & headers)
{
    headers_ = headers;
}

void ApiCore::start()
{
    if (tr_ || !cancel_) return;

    cancel_ = false;
    tr_ = new std::thread([this]()
    {
#ifdef _WIN32
        auto handle = ::GetCurrentThread();
#if BUILD_VX50
        ::SetThreadDescription(handle, wxString::FromUTF8(m_desc).c_str());
#endif
        ::SetThreadPriority(handle, THREAD_PRIORITY_HIGHEST);
#endif

        int64_t seqWant(disruptor::kFirstSequenceValue);
        int64_t seqGeted, i;
        std::vector<disruptor::Sequence*> dependents;
        disruptor::SequenceBarrier<waitStrategy_>*  barrier;

        disruptor::Sequence handled(disruptor::kInitialCursorValue);
        dependents.push_back(&handled);
        sequencer_->set_gating_sequences(dependents);
        dependents.clear();
        barrier = sequencer_->NewBarrier(dependents);

        while (!cancel_)
        {
            seqGeted = barrier->WaitFor(seqWant);
            for (i = seqWant; i <= seqGeted; i++)
            {
                const auto &r = (*sequencer_)[i];
                if (r.request_.cancel_)
                {
                    break;
                }
                doCallMethod(r.request_, r.handler_);
                handled.set_sequence(i);
            }

            seqWant = seqGeted + 1;
        }

        delete barrier;
        barrier = nullptr;
    });
}

void ApiCore::stop()
{
    if (!cancel_ && tr_)
    {
        const auto seq = sequencer_->Claim();
        (*sequencer_)[seq].request_.cancel_ = true;
        (*sequencer_)[seq].handler_ = nullptr;
        sequencer_->Publish(seq);

        cancel_ = true;
        tr_->join();
        delete tr_;
        tr_ = nullptr;
    }
}

void ApiCore::setProxyConfig(const ProxyConfig & cfg)
{
    proxyCfg_ = cfg;
}

const ApiCore::ProxyConfig & ApiCore::getProxyConfig() const
{
    return proxyCfg_;
}

void ApiCore::doCallMethod(const Request &request, ResponseHandler handler)
{
    try
    {
        Poco::URI uri(request.url_);
        const auto scheme = Poco::toLower(uri.getScheme());
        if ("http" != scheme && "https" != scheme)
        {
            poco_warning_f1(logger_, "invalid url %s", request.url_);
            return;
        }

        std::unique_ptr<Poco::Net::HTTPClientSession> sess;
        if ("https" == scheme)
        {
            const Context::Ptr context(new Context(Context::CLIENT_USE, "", "", "", Context::VERIFY_NONE));
            sess.reset(new HTTPSClientSession(uri.getHost(), uri.getPort(), context));
        }
        else
        {
            sess.reset(new HTTPClientSession(uri.getHost(), uri.getPort()));
        }

        sess->setKeepAlive(false);
        if (timeout_) sess->setTimeout(Poco::Timespan(timeout_ * 1000));
        if (!proxyCfg_.host.empty())
        {
            sess->setProxyConfig(proxyCfg_);
        }

        HTTPRequest req(request.type_, uri.getPathAndQuery(), "HTTP/1.1");
        for (auto &item : headers_)
        {
            req.add(item.first, item.second);
        }

        req.setContentType(request.mimeType_);
        if (!request.body_.empty())
        {
            req.setContentLength(request.body_.size());
        }

        auto &ss = sess->sendRequest(req);
        if (!request.body_.empty())
        {
            ss << request.body_;
        }

        HTTPResponse rsp;
        auto &rs = sess->receiveResponse(rsp);

        std::ostringstream  oss;
        oss << rs.rdbuf();

        auto status = rsp.getStatus();
        if (handler)    
        {
            handler(status, rsp.getReason(), oss.str());
        }
    }
    catch (Poco::TimeoutException &e)
    {
        if (handler) {
            handler(408, e.displayText());
        }
    }
    catch (Poco::Exception &e)
    {
        if (handler) {
            handler(e.code(), e.displayText());
        }
    }
}
}