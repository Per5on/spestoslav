import AsyncStorage from "@react-native-async-storage/async-storage";
import { api, API_BASE_URL, httpStatus } from "../api";
import { loadProducts } from "./cache";
import type { OnlinePrice, Price, Product, Retailer, Store } from "./model";

const categories = ["groceries", "technology", "fuel"] as const;
export type Category = typeof categories[number];

const prefix = "spestovnik-local-catalog-v1:" + API_BASE_URL + ":";
const freshFor = 10 * 60 * 1000;
const day = 24 * 60 * 60 * 1000;
type Scope = { category: Category; localityId: string };
type Snapshot<T> = { localityId: string; savedAt: number; rows: T[] };

async function allPages<T>(path: string, signal: AbortSignal, pageSize = 500): Promise<T[]> {
  const result: T[] = [];
  for (let offset = 0; offset < 10000; offset += pageSize) {
    const page = await api<T[]>(path + `&limit=${pageSize}&offset=${offset}`, { signal });
    result.push(...page);
    if (page.length < pageSize) return result;
  }
  throw new Error("Catalogue pagination capacity exceeded");
}

function catalogResource<T>(
  slot: string,
  fetchRows: (scope: Scope, signal: AbortSignal) => Promise<T[]>,
  prepare: (rows: T[], savedAt: number, now: number) => T[] = rows => rows,
  maxAge = day,
) {
  const pending = new Map<string, Promise<T[]>>();
  const latest = new Map<string, Promise<T[]>>();
  let generation = 0;
  return {
    async clear() {
      generation += 1;
      latest.clear();
      await AsyncStorage.multiRemove(categories.map(category => prefix + slot + ":" + category));
    },
    async load(
      scope: Scope,
      signal: AbortSignal,
      force = false,
      onCached: (rows: T[]) => void = () => {},
    ): Promise<T[]> {
      const key = prefix + slot + ":" + scope.category;
      const startedIn = generation;
      let saved: Snapshot<T> | null = null;
      try {
        const raw = await AsyncStorage.getItem(key);
        if (raw) {
          const candidate: Snapshot<T> = JSON.parse(raw);
          const now = Date.now();
          if (candidate?.localityId === scope.localityId &&
              Number.isFinite(candidate.savedAt) && candidate.savedAt <= now &&
              now - candidate.savedAt < maxAge && Array.isArray(candidate.rows)) {
            const rows = prepare(candidate.rows, candidate.savedAt, now);
            saved = { ...candidate, rows };
            if (rows.length !== candidate.rows.length) force = true;
            if (!signal.aborted && startedIn === generation) onCached(rows);
          }
        }
      } catch {
        // A storage error shouldn't prevent live catalogue loading.
      }
      if (signal.aborted || startedIn !== generation) throw new Error("Catalogue read cancelled");
      if (saved && !force && Date.now() - saved.savedAt < freshFor) return saved.rows;

      const requestKey = key + ":" + scope.localityId;
      let request = pending.get(requestKey);
      if (!request) {
        // Share the read across screens and the Android job. Leaving a tab
        // stops delivery to that screen while the bounded read warms its cache.
        const controller = new AbortController();
        const timer = setTimeout(() => controller.abort(), 35000);
        const started = fetchRows(scope, controller.signal).then(async rows => {
          if (controller.signal.aborted) throw new Error("Catalogue refresh timed out");
          const savedAt = Date.now();
          const prepared = prepare(rows, savedAt, savedAt);
          const raw = JSON.stringify({ localityId: scope.localityId, savedAt, rows: prepared });
          if (latest.get(key) === started) {
            // Leave room for Android's per-entry cursor limit.
            const write = raw.length < 750000 ? AsyncStorage.setItem(key, raw) : AsyncStorage.removeItem(key);
            await write.catch(() => undefined);
          }
          return prepared;
        }).finally(() => {
          clearTimeout(timer);
          pending.delete(requestKey);
          if (latest.get(key) === started) latest.delete(key);
        });
        pending.set(requestKey, started);
        latest.set(key, started);
        request = started;
      }
      return request;
    },
  };
}

function localPath(path: string, { category, localityId }: Scope) {
  return `/api/v1/${path}?locality_id=${encodeURIComponent(localityId)}&category_code=${category}`;
}

type FuelSnapshot = {
  schema_version: number;
  locality_id: string;
  products: Product[];
  stores: Store[];
  prices: Price[];
  online: OnlinePrice[];
};
const fuelRequests = new Map<string, Promise<FuelSnapshot | undefined>>();
let fuelSnapshotUnavailableUntil = 0;

async function fuelSnapshotField<K extends "products" | "stores" | "prices" | "online">(
  field: K, scope: Scope, signal: AbortSignal,
): Promise<FuelSnapshot[K] | undefined> {
  if (scope.category !== "fuel" || Date.now() < fuelSnapshotUnavailableUntil) return;
  const localityId = scope.localityId;
  let request = fuelRequests.get(localityId);
  if (!request) {
    // Each consumer has its own cache and cancellation. The shared HTTP request
    // is bounded by the API timeout even if all consumers leave the screen.
    request = api<FuelSnapshot>(`/api/v1/fuel-snapshot?locality_id=${encodeURIComponent(localityId)}`, {}, 5000)
      .then(result => {
        if (result?.schema_version !== 1 || result.locality_id !== localityId ||
            !Array.isArray(result.products) || !Array.isArray(result.stores) ||
            !Array.isArray(result.prices) || !Array.isArray(result.online)) return undefined;
        return result;
      })
      .catch(error => {
        if (httpStatus(error) === 404) fuelSnapshotUnavailableUntil = Date.now() + freshFor;
        return undefined; // Older hosts and failed snapshots retain the independent reads.
      })
      .finally(() => fuelRequests.delete(localityId));
    fuelRequests.set(localityId, request);
  }
  const result = await request;
  if (signal.aborted) throw new Error("Catalogue read cancelled");
  return result?.[field];
}

export function loadCatalogProducts(
  scope: { category: Category; localityId?: string }, signal: AbortSignal, force: boolean,
  onCached: (rows: Product[]) => void,
) {
  const localityId = scope.localityId;
  return loadProducts(signal, force, onCached, scope.category,
    scope.category === "fuel" && localityId
      ? requestSignal => fuelSnapshotField("products", { category: "fuel", localityId }, requestSignal)
      : undefined);
}

export const storesResource = catalogResource<Store>("stores",
  async (scope, signal) => await fuelSnapshotField("stores", scope, signal) ?? allPages(localPath("stores", scope), signal),
  rows => rows.flatMap(row => {
    if (typeof row?.id !== "string" || typeof row.retailer_name !== "string" ||
        typeof row.address !== "string") return [];
    const { id, retailer_name, retailer_code, branch_name, address } = row;
    return [{ id, retailer_name, retailer_code, branch_name, address }];
  }), 7 * day);

export const pricesResource = catalogResource<Price>("prices",
  async (scope, signal) => await fuelSnapshotField("prices", scope, signal) ?? allPages(localPath("prices/current", scope), signal),
  (rows, savedAt, now) => rows.flatMap(row => {
    if (typeof row?.product_id !== "string" || typeof row.branch_id !== "string" ||
        !Number.isFinite(Number(row.price_eur)) || Number(row.price_eur) <= 0) return [];
    const expiry = row.expires_at ?? new Date(savedAt + day).toISOString();
    if (!(Date.parse(expiry) > now)) return [];
    const { product_id, branch_id, price_eur, verified_at } = row;
    return [{ product_id, branch_id, price_eur, verified_at, expires_at: expiry }];
  }),
);

export const onlineResource = catalogResource<OnlinePrice>("online",
  async (scope, signal) => await fuelSnapshotField("online", scope, signal) ?? allPages(localPath("national-offers", scope), signal, 100),
  (rows, _savedAt, now) => rows.flatMap(row => {
    if (row?.price_scope !== "NATIONAL_ONLINE" || typeof row.product_id !== "string" ||
        typeof row.retailer_code !== "string" || !Number.isFinite(Number(row.price_eur)) ||
        Number(row.price_eur) <= 0 || !(Date.parse(row.valid_until) > now)) return [];
    const { product_id, retailer_code, price_eur, valid_until, source_reference, price_scope } = row;
    return [{ product_id, retailer_code, price_eur, valid_until, source_reference, price_scope }];
  }),
);

export const fuelChainsResource = catalogResource<Retailer>("retailers", async ({ category }, signal) => {
  const result = await api<{ retailers: Retailer[] }>(`/api/v1/catalog?category_code=${category}`, { signal });
  return result.retailers;
}, rows => rows.filter(row => row?.category_code === "fuel" &&
  typeof row.code === "string" && typeof row.name === "string"), 7 * day);

async function refreshCategory(
  category: Category, localityId: string | undefined, signal: AbortSignal, force: boolean,
) {
  const products = loadCatalogProducts({ category, localityId }, signal, force, () => {});
  const reads = localityId
    ? [products, storesResource.load({ category, localityId }, signal),
      pricesResource.load({ category, localityId }, signal),
      onlineResource.load({ category, localityId }, signal)]
    : category === "fuel"
      ? [products, fuelChainsResource.load({ category, localityId: "" }, signal)]
      : [products];
  const outcomes = await Promise.allSettled(reads);
  return !signal.aborted && outcomes.every(result => result.status === "fulfilled");
}

export async function syncCatalogs(localityId: string | undefined, signal: AbortSignal) {
  const outcomes = await Promise.all(categories.map(category => refreshCategory(category, localityId, signal, true)));
  return outcomes.every(Boolean);
}

export async function warmOtherCatalogs(category: Category, localityId: string, signal: AbortSignal) {
  for (const next of ["fuel", "groceries", "technology"] as const) {
    if (signal.aborted) return;
    if (next !== category) await refreshCategory(next, localityId, signal, false);
  }
}

export async function clearLocalCatalogs() {
  await Promise.all([storesResource.clear(), pricesResource.clear(), onlineResource.clear()]);
}
