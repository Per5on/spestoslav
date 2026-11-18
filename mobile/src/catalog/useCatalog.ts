import { useEffect, useMemo, useRef, useState } from "react";
import { api } from "../api";
import { MessageKey } from "../i18n";
import { Product, Store, Price, Retailer } from "./model";
import { loadProducts } from "./cache";
import { sampleProducts } from "./samples";
const noProducts: Product[] = [];
const noStores: Store[] = [];
const noPrices: Price[] = [];
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
  active = true,
) {
  const [chains, setChains] = useState<{ category: Category; rows: Retailer[] }>({ category, rows: [] });
  const [chainLoading, setChainLoading] = useState(true);
  const [chainError, setChainError] = useState(false);
  const [revision, setRevision] = useState(0);
  const [cached, setCached] = useState(false);
  const [products, setProducts] = useState<Partial<Record<Category, Product[]>>>({});
  const loadedRevision = useRef<Partial<Record<Category, number>>>({});
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
    if (!active) return;
    const controller = new AbortController();
    const { signal } = controller;
    const show = (rows: Product[]) => {
      if (!signal.aborted) setProducts(previous => ({ ...previous, [category]: rows }));
    };
    setError("");
    setLoading(category !== "fuel");
    setCached(false);
    const force = revision > (loadedRevision.current[category] ?? 0);
    const load = category === "fuel"
      ? allPages<Product>("/api/v1/products?category_code=fuel", signal, 100)
          .then(rows => ({ products: rows, cached: false }))
      : loadProducts(signal, force, show, category);
    load.then(result => {
      if (signal.aborted) return;
      show(result.products);
      setCached(result.cached);
      if (!result.cached) loadedRevision.current[category] = revision;
    }).catch(() => {
      if (!signal.aborted) setError("catalogError");
    }).finally(() => {
      if (!signal.aborted) setLoading(false);
    });
    return () => controller.abort();
  }, [active, category, revision]);
  useEffect(() => {
    if (!active) return;
    const controller = new AbortController();
    const { signal } = controller;
    setStoreError("");
    setStoreLoading(Boolean(localityId));
    if (localityId) {
      const storesRequest = allPages<Store>(
        `/api/v1/stores?locality_id=${localityId}&category_code=${category}`, signal,
      );
      const pricesRequest = includePrices
        ? allPages<Price>(`/api/v1/prices/current?locality_id=${localityId}`, signal)
        : Promise.resolve(noPrices);
      void storesRequest.then(stores => {
        if (!signal.aborted) setData(previous => ({
          scope,
          stores,
          prices: includePrices && previous.scope === scope ? previous.prices : noPrices,
        }));
      }).catch(() => undefined);
      void Promise.allSettled([storesRequest, pricesRequest]).then(([stores, prices]) => {
        if (signal.aborted) return;
        if (stores.status === "rejected") {
          setStoreError("storesError");
        } else if (prices.status === "rejected") {
          setStoreError("pricesError");
        } else {
          setData({ scope, stores: stores.value, prices: prices.value });
        }
        setStoreLoading(false);
      });
    }
    return () => controller.abort();
  }, [active, category, localityId, revision, includePrices]);
  useEffect(() => {
    if (!active) return;
    const controller = new AbortController();
    setChainLoading(true); setChainError(false);
    api<{ retailers: Retailer[] }>(`/api/v1/catalog?category_code=${category}`, { signal: controller.signal })
      .then(result => { if (!controller.signal.aborted) setChains({ category, rows: result.retailers.filter(r => r.category_code === category) }); })
      .catch(() => { if (!controller.signal.aborted) setChainError(true); })
      .finally(() => { if (!controller.signal.aborted) setChainLoading(false); });
    return () => controller.abort();
  }, [active, category, revision]);
  const real = products[category] ?? noProducts;
  const visibleProducts = useMemo(() => demo && category !== "fuel"
    ? [...sampleProducts.filter(row => row.category_code === category), ...real]
    : real, [demo, category, real]);
  return {
    cached,
    retailers: chains.category === category ? chains.rows : [],
    chainLoading, chainError,
    products: visibleProducts,
    loading: category !== "fuel" && loading && real.length === 0 && visibleProducts.length === 0,
    error,
    stores: data.scope === scope ? data.stores : noStores,
    prices: data.scope === scope && includePrices ? data.prices : noPrices,
    storeLoading: Boolean(localityId) && (storeLoading || data.scope !== scope),
    storeError,
    revision,
    refresh: () => setRevision((v) => v + 1),
  };
}
