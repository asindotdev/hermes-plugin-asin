"""Unit tests for the Asin plugin. The network is mocked."""

import io
import json
import urllib.error

import hermes_plugin_asin as plugin
import pytest
from hermes_plugin_asin import _client


class FakeContext:
    def __init__(self, settings=None):
        self.settings = settings or {}
        self.providers, self.tools = [], {}

    def get_config(self, key, default=None):
        return self.settings.get(key, default)

    def register_web_search_provider(self, provider):
        self.providers.append(provider)

    def register_tool(self, name, toolset, schema, handler, check_fn=None, **kwargs):
        self.tools[name] = {"toolset": toolset, "schema": schema, "handler": handler, "check_fn": check_fn}


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class Calls(list):
    """Records each request and answers it with the payload given to respond()."""

    def __init__(self, monkeypatch):
        super().__init__()
        self.monkeypatch = monkeypatch

    def respond(self, payload):
        def urlopen(request, timeout):
            self.append({"request": request, "timeout": timeout})
            return FakeResponse(json.dumps(payload).encode())

        self.monkeypatch.setattr(_client.urllib.request, "urlopen", urlopen)

    def fail(self, status, body):
        def urlopen(request, timeout):
            self.append({"request": request, "timeout": timeout})
            raise urllib.error.HTTPError(request.full_url, status, "error", {}, io.BytesIO(json.dumps(body).encode()))

        self.monkeypatch.setattr(_client.urllib.request, "urlopen", urlopen)

    def unreachable(self):
        def urlopen(request, timeout):
            raise urllib.error.URLError("down")

        self.monkeypatch.setattr(_client.urllib.request, "urlopen", urlopen)


@pytest.fixture
def calls(monkeypatch):
    return Calls(monkeypatch)


@pytest.fixture
def api_key(monkeypatch):
    monkeypatch.setattr(_client, "get_secret", lambda name, default=None: "test-key" if name == _client.KEY_ENV else default)


@pytest.fixture
def no_key(monkeypatch):
    monkeypatch.setattr(_client, "get_secret", lambda name, default=None: default)


def query(request):
    return dict(_client.urllib.parse.parse_qsl(_client.urllib.parse.urlsplit(request.full_url).query))


def assert_auth(request):
    assert request.get_header("User-agent").startswith("hermes-plugin-asin/")
    assert request.get_header("Authorization") == "Bearer test-key"


def tools():
    ctx = FakeContext()
    plugin.register(ctx)
    return ctx.tools


def run(name, args):
    return json.loads(tools()[name]["handler"](args, task_id="t1"))


def test_register_declares_every_tool():
    registered = tools()
    assert sorted(registered) == sorted(['asin_search_amazon', 'asin_price_history', 'asin_get_offers'])
    for name, tool in registered.items():
        assert tool["toolset"] == "asin"
        assert tool["schema"]["name"] == name
        assert tool["schema"]["parameters"]["type"] == "object"


def test_tools_hidden_without_key(no_key):
    assert all(tool["check_fn"]() is False for tool in tools().values())


def test_tools_shown_with_key(api_key):
    assert all(tool["check_fn"]() is True for tool in tools().values())


def test_missing_key_returns_an_error(no_key, calls):
    assert "ASIN_API_KEY" in run('asin_search_amazon', {'query': 'kindle'})["error"]
    assert calls == []


def test_missing_required_argument(api_key, calls):
    assert "required" in run('asin_search_amazon', {})["error"]
    assert calls == []


@pytest.mark.parametrize("name,args,url", [('asin_search_amazon', {'query': 'kindle', 'marketplace': 'de'}, 'https://www.asin.dev/api/v1/search?query=kindle&marketplace=de'), ('asin_price_history', {'asin': 'B0CZY1LRT4', 'marketplace': 'de', 'days': 90}, 'https://www.asin.dev/api/v1/history?asin=B0CZY1LRT4&marketplace=de&days=90'), ('asin_get_offers', {'asin': 'B0CZY1LRT4', 'marketplace': 'de'}, 'https://www.asin.dev/api/v1/offers?asin=B0CZY1LRT4&marketplace=de')])
def test_each_tool_calls_its_endpoint(api_key, calls, name, args, url):
    calls.respond({"ok": True})
    assert run(name, args) == {"ok": True}
    request = calls[0]["request"]
    assert request.full_url == url
    assert request.get_method() == "GET"
    assert_auth(request)


def test_api_error_message_is_returned(api_key, calls):
    calls.fail(400, {'error': {'code': 'invalid_option', 'message': 'Unknown marketplace'}})
    assert run('asin_search_amazon', {'query': 'kindle'}) == {"error": "Asin: Unknown marketplace"}


def test_network_error(api_key, calls):
    calls.unreachable()
    assert run('asin_search_amazon', {'query': 'kindle'}) == {"error": "Asin: could not reach the API"}
