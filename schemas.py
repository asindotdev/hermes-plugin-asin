"""Tool schemas (what the model reads) and how each tool maps to the API."""

# name: (description, JSON schema of the arguments, API path, {argument: API parameter}, fixed parameters)
TOOLS = {
    'asin_search_amazon': (
        'Search an Amazon store and return products with their ASIN, title, price, currency, rating and review count.',
        {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search keywords."
                },
                "marketplace": {
                    "type": "string",
                    "description": "Amazon store, for example com (default) or de.",
                    "enum": [
                        "com",
                        "co.uk",
                        "de",
                        "fr",
                        "it",
                        "es",
                        "ca",
                        "co.jp"
                    ]
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
        'Get the price history Asin has recorded for an Amazon product: lowest, highest and average price, and the dated price points. Empty when Asin has no history for the product yet.',
        {
            "type": "object",
            "properties": {
                "asin": {
                    "type": "string",
                    "description": "10-character ASIN."
                },
                "marketplace": {
                    "type": "string",
                    "description": "Amazon store, for example com (default).",
                    "enum": [
                        "com",
                        "co.uk",
                        "de",
                        "fr",
                        "it",
                        "es",
                        "ca",
                        "co.jp"
                    ]
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
        "Get the offers Asin has already collected for an Amazon product: Amazon's own price, the lowest new and used prices, and each seller's offer. Empty when Asin has not checked the product yet.",
        {
            "type": "object",
            "properties": {
                "asin": {
                    "type": "string",
                    "description": "10-character ASIN."
                },
                "marketplace": {
                    "type": "string",
                    "description": "Amazon store, for example com (default).",
                    "enum": [
                        "com",
                        "co.uk",
                        "de",
                        "fr",
                        "it",
                        "es",
                        "ca",
                        "co.jp"
                    ]
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
}
