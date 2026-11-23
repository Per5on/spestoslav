import { useEffect, useMemo, useRef, useState } from "react";
import { AppState } from "react-native";
import type { MessageKey } from "../i18n";
import type { Product, Store, Price, OnlinePrice, Retailer } from "./model";
import { loadProducts } from "./cache";
import {
  fuelChainsResource, onlineResource, pricesResource, storesResource, warmOtherCatalogs, type Category,
} from "./catalogData";
import { sampleProducts } from "./samples";

const noProducts: Product[] = [];
const noStores: Store[] = [];
const noPrices: Price[] = [];
const noOnline: OnlinePrice[] = [];
const noRetailers: Retailer[] = [];
type Products = { rows: Product[]; cached: boolean };
type LocalData = { localityId: string; stores?: Store[]; prices?: Price[]; online?: OnlinePrice[] };

export function useCatalog(
  category: Category,
  localityId: string | undefined,
  demo: boolean,
  active: boolean,
) {
  const [revision, setRevision] = useState(0);
  const [resumeRevision, setResumeRevision] = useState(0);
  const [products, setProducts] = useState<Partial<Record<Category, Products>>>({});
  const [locals, setLocals] = useState<Partial<Record<Category, LocalData>>>({});
  const [chains, setChains] = useState<Retailer[]>();
  const [finished, setFinished] = useState("");
  const [error, setError] = useState<MessageKey | "">("");
  const [storeError, setStoreError] = useState<MessageKey | "">("");
  const [chainError, setChainError] = useState(false);
  const manual = useRef<{ category: Category; localityId?: string; revision: number }>(null);
  const [refreshing, setRefreshing] = useState(false);
  const loadKey = `${category}:${localityId ?? ""}:${resumeRevision}:${revision}`;
  const loaded = finished === loadKey;
  const data = locals[category]?.localityId === localityId ? locals[category] : undefined;

  useEffect(() => {
    let previous = AppState.currentState;
    const subscription = AppState.addEventListener("change", state => {
      if (state === "active" && previous !== "active") setResumeRevision(value => value + 1);
      previous = state;
    });
    return () => subscription.remove();
  }, []);

  useEffect(() => {
    if (!active) {
      setRefreshing(false);
      return;
    }
    const controller = new AbortController();
    const { signal } = controller;
    const requested = manual.current;
    const force = requested !== null && requested.category === category &&
      requested.localityId === localityId && requested.revision === revision;
    if (requested && !force) manual.current = null;
    setRefreshing(force);
    setError("");
    setStoreError("");
    setChainError(false);

    const showProducts = (rows: Product[], cached: boolean) => {
      if (!signal.aborted) setProducts(previous =>
        previous[category]?.rows === rows && previous[category]?.cached === cached
          ? previous : { ...previous, [category]: { rows, cached } });
    };
    function show<K extends "stores" | "prices" | "online">(field: K, rows: LocalData[K]) {
      if (!localityId || signal.aborted) return;
      setLocals(previous => {
        const current = previous[category]?.localityId === localityId ? previous[category] : undefined;
        if (current?.[field] === rows) return previous;
        return { ...previous, [category]: { ...current, localityId, [field]: rows } };
      });
    }
    const showChains = (rows: Retailer[]) => {
      if (!signal.aborted) setChains(rows);
    };

    const productRead = category !== "fuel" || localityId
      ? loadProducts(signal, force, rows => showProducts(rows, true), category)
        .then(result => showProducts(result.products, result.cached))
        .catch(() => {
          if (!signal.aborted) setError("catalogError");
        })
      : Promise.resolve();

    const loadLocal = async (id: string) => {
      const scope = { category, localityId: id };
      const [stores, prices, online] = await Promise.allSettled([
        storesResource.load(scope, signal, force, rows => show("stores", rows))
          .then(rows => show("stores", rows)),
        pricesResource.load(scope, signal, force, rows => show("prices", rows))
          .then(rows => show("prices", rows)),
        onlineResource.load(scope, signal, force, rows => show("online", rows))
          .then(rows => show("online", rows)),
      ]);
      if (signal.aborted) return;
      if (stores.status === "rejected") setStoreError("storesError");
      else if (prices.status === "rejected" || online.status === "rejected") setStoreError("pricesError");
    };
    const localRead = localityId
      ? loadLocal(localityId)
      : category === "fuel"
        ? fuelChainsResource.load({ category, localityId: "" }, signal, force, showChains)
          .then(showChains).catch(() => {
            if (!signal.aborted) setChainError(true);
          })
        : Promise.resolve();

    void Promise.all([productRead, localRead]).then(() => {
      if (signal.aborted) return;
      if (manual.current === requested) manual.current = null;
      setFinished(loadKey);
      setRefreshing(false);
    });
    return () => controller.abort();
  }, [active, category, localityId, revision, loadKey]);

  const warm = active && loaded && !refreshing && !error && !storeError;
  useEffect(() => {
    if (!warm || !localityId) return;
    const controller = new AbortController();
    // Let the selected tab render and settle before fetching other tabs.
    const timer = setTimeout(() => void warmOtherCatalogs(category, localityId, controller.signal), 700);
    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [warm, category, localityId]);

  const real = products[category]?.rows ?? noProducts;
  const visibleProducts = useMemo(() => demo && category !== "fuel"
    ? [...sampleProducts.filter(row => row.category_code === category), ...real]
    : real, [demo, category, real]);
  return {
    cached: products[category]?.cached ?? false,
    retailers: chains ?? noRetailers,
    chainLoading: !chains && !loaded,
    chainError,
    products: visibleProducts,
    loading: category !== "fuel" && !products[category] && visibleProducts.length === 0 && !loaded,
    error,
    stores: data?.stores ?? noStores,
    prices: data?.prices ?? noPrices,
    online: data?.online ?? noOnline,
    storeLoading: Boolean(localityId) && !loaded &&
      (!data?.stores || !data.prices || !data.online || (category === "fuel" && !products.fuel)),
    storeError,
    revision,
    refreshing,
    refresh: () => {
      manual.current = { category, localityId, revision: revision + 1 };
      setRefreshing(true);
      setRevision(revision + 1);
    },
  };
}
