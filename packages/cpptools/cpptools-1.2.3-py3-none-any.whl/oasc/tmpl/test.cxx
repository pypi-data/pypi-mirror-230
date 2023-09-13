#include <string>
#include "gtest/gtest.h"
#include "Poco/Net/HttpServer.h"
#include "Poco/Net/HTTPRequestHandler.h"
#include "Poco/Net/HTTPServerRequest.h"
#include "Poco/Net/HTTPServerResponse.h"
#include "Poco/Net/MediaType.h"
#include "Poco/StreamCopier.h"
#include "Poco/URI.h"
#include "@PROJECT@/@CLASS@.h"
#include "xpack/json.h"

using namespace Poco::Net;
using Poco::StreamCopier;

namespace @NAMESPACE@ {
struct Credentials
{
    std::string  scheme;
    std::string  authInfo;
    inline bool operator == (const Credentials& other) const
    {
        return scheme == other.scheme && authInfo == other.authInfo;
    }
    XPACK(O(scheme, authInfo));
};

struct TestRequest
{
    std::string   path;
    std::string   method;
    std::string   cookies;
    std::string   headers;
    Credentials   credentials;
    std::string   content;

    inline bool operator==(const TestRequest& other) const
    {
        return path == other.path && method == other.method/* && cookies == other.cookies
            && headers == other.headers && credentials == other.credentials*/ && content == other.content;
    }

    XPACK(M(path, method), O(cookies, headers, credentials, content));
};

class PrintHttpRequestHandler : public HTTPRequestHandler
{
public:
    PrintHttpRequestHandler() = default;
    virtual ~PrintHttpRequestHandler() = default;
    // ͨ�� HTTPRequestHandler �̳�
    virtual void handleRequest(HTTPServerRequest & request, HTTPServerResponse & response) override
    {
        TestRequest tr;
        tr.path = request.getURI();
        tr.method = request.getMethod();

        NameValueCollection cookies;
        request.getCookies(cookies);
        for (const auto& cookie : cookies)
        {
            tr.cookies += cookie.first;
            tr.cookies += ":";
            tr.cookies += cookie.second;
            tr.cookies += ";";
        }

        for (const auto&header : request)
        {
            if (header.first == "Connection" || header.first == "Host")
                continue;

            tr.headers += header.first;
            tr.headers += ":";
            tr.headers += header.second;
            tr.headers += ";";
        }

        if (request.hasCredentials())
        {
            request.getCredentials(tr.credentials.scheme, tr.credentials.authInfo);
        }

        StreamCopier::copyToString(request.stream(), tr.content);

        const auto content = xpack::json::encode(tr);
        response.setContentType("application/json");
        response.setContentLength(content.size());
        response.setStatusAndReason(HTTPResponse::HTTP_OK);
        response.send() << content;
    }

};
class PrintHttpRequestHandlerFactory : public HTTPRequestHandlerFactory
{
public:
    PrintHttpRequestHandlerFactory() = default;
    virtual ~PrintHttpRequestHandlerFactory() = default;

    // ͨ�� HTTPRequestHandlerFactory �̳�
    virtual HTTPRequestHandler * createRequestHandler(const HTTPServerRequest & request) override
    {
        return new PrintHttpRequestHandler();
    }

};

class @TEST_CLASS@ : public ::testing::Test
{
protected:
    @TEST_CLASS@()
        :_server(nullptr)
    {
        Poco::UInt16 port = 9999;
        auto params = new Poco::Net::HTTPServerParams();
        params->setMaxQueued(100);
        params->setMaxThreads(16);

        _server = new HTTPServer(new PrintHttpRequestHandlerFactory(), port, params);
        _server->start();

        _core.reset(new ApiCore());
        _core->start();

        _agent.reset(create@CLASS@(_core));
        _agent->setServer("http://127.0.0.1:9999");
    }
    virtual ~@TEST_CLASS@()
    {
        _agent.reset();
        _core.reset();

        if (_server) _server->stopAll();
        delete _server;
    }
    virtual void SetUp() override
    {
    }

    virtual void TearDown() override
    {
    }
	
    std::shared_ptr<ApiCore> _core;
    Poco::Net::HTTPServer* _server;
	std::unique_ptr<@CLASS@> _agent;
};

@TEST_CASES@
}

int main(int argc, char **argv) 
{
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}