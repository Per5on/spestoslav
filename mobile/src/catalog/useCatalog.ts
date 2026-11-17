import { useEffect, useState } from "react";
import { api } from "../api";
import { MessageKey } from "../i18n";
import { Product, Store, Price, Retailer } from "./model";
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
  const [chains, setChains] = useState<{ category: Category; rows: Retailer[] }>({ category, rows: [] });
  const [chainLoading, setChainLoading] = useState(true);
  const [chainError, setChainError] = useState(false);
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
    (async () => {
        try {
          const loaded = category === "fuel" ? {
            products: await allPages<Product>("/api/v1/products?category_code=fuel", controller.signal, 100), cached: false,
          } : await loadProducts(controller.signal, revision > 0, rows => {
            if (alive) setProducts(rows);
          }, category);
          const real = loaded.products;
          if (alive) setCached(loaded.cached);
          if (!demo || category === "fuel") {
            if (alive) setProducts(real);
            return;
          }
          try {
            const sample = await api<{ is_demo: boolean; products: Product[] }>(
              `/api/v1/demo/catalog?category_code=${category}`,
              { signal: controller.signal },
            );
            if (alive)
              setProducts([
                ...(sample.is_demo
                  ? sample.products.map((p) => ({ ...p, is_demo: true }))
                  : []),
                ...real,
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
  useEffect(() => {
    const controller = new AbortController();
    setChainLoading(true); setChainError(false);
    api<{ retailers: Retailer[] }>(`/api/v1/catalog?category_code=${category}`, { signal: controller.signal })
      .then(result => { if (!controller.signal.aborted) setChains({ category, rows: result.retailers.filter(r => r.category_code === category) }); })
      .catch(() => { if (!controller.signal.aborted) setChainError(true); })
      .finally(() => { if (!controller.signal.aborted) setChainLoading(false); });
    return () => controller.abort();
  }, [category, revision]);
  return {
    cached,
    retailers: chains.category === category ? chains.rows : [],
    chainLoading, chainError,
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
