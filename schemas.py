"""Tool schemas (what the model reads) and how each tool maps to the API."""

# name: (description, JSON schema of the arguments, "METHOD /path" ("/path" alone is a GET), {argument: API parameter}, fixed parameters)
TOOLS = {
    'asin_search_amazon': (
        "Search an Amazon store to find a product's ASIN: up to 60 results (sponsored included) with ASIN, title, price, currency, rating and review count. Free, up to 30 searches per hour.",
        {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search keywords."
                },
                "marketplace": {
                    "type": "string",
                    "enum": [
                        "com",
                        "co.uk",
                        "de",
                        "fr",
                        "it",
                        "es",
                        "ca",
                        "co.jp",
                        "com.br",
                        "com.mx",
                        "in"
                    ],
                    "description": "Amazon store: com (amazon.com, default), co.uk, de, fr, it, es, ca, co.jp, com.br, com.mx or in."
                }
            },
            "required": [
                "query"
            ]
        },
        '/search',
        {'query': 'query', 'marketplace': 'marketplace'},
        {},
    ),
    'asin_price_history': (
        'Price history of an Amazon product: every price Asin has read for this ASIN on this store, oldest first, with the lowest, highest and average price over the period (90 days by default). Free, up to 600 reads per hour. Empty when nobody tracks the product yet: asin_track_product starts the history.',
        {
            "type": "object",
            "properties": {
                "asin": {
                    "type": "string",
                    "description": "10-character ASIN."
                },
                "marketplace": {
                    "type": "string",
                    "enum": [
                        "com",
                        "co.uk",
                        "de",
                        "fr",
                        "it",
                        "es",
                        "ca",
                        "co.jp",
                        "com.br",
                        "com.mx",
                        "in"
                    ],
                    "description": "Amazon store: com (amazon.com, default), co.uk, de, fr, it, es, ca, co.jp, com.br, com.mx or in."
                },
                "days": {
                    "type": "integer",
                    "description": "History period in days.",
                    "minimum": 1,
                    "maximum": 3650
                }
            },
            "required": [
                "asin"
            ]
        },
        '/history',
        {'asin': 'asin', 'marketplace': 'marketplace', 'days': 'days'},
        {},
    ),
    'asin_get_offers': (
        "Offers Asin has already read for an Amazon product, cheapest first: Amazon's own price, the lowest new and used prices, and each seller's price. Free, never reads Amazon. Empty with fetched_at null when nobody read them yet: asin_read_offers reads them live.",
        {
            "type": "object",
            "properties": {
                "asin": {
                    "type": "string",
                    "description": "10-character ASIN."
                },
                "marketplace": {
                    "type": "string",
                    "enum": [
                        "com",
                        "co.uk",
                        "de",
                        "fr",
                        "it",
                        "es",
                        "ca",
                        "co.jp",
                        "com.br",
                        "com.mx",
                        "in"
                    ],
                    "description": "Amazon store: com (amazon.com, default), co.uk, de, fr, it, es, ca, co.jp, com.br, com.mx or in."
                }
            },
            "required": [
                "asin"
            ]
        },
        '/offers',
        {'asin': 'asin', 'marketplace': 'marketplace'},
        {},
    ),
    'asin_read_offers': (
        "Read the offers of an Amazon product live from Amazon: Amazon's own price, the lowest new and used prices, and each seller's price, cheapest first. Costs 1 credit, refunded if Amazon does not answer; a read from the last 3 hours is returned for free instead (charged: false). Set refresh to force a new read.",
        {
            "type": "object",
            "properties": {
                "asin": {
                    "type": "string",
                    "description": "10-character ASIN."
                },
                "marketplace": {
                    "type": "string",
                    "enum": [
                        "com",
                        "co.uk",
                        "de",
                        "fr",
                        "it",
                        "es",
                        "ca",
                        "co.jp",
                        "com.br",
                        "com.mx",
                        "in"
                    ],
                    "description": "Amazon store: com (amazon.com, default), co.uk, de, fr, it, es, ca, co.jp, com.br, com.mx or in."
                },
                "refresh": {
                    "type": "boolean",
                    "description": "Read Amazon again unless the last read is under 5 minutes old (1 credit)."
                }
            },
            "required": [
                "asin"
            ]
        },
        'POST /offers',
        {'asin': 'asin', 'marketplace': 'marketplace', 'refresh': 'refresh'},
        {},
    ),
    'asin_track_product': (
        'Add an Amazon product to the watchlist (by ASIN, product link or amzn.to / a.co short link) so Asin checks its price on a schedule and emails on drops or when it reaches a target price. Each check costs 1 credit (about 30 credits a month when checked daily). The first check runs within seconds; set wait to get its result in the answer.',
        {
            "type": "object",
            "properties": {
                "product": {
                    "type": "string",
                    "description": "ASIN (B09DFCB66S), Amazon product link or short link."
                },
                "marketplace": {
                    "type": "string",
                    "enum": [
                        "com",
                        "co.uk",
                        "de",
                        "fr",
                        "it",
                        "es",
                        "ca",
                        "co.jp",
                        "com.br",
                        "com.mx",
                        "in"
                    ],
                    "description": "Amazon store when product is an ASIN: com (default), co.uk, de, fr, it, es, ca, co.jp, com.br, com.mx or in. A link sets it on its own."
                },
                "target_price": {
                    "type": "number",
                    "description": "Email the account owner when the price goes at or below this amount."
                },
                "interval_minutes": {
                    "type": "integer",
                    "enum": [
                        5,
                        30,
                        60,
                        360,
                        720,
                        1440
                    ],
                    "description": "Minutes between two price checks: 1440 (daily, default), 720, 360, 60, 30 or 5. Faster than daily needs a credit pack or a paid plan: 60 with a pack or Starter, 30 with Pro, 5 with Business."
                },
                "wait": {
                    "type": "boolean",
                    "description": "Answer once the first check is done (up to 45 seconds)."
                }
            },
            "required": [
                "product"
            ]
        },
        'POST /products',
        {'product': 'product', 'marketplace': 'marketplace', 'target_price': 'target_price', 'interval_minutes': 'interval_minutes', 'wait': 'wait'},
        {},
    ),
    'asin_list_tracked': (
        "List the products on the watchlist, newest first, with each one's current price, stock, target and recent price trend. Filter by ASIN to know whether a product is tracked, or with filter: drops (cheaper than when added), target (at or below the target price), out_of_stock, attention (last check failed), paused. Free.",
        {
            "type": "object",
            "properties": {
                "asin": {
                    "type": "string",
                    "description": "Only this ASIN."
                },
                "marketplace": {
                    "type": "string",
                    "enum": [
                        "com",
                        "co.uk",
                        "de",
                        "fr",
                        "it",
                        "es",
                        "ca",
                        "co.jp",
                        "com.br",
                        "com.mx",
                        "in"
                    ],
                    "description": "Only this Amazon store."
                },
                "filter": {
                    "type": "string",
                    "enum": [
                        "all",
                        "drops",
                        "target",
                        "out_of_stock",
                        "attention",
                        "paused"
                    ],
                    "description": "Which products: all (default), drops, target, out_of_stock, attention or paused."
                },
                "page": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Page number. Default: 1."
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Products per page. Default: 20."
                }
            },
            "required": []
        },
        '/products',
        {'asin': 'asin', 'marketplace': 'marketplace', 'filter': 'filter', 'page': 'page', 'limit': 'limit'},
        {},
    ),
    'asin_tracked_product': (
        'Get one tracked product: title, brand, current, first, lowest and highest price, stock, coupon, seller, best sellers rank, target price, check interval, last error, and every price read over the period (90 days by default), including reads made before it was added. Free.',
        {
            "type": "object",
            "properties": {
                "product_id": {
                    "type": "string",
                    "description": "product_id of a tracked product, from asin_track_product or asin_list_tracked."
                },
                "days": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "History period in days. Default: 90."
                }
            },
            "required": [
                "product_id"
            ]
        },
        '/products/{id}',
        {'product_id': 'id', 'days': 'days'},
        {},
    ),
    'asin_update_tracking': (
        'Change how a tracked product is watched: target price (or remove it), email on price drops and restocks, check interval, or pause and resume checks (a paused product uses no credits). Send only what changes. Free.',
        {
            "type": "object",
            "properties": {
                "product_id": {
                    "type": "string",
                    "description": "product_id of a tracked product, from asin_track_product or asin_list_tracked."
                },
                "target_price": {
                    "type": "number",
                    "description": "Email the account owner when the price goes at or below this amount."
                },
                "alert_on_drop": {
                    "type": "boolean",
                    "description": "Email when the price drops or the product is back in stock."
                },
                "interval_minutes": {
                    "type": "integer",
                    "enum": [
                        5,
                        30,
                        60,
                        360,
                        720,
                        1440
                    ],
                    "description": "Minutes between two price checks: 1440 (daily, default), 720, 360, 60, 30 or 5. Faster than daily needs a credit pack or a paid plan: 60 with a pack or Starter, 30 with Pro, 5 with Business."
                },
                "paused": {
                    "type": "boolean",
                    "description": "true stops the checks for now; false resumes them."
                },
                "remove_target_price": {
                    "type": "boolean",
                    "description": "true removes the target price."
                }
            },
            "required": [
                "product_id"
            ]
        },
        'PATCH /products/{id}',
        {'product_id': 'id', 'target_price': 'target_price', 'alert_on_drop': 'alert_on_drop', 'interval_minutes': 'interval_minutes', 'paused': 'paused', 'remove_target_price': 'remove_target_price'},
        {},
    ),
    'asin_check_now': (
        "Check a tracked product's price right away instead of waiting for its schedule. Costs 1 credit, at most once every 5 minutes (earlier calls return the product unchanged). A paused product must be resumed first. Set wait to get the new price in the answer.",
        {
            "type": "object",
            "properties": {
                "product_id": {
                    "type": "string",
                    "description": "product_id of a tracked product, from asin_track_product or asin_list_tracked."
                },
                "wait": {
                    "type": "boolean",
                    "description": "Answer once the check is done (up to 45 seconds)."
                }
            },
            "required": [
                "product_id"
            ]
        },
        'POST /products/{id}/check',
        {'product_id': 'id', 'wait': 'query:wait'},
        {},
    ),
    'asin_stop_tracking': (
        'Remove a product from the watchlist, with its price history. Free. Ask the user before calling it.',
        {
            "type": "object",
            "properties": {
                "product_id": {
                    "type": "string",
                    "description": "product_id of a tracked product, from asin_track_product or asin_list_tracked."
                }
            },
            "required": [
                "product_id"
            ]
        },
        'DELETE /products/{id}',
        {'product_id': 'id'},
        {},
    ),
    'asin_account': (
        'Your Asin account: plan, credits left (monthly allowance and packs), renewal date, how many products you track out of your limit, the credits they use each month, and the fastest check interval your plan allows. Free.',
        {
            "type": "object",
            "properties": {},
            "required": []
        },
        '/account',
        {},
        {},
    ),
}
