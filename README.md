# Asin for Hermes Agent

Gives [Hermes Agent](https://hermes-agent.nousresearch.com) tools to search Amazon and read a product's price history and offers, through the Asin API.

## Install

```sh
hermes plugins install asin
```

Hermes asks for `ASIN_API_KEY` during the install. Create a key in the [Asin dashboard](https://www.asin.dev/app).

## Tools

| Tool | What it does |
|---|---|
| `asin_search_amazon` | Search an Amazon store and return products with their ASIN, title, price, currency, rating and review count. |
| `asin_price_history` | Get the price history Asin has recorded for an Amazon product: lowest, highest and average price, and the dated price points. Empty when Asin has no history for the product yet. |
| `asin_get_offers` | Get the offers Asin has already collected for an Amazon product: Amazon's own price, the lowest new and used prices, and each seller's offer. Empty when Asin has not checked the product yet. |

The tools are hidden from the model until the API key is set.

## What it does on your machine

- **Network:** calls `https://www.asin.dev` only, with your `ASIN_API_KEY`. Calls can use credits on your Asin account ([pricing](https://www.asin.dev/pricing)).
- **Credentials:** reads the key only through Hermes's secret scope. It stores nothing.
- **Nothing else:** no files written, no processes started, no telemetry, no self-update. Standard library only, no dependencies.

## Development

```sh
python -m pytest
```

The tests mock the network and run without Hermes installed.

## Contact

- Source: https://github.com/asindotdev/hermes-plugin-asin
- Asin: https://www.asin.dev
- Issues: https://github.com/asindotdev/hermes-plugin-asin/issues

## License

MIT
