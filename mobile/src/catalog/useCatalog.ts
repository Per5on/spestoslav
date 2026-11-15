import { useEffect, useState } from "react";
import { api } from "../api";
import { MessageKey } from "../i18n";
import { Product, Store, Price } from "./model";
export type Category = "groceries" | "technology" | "fuel";
export function useCatalog(
  category: Category,
  localityId: string | undefined,
  demo: boolean,
) {
  const [revision, setRevision] = useState(0);
  const [products, setProducts] = useState<Product[]>([]),
    [productScope, setProductScope] = useState<Category>("groceries");
  const [loading, setLoading] = useState(true),
    [error, setError] = useState<MessageKey | "">("");
  const scope = category + ":" + (localityId ?? "");
  const [data, setData] = useState<{
    scope: string;
    stores: Store[];
    prices: Price[];
  }>({ scope: "", stores: [], prices: [] });
  const [storeLoading, setStoreLoading] = useState(false),
    [storeError, setStoreError] = useState<MessageKey | "">("");
  useEffect(() => {
    let alive = true;
    const controller = new AbortController();
    setProducts([]);
    setProductScope(category);
    setError("");
    setLoading(category === "groceries");
    if (category === "groceries")
      (async () => {
        try {
          const real = await api<Product[]>(
            "/api/v1/products?category_code=groceries&limit=100",
            { signal: controller.signal },
          );
          if (!demo) {
            if (alive) setProducts(real);
            return;
          }
          try {
            const sample = await api<{ is_demo: boolean; products: Product[] }>(
              "/api/v1/demo/catalog",
              { signal: controller.signal },
            );
            if (alive)
              setProducts([
                ...real,
                ...(sample.is_demo
                  ? sample.products.map((p) => ({ ...p, is_demo: true }))
                  : []),
              ]);
          } catch {
            if (alive) {
              setProducts(real);
              setError("demoError");
            }
          }
        } catch {
          if (alive) setError("catalogError");
        } finally {
          if (alive) setLoading(false);
        }
      })();
    return () => {
      alive = false;
      controller.abort();
    };
  }, [category, demo, revision]);
  useEffect(() => {
    let alive = true;
    const controller = new AbortController();
    setData({ scope, stores: [], prices: [] });
    setStoreError("");
    setStoreLoading(Boolean(localityId));
    if (localityId)
      (async () => {
        try {
          const stores = await api<Store[]>(
            `/api/v1/stores?locality_id=${localityId}&category_code=${category}&limit=500`,
            { signal: controller.signal },
          );
          if (alive) setData({ scope, stores, prices: [] });
          try {
            const prices = await api<Price[]>(
              `/api/v1/prices/current?locality_id=${localityId}&limit=500`,
              { signal: controller.signal },
            );
            if (alive) setData({ scope, stores, prices });
          } catch {
            if (alive) setStoreError("pricesError");
          }
        } catch {
          if (alive) setStoreError("storesError");
        } finally {
          if (alive) setStoreLoading(false);
        }
      })();
    return () => {
      alive = false;
      controller.abort();
    };
  }, [category, localityId, revision]);
  return {
    products: productScope === category ? products : [],
    loading: category === "groceries" && (loading || productScope !== category),
    error,
    stores: data.scope === scope ? data.stores : [],
    prices: data.scope === scope ? data.prices : [],
    storeLoading: Boolean(localityId) && (storeLoading || data.scope !== scope),
    storeError,
    refresh: () => setRevision((v) => v + 1),
  };
}
