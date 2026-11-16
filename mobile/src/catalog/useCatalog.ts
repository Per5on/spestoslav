import { useEffect, useState } from "react";
import { api } from "../api";
import { MessageKey } from "../i18n";
import { Product, Store, Price } from "./model";
import { loadProducts } from "./cache";
async function allPages<T>(
  path: string,
  signal: AbortSignal,
  pageSize = 500,
): Promise<T[]> {
  const result: T[] = [];
  for (let offset = 0; offset < 10000; offset += pageSize) {
    const page = await api<T[]>(path + `&limit=${pageSize}&offset=${offset}`, {
      signal,
    });
    result.push(...page);
    if (page.length < pageSize) return result;
  }
  throw new Error("Too many rows; refine the locality");
}
export type Category = "groceries" | "technology" | "fuel";
export function useCatalog(
  category: Category,
  localityId: string | undefined,
  demo: boolean,
  includePrices = true,
) {
  const [revision, setRevision] = useState(0);
  const [cached, setCached] = useState(false);
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
    setCached(false);
    setLoading(category !== "fuel");
    if (category !== "fuel")
      (async () => {
        try {
          const loaded =
            category === "groceries"
              ? await loadProducts(controller.signal, revision > 0, (rows) => {
                  if (alive) {
                    setProducts(rows);
                    setCached(true);
                  }
                })
              : {
                  products: await allPages<Product>(
                    "/api/v1/products?category_code=technology",
                    controller.signal,
                    100,
                  ),
                  cached: false,
                };
          const real = loaded.products;
          if (alive) setCached(loaded.cached);
          if (!demo || category !== "groceries") {
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
          const stores = await allPages<Store>(
            `/api/v1/stores?locality_id=${localityId}&category_code=${category}`,
            controller.signal,
          );
          if (alive) setData({ scope, stores, prices: [] });
          if (!includePrices) return;
          try {
            const prices = await allPages<Price>(
              `/api/v1/prices/current?locality_id=${localityId}`,
              controller.signal,
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
  }, [category, localityId, revision, includePrices]);
  return {
    cached,
    products: productScope === category ? products : [],
    loading: category !== "fuel" && (loading || productScope !== category),
    error,
    stores: data.scope === scope ? data.stores : [],
    prices: data.scope === scope ? data.prices : [],
    storeLoading: Boolean(localityId) && (storeLoading || data.scope !== scope),
    storeError,
    refresh: () => setRevision((v) => v + 1),
  };
}
