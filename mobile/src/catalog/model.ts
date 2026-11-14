export type Product = {
  id: string;
  name: string;
  category_code: string;
  image_url?: string | null;
  package?: string;
  package_quantity?: string | null;
  package_unit?: string | null;
  is_demo?: boolean;
};
export type BasketItem = { product: Product; quantity: number };
export type Store = {
  id: string;
  retailer_name: string;
  branch_name?: string;
  address: string;
};
export type Price = {
  product_id: string;
  branch_id: string;
  price_eur: number;
  verified_at: string;
  expires_at?: string | null;
};
export function changeQuantity(
  items: BasketItem[],
  product: Product,
  delta: number,
): BasketItem[] {
  const existing = items.find((i) => i.product.id === product.id);
  const quantity = Math.max(0, Math.min(99, (existing?.quantity ?? 0) + delta));
  return existing
    ? items.flatMap((i) =>
        i.product.id !== product.id
          ? [i]
          : quantity
            ? [{ ...i, quantity }]
            : [],
      )
    : quantity
      ? [...items, { product, quantity }]
      : items;
}
export function restoreBasket(value: unknown): BasketItem[] {
  if (!Array.isArray(value)) return [];
  const seen = new Set<string>();
  return value
    .filter((i): i is BasketItem => {
      if (
        !i ||
        typeof i.product?.id !== "string" ||
        typeof i.product?.name !== "string" ||
        !Number.isInteger(i.quantity) ||
        i.quantity < 1 ||
        i.quantity > 99 ||
        seen.has(i.product.id)
      )
        return false;
      seen.add(i.product.id);
      return true;
    })
    .slice(0, 100);
}
// Never treat demo fixtures or prices for another locality as purchasable offers.
export function lowestPrice(
  product: Product,
  prices: Price[],
  stores: Store[],
  now = Date.now(),
): number | null {
  if (product.is_demo) return null;
  const ids = new Set(stores.map((s) => s.id));
  const eligible = prices.filter(
    (p) =>
      p.product_id === product.id &&
      ids.has(p.branch_id) &&
      Number(p.price_eur) > 0 &&
      Number.isFinite(Number(p.price_eur)) &&
      (!p.expires_at || Date.parse(p.expires_at) > now),
  );
  return eligible.length
    ? Math.min(...eligible.map((p) => Number(p.price_eur)))
    : null;
}
export function productName(p: Product) {
  return p.name.replace(/^Демо:\s*/i, "");
}
export function matchesProduct(p: Product, query: string) {
  return productName(p)
    .toLocaleLowerCase("bg")
    .includes(query.trim().toLocaleLowerCase("bg"));
}
export function filterLocalities<
  T extends { name: string; name_bg?: string | null; postal_codes: string[] },
>(rows: T[], query: string, mode: "name" | "postal"): T[] {
  const q = query.trim().toLocaleLowerCase("bg");
  return rows.filter((l) =>
    mode === "postal"
      ? l.postal_codes.some((c) => c.startsWith(q))
      : [l.name, l.name_bg].some((n) => n?.toLocaleLowerCase("bg").includes(q)),
  );
}
