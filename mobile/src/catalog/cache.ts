import AsyncStorage from "@react-native-async-storage/async-storage";
import { api, API_BASE_URL, httpStatus } from "../api";
import { Product } from "./model";
const KEY = "spestovnik-catalog-v1:" + API_BASE_URL;
const MAX_AGE = 7 * 24 * 60 * 60 * 1000;
type Cache = { schema_version: 1; saved_at: number; products: Product[] };
export function parseCatalogCache(
  raw: string | null,
  now = Date.now(),
  category: "groceries" | "technology" = "groceries",
): Cache | null {
  if (!raw) return null;
  try {
    return validateCatalog(JSON.parse(raw), now, category);
  } catch {
    return null;
  }
}
function validateCatalog(value: Cache | null, now: number, category: "groceries" | "technology"): Cache | null {
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
    "source_url",
    "source_product_code",
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
  category: "groceries" | "technology" = "groceries",
) {
  const key = KEY + (category === "groceries" ? "" : ":technology");
  let cached: Cache | null = null;
  try {
    cached = parseCatalogCache(await AsyncStorage.getItem(key), Date.now(), category);
    if (cached && !signal.aborted) onCached(cached.products);
  } catch {}
  if (cached && !force && Date.now() - cached.saved_at < 6 * 60 * 60 * 1000)
    return { products: cached.products, cached: true };
  let products: Product[] = [];
  try {
    try {
      const snapshot = await api<{
        schema_version: number;
        products: Product[];
      }>(`/api/v1/catalog/${category}`, { signal });
      if (snapshot.schema_version !== 1) throw new Error("Unknown catalogue");
      products = snapshot.products;
    } catch (e) {
      if (httpStatus(e) !== 404) throw e;
      // Compatibility during the staged API rollout, without silently stopping at 100.
      for (let offset = 0; offset < 10000; offset += 100) {
        const page = await api<Product[]>(
          `/api/v1/products?category_code=${category}&limit=100&offset=${offset}`,
          { signal },
        );
        products.push(...page);
        if (page.length < 100) break;
        if (offset === 9900)
          throw new Error("Catalogue pagination capacity exceeded");
      }
    }
    if (signal.aborted) throw new Error("Aborted");
    const now = Date.now();
    const validated = validateCatalog({
      schema_version: 1,
      saved_at: now,
      products,
    }, now, category);
    if (!validated) throw new Error("Invalid catalogue");
    void AsyncStorage.setItem(key, JSON.stringify(validated)).catch(() => undefined);
    return { products: validated.products, cached: false };
  } catch (e) {
    if (cached && !signal.aborted)
      return { products: cached.products, cached: true };
    throw e;
  }
}
