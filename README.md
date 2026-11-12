# Asin for Hermes Agent

Amazon prices for [Hermes Agent](https://hermes-agent.nousresearch.com), through the [Asin](https://www.asin.dev) API.

- **Find a product** on 11 Amazon stores and get its ASIN, price, rating and reviews.
- **Know if a price is good**: the product's price history with its lowest, highest and average price, and who sells it at what price right now.
- **Watch prices for you**: add products to a watchlist, set a target price, and Asin checks them on a schedule and emails you when the price drops or the product is back in stock. Hermes can add, adjust, check and remove them in conversation.

Stores: amazon.com, .co.uk, .de, .fr, .it, .es, .ca, .co.jp, .com.br, .com.mx and .in.

## Contents

- [Install](#install)
- [How it works](#how-it-works)
- [Tools](#tools)
- [Is this a good price?](#is-this-a-good-price)
- [The watchlist](#the-watchlist)
- [Example prompts](#example-prompts)
- [Credits and errors](#credits-and-errors)
- [What it does on your machine](#what-it-does-on-your-machine)

## Install

```sh
hermes plugins install asin
```

Hermes asks for `ASIN_API_KEY` during the install. Create a key in the [Asin dashboard](https://www.asin.dev/app).

Answer yes to `Enable 'asin' now?`, or run `hermes plugins enable asin` later. The tools join the `asin` toolset, which is on by default; turn it on or off in `hermes tools` like any other toolset. They stay hidden from the model until the API key is set.

## How it works

Each tool is one HTTPS call to `https://www.asin.dev/api/v1`, authenticated with your key. Asin reads Amazon product pages and offers, and keeps every price it reads. Because that history is shared, a product someone else already tracks comes with months of prices the day you look at it.

```
Hermes  ──tool call──▶  plugin  ──/api/v1/...──▶  asin.dev  ──scheduled checks──▶  Amazon
        ◀──JSON──────          ◀──JSON──────────            ──email alerts──▶  you
```

Most tools only read what Asin already knows and are free. Reading Amazon live (`asin_read_offers`, `asin_check_now`) and each scheduled check of a tracked product cost 1 credit.

## Tools

| Tool | What it does | Input | Credits |
|---|---|---|---|
| `asin_search_amazon` | Searches a store: up to 60 results (sponsored included) with ASIN, title, price, rating and review count. Up to 30 searches per hour. | `query` | free |
| `asin_price_history` | Every price Asin has read for the product over the period (90 days by default), with the lowest, highest and average. Up to 600 reads per hour. | `asin` | free |
| `asin_get_offers` | The offers Asin last read: Amazon's own price, lowest new and used prices, and each seller's price, cheapest first. | `asin` | free |
| `asin_read_offers` | Reads the offers live from Amazon. A read from the last 3 hours is returned free instead; `refresh` forces a new one. Refunded if Amazon does not answer. | `asin` | 1 |
| `asin_track_product` | Adds a product to the watchlist by ASIN, product link or short link (amzn.to, a.co), with an optional target price and check interval. | `product` | 1 per check |
| `asin_list_tracked` | The watchlist with current prices and trends. Filters: `drops`, `target`, `out_of_stock`, `attention`, `paused`. | none | free |
| `asin_tracked_product` | One tracked product: prices, stock, coupon, seller, best sellers rank, target, last error and full price history. | `product_id` | free |
| `asin_update_tracking` | Changes the target price, drop and restock alerts, check interval, or pauses and resumes checks. | `product_id` | free |
| `asin_check_now` | Checks the price right away, at most once every 5 minutes. | `product_id` | 1 |
| `asin_stop_tracking` | Removes the product and its price history from the watchlist. | `product_id` | free |
| `asin_account` | Plan, credits left, renewal date, tracked products and their monthly credit use, fastest allowed interval. | none | free |

Every tool that takes an ASIN also takes `marketplace` (`com` by default, or `co.uk`, `de`, `fr`, `it`, `es`, `ca`, `co.jp`, `com.br`, `com.mx`, `in`).

## Is this a good price?

Ask Hermes and it combines three free calls:

1. `asin_search_amazon` finds the ASIN if you gave a name or a link.
2. `asin_price_history` shows where today's price sits between the lowest, highest and average of the last months.
3. `asin_get_offers` (or `asin_read_offers` for fresh data) shows whether another seller, or the used offer, is cheaper than Amazon.

When the product has no history yet, `asin_track_product` starts one.

## The watchlist

- **Adding:** `asin_track_product` takes an ASIN, a full Amazon link or a short link; a link sets the store on its own. The first check runs within seconds; `wait: true` returns its result in the same answer.
- **Alerts:** with `target_price`, Asin emails the account owner when the price reaches it. With `alert_on_drop`, it emails on every drop and when the product is back in stock.
- **Interval:** `interval_minutes` is 1440 (daily) by default. Faster checks need a credit pack or a paid plan: every 60 minutes with a pack or Starter, 30 with Pro, 5 with Business.
- **Cost:** each check costs 1 credit, so a product checked daily uses about 30 credits a month. `paused: true` stops the checks and the cost without losing the history.
- **Removing:** `asin_stop_tracking` deletes the product and its history; its description tells the model to ask you first.

## Example prompts

- "Is $279 a good price for the Sony WH-1000XM5 on amazon.com right now?"
- "Show me the price history of B09DFCB66S on amazon.de over the last year."
- "Who sells this product cheapest? https://www.amazon.fr/dp/B0CZY1LRT4"
- "Track this link and tell me when it drops under 150 €: https://amzn.to/…"
- "Which products on my watchlist are cheaper than when I added them?"
- "Check the price of my tracked Kindle now."
- "Pause all my out-of-stock products."
- "How many Asin credits do I have left, and how many does my watchlist use per month?"

## Credits and errors

- Searching, history, known offers, the watchlist and the account are free. Live reads and price checks cost 1 credit each. The cost is in each tool's description, so the model knows it before it calls. Plans and prices: [asin.dev/pricing](https://www.asin.dev/pricing).
- Errors come back to the model as `{"error": "Asin: <message>"}` with the API's own message (invalid key, no credits left, unknown ASIN, rate limit), so it can fix the input instead of stopping. When a scheduled check fails, the reason is in the product's `last_error`.
- Calls time out after 60 seconds.

## What it does on your machine

- **Network:** calls `https://www.asin.dev/api/v1` only, with your `ASIN_API_KEY`. Some calls use credits on your Asin account.
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
