import AsyncStorage from "@react-native-async-storage/async-storage";
import { api, API_BASE_URL } from "../api";
import { Product } from "./model";
const KEY = "spestovnik-catalog-v1:" + API_BASE_URL;
const MAX_AGE = 7 * 24 * 60 * 60 * 1000;
type Cache = { schema_version: 1; saved_at: number; products: Product[] };
export function parseCatalogCache(
  raw: string | null,
  now = Date.now(),
): Cache | null {
  if (!raw) return null;
  try {
    const value = JSON.parse(raw);
    if (
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
          p.category_code === "groceries" &&
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
  } catch {
    return null;
  }
}
export async function loadProducts(
  signal: AbortSignal,
  force: boolean,
  onCached: (rows: Product[]) => void,
) {
  let cached: Cache | null = null;
  try {
    cached = parseCatalogCache(await AsyncStorage.getItem(KEY));
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
      }>("/api/v1/catalog/groceries", { signal });
      if (snapshot.schema_version !== 1) throw new Error("Unknown catalogue");
      products = snapshot.products;
    } catch (e) {
      if (!String(e).includes("404")) throw e;
      // Compatibility during the staged API rollout, without silently stopping at 100.
      for (let offset = 0; offset < 10000; offset += 100) {
        const page = await api<Product[]>(
          `/api/v1/products?category_code=groceries&limit=100&offset=${offset}`,
          { signal },
        );
        products.push(...page);
        if (page.length < 100) break;
        if (offset === 9900)
          throw new Error("Catalogue pagination capacity exceeded");
      }
    }
    if (signal.aborted) throw new Error("Aborted");
    const raw = JSON.stringify({
      schema_version: 1,
      saved_at: Date.now(),
      products,
    });
    const validated = parseCatalogCache(raw);
    if (!validated) throw new Error("Invalid catalogue");
    try {
      await AsyncStorage.setItem(KEY, JSON.stringify(validated));
    } catch {}
    return { products: validated.products, cached: false };
  } catch (e) {
    if (cached && !signal.aborted)
      return { products: cached.products, cached: true };
    throw e;
  }
}
