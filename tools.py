"""Tool handlers: each one calls the Asin API and returns a JSON string, errors included."""

from __future__ import annotations

import json

from . import _client
from .schemas import TOOLS


def _arguments(name, args):
    _, _, path, mapping, fixed = TOOLS[name]
    params, path_values = dict(fixed), {}
    for arg, value in (args or {}).items():
        if value is None or value == "":
            continue
        if "{" + arg + "}" in path:
            path_values[arg] = str(value).strip()
        elif arg in mapping:
            params[mapping[arg]] = json.dumps(value, separators=(",", ":")) if isinstance(value, (dict, list)) else value
    for arg in TOOLS[name][1].get("required", []):
        if arg not in path_values and mapping.get(arg) not in params:
            raise ValueError(f"{arg} is required")
    return path.format(**path_values), params


def call(name, args):
    try:
        path, params = _arguments(name, args)
        return json.dumps(_client.get(path, params), ensure_ascii=False)
    except (ValueError, KeyError, _client.ApiError) as exc:
        return json.dumps({"error": f"Asin: {exc}"})


def handler(name):
    def run(args, **kwargs):
        return call(name, args)

    run.__name__ = name
    return run
