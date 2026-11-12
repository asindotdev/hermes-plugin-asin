"""Tool handlers: each one calls the Asin API and returns a JSON string, errors included."""

from __future__ import annotations

import json
import urllib.parse

from . import _client
from .schemas import TOOLS


def _arguments(name, args):
    """Split the model's arguments into method, path, query parameters and JSON body.

    A route is "METHOD /path" ("/path" alone is a GET). GET and DELETE send their arguments as query
    parameters; other methods send them as a JSON body, except API names written "query:<name>".
    remove_target_price: true sends target_price as null, which clears it.
    """
    _, schema, route, mapping, fixed = TOOLS[name]
    method, path = route.split(" ", 1) if " " in route else ("GET", route)
    in_query = method in ("GET", "DELETE")
    query, body, path_values = {}, {}, {}
    for key, value in fixed.items():
        (query if in_query else body)[key] = value
    for arg, value in (args or {}).items():
        if arg not in mapping or value is None or value == "":
            continue
        api_name = mapping[arg]
        if api_name == "remove_target_price":
            if value is True:
                body["target_price"] = None
            continue
        if "{" + api_name + "}" in path:
            path_values[api_name] = urllib.parse.quote(str(value).strip(), safe="")
        elif api_name.startswith("query:"):
            query[api_name[len("query:"):]] = value
        elif in_query:
            query[api_name] = json.dumps(value, separators=(",", ":")) if isinstance(value, (dict, list)) else value
        else:
            body[api_name] = value
    for arg in schema.get("required", []):
        api_name = mapping.get(arg, "")
        sent = path_values if "{" + api_name + "}" in path else query if (in_query or api_name.startswith("query:")) else body
        if api_name.removeprefix("query:") not in sent:
            raise ValueError(f"{arg} is required")
    return method, path.format(**path_values), query, (None if in_query else body)


def call(name, args):
    try:
        method, path, query, body = _arguments(name, args)
        return json.dumps(_client.request(method, path, query, body), ensure_ascii=False)
    except (ValueError, KeyError, _client.ApiError) as exc:
        return json.dumps({"error": f"Asin: {exc}"})


def handler(name):
    def run(args, **kwargs):
        return call(name, args)

    run.__name__ = name
    return run
