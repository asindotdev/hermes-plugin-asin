"""Asin tools for Hermes Agent."""


def register(ctx):
    from . import _client
    from .schemas import TOOLS
    from .tools import handler

    for name, (description, parameters, _path, _mapping, _fixed) in TOOLS.items():
        ctx.register_tool(
            name=name,
            toolset="asin",
            schema={"name": name, "description": description, "parameters": parameters},
            handler=handler(name),
            check_fn=lambda: bool(_client.api_key()),
        )
