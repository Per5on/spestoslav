import AsyncStorage from "@react-native-async-storage/async-storage";
import { api, API_BASE_URL, httpStatus } from "../api";
import type { Category } from "./catalogData";
import { Product } from "./model";
const KEY = "spestovnik-catalog-v1:" + API_BASE_URL;
const MAX_AGE = 7 * 24 * 60 * 60 * 1000;
type Cache = { schema_version: 1; saved_at: number; products: Product[] };
export function parseCatalogCache(
  raw: string | null,
  now = Date.now(),
  category: Category = "groceries",
): Cache | null {
  if (!raw) return null;
  try {
    return validateCatalog(JSON.parse(raw), now, category);
  } catch {
    return null;
  }
}
function validateCatalog(value: Cache | null, now: number, category: Category): Cache | null {
  if (
    !value ||
    value.schema_version !== 1 ||
    !Number.isFinite(value.saved_at) ||
    value.saved_at > now ||
    now - value.saved_at > MAX_AGE ||
    !Array.isArray(value.products) ||
    value.products.length > 10000
  )
    return null;
  const ids = new Set<string>();
  if (
    !value.products.every(
      (p: Product) =>
        p &&
        typeof p.id === "string" &&
        typeof p.name === "string" &&
        p.category_code === category &&
        !p.is_demo &&
        !ids.has(p.id) &&
        Boolean(ids.add(p.id)),
    )
  )
    return null;
  const fields = [
    "id",
    "name",
    "category_code",
    "brand",
    "package_quantity",
    "package_unit",
    "barcode",
    "group_code",
    "fuel_type",
    "source_url",
    "source_product_code",
    "source_category",
    "package",
    "catalog_observed_at",
    "image_url",
  ] as const;
  return {
    ...value,
    products: value.products.map(
      (p: Product) =>
        Object.fromEntries(
          fields
            .filter((k) => k in p)
            .map((k) => [k, (p as unknown as Record<string, unknown>)[k]]),
        ) as Product,
    ),
  };
}
export async function loadProducts(
  signal: AbortSignal,
  force: boolean,
  onCached: (rows: Product[]) => void,
  category: Category = "groceries",
  preferredRead?: (signal: AbortSignal) => Promise<Product[] | undefined>,
) {
  const key = KEY + (category === "groceries" ? "" : ":" + category);
  let cached: Cache | null = null;
  try {
    cached = parseCatalogCache(await AsyncStorage.getItem(key), Date.now(), category);
    if (cached && !signal.aborted) onCached(cached.products);
  } catch {}
  if (signal.aborted) throw new Error("Catalogue read cancelled");
  if (cached && !force && Date.now() - cached.saved_at < 6 * 60 * 60 * 1000)
    return { products: cached.products, cached: true };
  try {
    return { products: await refreshProducts(key, category, preferredRead), cached: false };
  } catch (e) {
    if (cached && !signal.aborted)
      return { products: cached.products, cached: true };
    throw e;
  }
}

const pending = new Map<string, Promise<Product[]>>();
function refreshProducts(
  key: string, category: Category,
  preferredRead?: (signal: AbortSignal) => Promise<Product[] | undefined>,
) {
  const existing = pending.get(key);
  if (existing) return existing;

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 35000);
  const read = async () => await preferredRead?.(controller.signal) ?? fetchProducts(category, controller.signal);
  const request = read().then(async products => {
    if (controller.signal.aborted) throw new Error("Catalogue refresh timed out");
    const now = Date.now();
    const validated = validateCatalog({ schema_version: 1, saved_at: now, products }, now, category);
    if (!validated) throw new Error("Invalid catalogue");
    await AsyncStorage.setItem(key, JSON.stringify(validated)).catch(() => undefined);
    return validated.products;
  }).finally(() => {
    clearTimeout(timer);
    pending.delete(key);
  });
  pending.set(key, request);
  return request;
}

async function fetchProducts(category: Category, signal: AbortSignal): Promise<Product[]> {
  if (category !== "fuel") {
    try {
      const snapshot = await api<{ schema_version: number; products: Product[] }>(
        `/api/v1/catalog/${category}`, { signal },
      );
      if (snapshot.schema_version !== 1) throw new Error("Unknown catalogue");
      return snapshot.products;
    } catch (e) {
      if (httpStatus(e) !== 404) throw e;
    }
  }

  // Fuel and older server deployments expose the paginated product route.
  const products: Product[] = [];
  for (let offset = 0; offset < 10000; offset += 100) {
    const page = await api<Product[]>(
      `/api/v1/products?category_code=${category}&limit=100&offset=${offset}`, { signal },
    );
    products.push(...page);
    if (page.length < 100) return products;
  }
  throw new Error("Catalogue pagination capacity exceeded");
}
