COLUMNS = [
    "id",
    "title",
    "author",
    "genre",
    "publisher",
    "year",
    "name",
    "address",
    "phone",
    "email",
    "user_id",
    "book_id",
    "quantity",
    "unit_price_USD",
    "timestamp",
    "shipping",
    "paid_price",
    "date",
]

CONDITIONS = [
    "startswith",
    "contains",
    "endswith",
    "not_startswith",
    "not_contains",
    "not_endswith",
    "not_equals",
    "equals",
    "greater_than",
    "less_than",
]

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_sorted_data",
            "description": "Get rows with top records from users, books and orders or days with highest revenue",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_type": {
                        "type": "string",
                        "enum": ["users", "books", "orders", "best_days"],
                        "description": "users, books, orders or best_days",
                    },
                    "store_num": {
                        "type": "integer",
                        "enum": [1, 2, 3, 4, 5],
                        "description": "Store number from 1 to 5",
                    },
                    "column_name": {
                        "type": "string",
                        "enum": COLUMNS + ["daily_revenue"],
                        "description": "Column name to sort by. ",
                    },
                    "n": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100,
                        "description": "Number of rows to return (default 3)",
                    },
                    "is_ascending": {
                        "type": "boolean",
                        "description": "True for smallest/cheapest first, False (default) for biggest first",
                    },
                },
                "required": ["store_num", "file_type", "column_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_most_popular",
            "description": "Get the most popular records from users, books or orders",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_type": {
                        "type": "string",
                        "enum": ["users", "books", "orders"],
                        "description": "users, books or orders",
                    },
                    "store_num": {
                        "type": "integer",
                        "enum": [1, 2, 3, 4, 5],
                        "description": "Store number from 1 to 5",
                    },
                    "column_name": {
                        "type": "string",
                        "enum": COLUMNS,
                        "description": "Column name to find the most popular record in",
                    },
                    "n": {
                        "type": "integer",
                        "minimum": 1,
                        "description": "Number of rows to return (default 3)",
                    },
                },
                "required": ["store_num", "file_type", "column_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_unique_users",
            "description": "Get number of unique users",
            "parameters": {
                "type": "object",
                "properties": {
                    "store_num": {
                        "type": "integer",
                        "enum": [1, 2, 3, 4, 5],
                        "description": "Store number from 1 to 5",
                    }
                },
                "required": ["store_num"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_unique_authors",
            "description": "Get number of unique authors",
            "parameters": {
                "type": "object",
                "properties": {
                    "store_num": {
                        "type": "integer",
                        "enum": [1, 2, 3, 4, 5],
                        "description": "Store number from 1 to 5",
                    }
                },
                "required": ["store_num"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_best_author",
            "description": "Get name of top selling author(s)",
            "parameters": {
                "type": "object",
                "properties": {
                    "store_num": {
                        "type": "integer",
                        "enum": [1, 2, 3, 4, 5],
                        "description": "Store number from 1 to 5",
                    }
                },
                "required": ["store_num"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_best_customer_ids",
            "description": "Get ids belonging to the top customer",
            "parameters": {
                "type": "object",
                "properties": {
                    "store_num": {
                        "type": "integer",
                        "enum": [1, 2, 3, 4, 5],
                        "description": "Store number from 1 to 5",
                    }
                },
                "required": ["store_num"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "filter_dashboard",
            "description": "Change the dashboard under some condition. Use when user wants to only filter values, but doesn not want any specific value.",
            "parameters": {
                "type": "object",
                "properties": {
                    "dataset": {
                        "type": "string",
                        "enum": ["users", "books", "orders"],
                        "description": "users, books, orders or best_days",
                    },
                    "column_name": {
                        "type": "string",
                        "enum": COLUMNS,
                        "description": "Column to be filtered",
                    },
                    "condition": {
                        "type": "string",
                        "enum": CONDITIONS,
                        "description": "Condition by which column should be filtered",
                    },
                    "value": {
                        "type": "string",
                        "description": "One or more values to filter against, f.e. 'p', 'p or s'",
                    },
                },
                "required": ["dataset", "column_name", "condition", "value"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "clear_filters",
            "description": "Clear all active filters for a chosen dataset or all datasets",
            "parameters": {
                "type": "object",
                "properties": {
                    "dataset": {
                        "type": "string",
                        "enum": ["books", "users", "orders", "all"],
                        "description": "Dataset to clear filters for",
                    }
                },
                "required": ["dataset"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "count_entities",
            "description": "Count values after filtering by some condition. If filters, columns and value are not provided, counts the whole entity",
            "parameters": {
                "type": "object",
                "properties": {
                    "store_num": {
                        "type": "integer",
                        "enum": [1, 2, 3, 4, 5],
                        "description": "Number of chosen store",
                    },
                    "entity": {
                        "type": "string",
                        "enum": ["users", "books", "orders"],
                        "description": "users, books, orders or best_days",
                    },
                    "column_name": {
                        "type": "string",
                        "enum": COLUMNS,
                        "description": "Column to be filtered",
                    },
                    "condition": {
                        "type": "string",
                        "enum": CONDITIONS,
                        "description": "Condition by which column should be filtered",
                    },
                    "value": {
                        "type": "string",
                        "description": "One or more values to filter against, f.e. 'p', 'p or s'",
                    },
                },
                "required": ["store_num", "entity"],
            },
        },
    },
]
