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
    assert sorted(registered) == sorted(['asin_search_amazon', 'asin_price_history', 'asin_get_offers', 'asin_read_offers', 'asin_track_product', 'asin_list_tracked', 'asin_tracked_product', 'asin_update_tracking', 'asin_check_now', 'asin_stop_tracking', 'asin_account'])
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


@pytest.mark.parametrize("name,args,url", [('asin_search_amazon', {'query': 'kindle', 'marketplace': 'de'}, 'https://www.asin.dev/api/v1/search?query=kindle&marketplace=de'), ('asin_price_history', {'asin': 'B0CZY1LRT4', 'marketplace': 'de', 'days': 90}, 'https://www.asin.dev/api/v1/history?asin=B0CZY1LRT4&marketplace=de&days=90'), ('asin_get_offers', {'asin': 'B0CZY1LRT4', 'marketplace': 'de'}, 'https://www.asin.dev/api/v1/offers?asin=B0CZY1LRT4&marketplace=de'), ('asin_list_tracked', {'filter': 'drops', 'page': 2}, 'https://www.asin.dev/api/v1/products?filter=drops&page=2'), ('asin_tracked_product', {'product_id': 'p_123', 'days': 30}, 'https://www.asin.dev/api/v1/products/p_123?days=30'), ('asin_account', {}, 'https://www.asin.dev/api/v1/account')])
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


def sent_body(request):
    return json.loads(request.data)


def test_read_offers_posts_a_json_body(api_key, calls):
    calls.respond({"offers": []})
    run("asin_read_offers", {"asin": "B0CZY1LRT4", "marketplace": "fr", "refresh": True})
    request = calls[0]["request"]
    assert request.full_url == "https://www.asin.dev/api/v1/offers"
    assert request.get_method() == "POST"
    assert request.get_header("Content-type") == "application/json"
    assert sent_body(request) == {"asin": "B0CZY1LRT4", "marketplace": "fr", "refresh": True}
    assert_auth(request)


def test_track_product(api_key, calls):
    calls.respond({"product_id": "p_123"})
    assert run("asin_track_product", {"product": "https://amzn.to/abc", "target_price": 199.99, "interval_minutes": 1440, "wait": True}) == {"product_id": "p_123"}
    request = calls[0]["request"]
    assert (request.get_method(), request.full_url) == ("POST", "https://www.asin.dev/api/v1/products")
    assert sent_body(request) == {"product": "https://amzn.to/abc", "target_price": 199.99, "interval_minutes": 1440, "wait": True}


def test_update_tracking_sends_only_what_changes(api_key, calls):
    calls.respond({})
    run("asin_update_tracking", {"product_id": "p_123", "paused": True, "target_price": None})
    request = calls[0]["request"]
    assert (request.get_method(), request.full_url) == ("PATCH", "https://www.asin.dev/api/v1/products/p_123")
    assert sent_body(request) == {"paused": True}


def test_update_tracking_can_remove_the_target_price(api_key, calls):
    calls.respond({})
    run("asin_update_tracking", {"product_id": "p_123", "remove_target_price": True})
    assert sent_body(calls[0]["request"]) == {"target_price": None}


def test_check_now_sends_wait_in_the_query(api_key, calls):
    calls.respond({})
    run("asin_check_now", {"product_id": "p_123", "wait": True})
    request = calls[0]["request"]
    assert (request.get_method(), request.full_url) == ("POST", "https://www.asin.dev/api/v1/products/p_123/check?wait=true")
    assert sent_body(request) == {}


def test_stop_tracking(api_key, calls):
    calls.respond({"deleted": True, "product_id": "p_123"})
    assert run("asin_stop_tracking", {"product_id": "p_123"}) == {"deleted": True, "product_id": "p_123"}
    request = calls[0]["request"]
    assert (request.get_method(), request.full_url, request.data) == ("DELETE", "https://www.asin.dev/api/v1/products/p_123", None)


def test_product_id_is_escaped_in_the_path(api_key, calls):
    calls.respond({})
    run("asin_tracked_product", {"product_id": "../account"})
    assert calls[0]["request"].full_url == "https://www.asin.dev/api/v1/products/..%2Faccount"


@pytest.mark.parametrize("name", ["asin_track_product", "asin_tracked_product", "asin_update_tracking", "asin_check_now", "asin_stop_tracking", "asin_read_offers"])
def test_required_inputs_are_checked_before_any_request(api_key, calls, name):
    assert "is required" in run(name, {})["error"]
    assert calls == []


def test_manifest_lists_every_tool():
    from pathlib import Path

    manifest = (Path(__file__).resolve().parents[1] / "plugin.yaml").read_text()
    listed = {line.strip()[2:] for line in manifest.splitlines() if line.strip().startswith("- asin_")}
    assert listed == set(tools())
