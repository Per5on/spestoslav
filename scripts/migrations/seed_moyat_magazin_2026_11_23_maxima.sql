WITH offer AS (
  SELECT p.id AS product_id, 1.69::numeric AS price_eur,
         '2026-11-23T00:00:00+02:00'::timestamptz AS starts_at,
         '2026-12-07T00:00:00+02:00'::timestamptz AS ends_at
  FROM grocery_catalog_identities i
  JOIN products p ON p.id = i.product_id
  WHERE i.source = 'burlex-public-basket' AND i.source_product_code = '303619'
    AND p.active AND p.category_code = 'groceries'
    AND p.package_quantity = 250 AND p.package_unit = 'g'
), written AS (
  INSERT INTO current_prices
    (id, product_id, branch_id, price_eur, source, observed_at, verified_at, expires_at)
  SELECT gen_random_uuid(), o.product_id, b.id, o.price_eur, 'RETAILER_PROMO_MAXIMUM',
         o.starts_at, now(), o.ends_at
  FROM offer o CROSS JOIN store_branches b
  JOIN catalog_retailers r ON r.code = b.retailer_code AND r.active
  WHERE b.active AND b.retailer_code = 'moyat_magazin'
    AND b.source = 'OFFICIAL_STORE_LOCATOR'
    AND o.starts_at <= now() AND o.ends_at > now()
    AND NOT EXISTS (
      SELECT 1 FROM promotions pr
      WHERE pr.branch_id = b.id AND pr.product_id = o.product_id
        AND pr.verified AND pr.starts_at <= now() AND (pr.ends_at IS NULL OR pr.ends_at > now())
    )
  ON CONFLICT (product_id, branch_id) DO UPDATE
    SET price_eur = excluded.price_eur, source = excluded.source,
        observed_at = excluded.observed_at, verified_at = excluded.verified_at,
        expires_at = excluded.expires_at
    WHERE current_prices.expires_at <= now()
      OR (current_prices.source = 'RETAILER_PROMO_MAXIMUM'
          AND current_prices.observed_at <= excluded.observed_at
          AND (current_prices.observed_at, current_prices.expires_at, current_prices.price_eur)
              IS DISTINCT FROM (excluded.observed_at, excluded.expires_at, excluded.price_eur))
  RETURNING 1
)
SELECT count(*) AS inserted_or_updated FROM written;
