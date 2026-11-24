# Catalogue artwork

These 160 × 140 WebPs show representative products and groups. They are bundled in the app and served by the versioned catalogue thumbnail endpoint. The database seed mirrors the same files in the dedicated thumbnail database.

Milk, oil, laptop, television and washing machine reuse the approved app illustrations. The other files are generated studio-style illustrations of the named objects. Product photos already listed under „Трети страни“ keep their original credits.

The app bundles the referenced subset. Four broad group images remain available on the API for older clients. The current client skips a remote download when a manifest entry has the same SHA-256 as its bundled bytes. Regenerate `sha256.json` from the final WebP bytes after editing the pack. Mobile and API tests compare its entries with the actual files.
