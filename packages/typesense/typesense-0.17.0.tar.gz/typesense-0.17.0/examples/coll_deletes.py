import typesense

client = typesense.Client(
    {
        "api_key": "abcd",
        "nodes": [{"host": "localhost", "port": "8108", "protocol": "http"}],
        "connection_timeout_seconds": 2,
    }
)

products_schema = {
    "enable_nested_fields": True,
    "name": "Foo22",
    "fields": [
        {"name": "id", "type": "string", "index": True, "sort": True},
        {"name": "title", "type": "string", "sort": True},
        {"name": "body_html", "type": "string", "optional": True},
        {"name": "vendor", "type": "string", "optional": True},
        {"name": "product_type", "type": "string", "optional": True},
        {"name": "handle", "type": "string"},
        {
            "name": "date",
            "type": "int64",
            "optional": True,
            "sort": True,
        },
        {"name": "status", "type": "string"},
        {"name": "tags", "type": "string", "optional": True},
        {"name": "variants", "type": "object[]", "optional": True},
        {
            "name": "price",
            "type": "float",
            "optional": True,
            "sort": True,
            "facet": True
        },
        {"name": "variants.image_id", "type": "auto", "optional": True},
        {
            "name": "options",
            "type": "object[]",
            "optional": True,
            "facet": True,
        },
        {"name": "images", "type": "object[]", "optional": True},
        {"name": "image", "type": "object", "optional": True},
        {"name": "keywords", "type": "string[]", "optional": True},
        {"name": "is_deleted", "type": "bool", "optional": True},
        {"name": "review_rating_value", "type": "int32", "optional": True},
        {"name": "review_rating_count", "type": "int32", "optional": True},
        {
            "name": "inventory_qty",
            "type": "int64",
            "optional": True,
            "sort": True,
        },
        {
            "name": "discount",
            "type": "float",
            "optional": True,
            "sort": True,
            "facet": True
        },
        {
            "name": "embedding",
            "type": "float[]",
            "embed": {
                "from": [
                    "title",
                ],
                "model_config": {
                    "model_name": "openai/text-embedding-ada-002",
                    "api_key": "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"
                }
            }
        }
    ],
}

x = client.collections.create(products_schema)
print(x)
