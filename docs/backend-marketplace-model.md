# Marketplace backend data model

- `store_branches` are registered physical branches linked to canonical `inhabited_localities`; only active registered branches are returned.
- `product_barcodes` holds verified barcode aliases for products.
- `current_prices` holds exactly one verified current price per product and branch. It is not a historical price ledger.
- `promotions` holds verified offers with validity dates.
- `price_cache` holds temporary unverified observations. Pending rows are never exposed as current prices. A reviewed observation may update `current_prices`.
- `receipt_scans` and `receipt_items` hold receipt processing metadata and parsed lines. Receipt images belong in object storage; OCR runs asynchronously. Extracted values require review before being accepted.
- All prices are EUR. Receipt uploads and write/review endpoints require authentication and object-storage/OCR configuration before mobile release.
