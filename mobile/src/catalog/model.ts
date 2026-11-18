export type Retailer = { code: string; name: string; category_code: string; website_url?: string | null };
export type Product = {
  id: string;
  name: string;
  category_code: string;
  image_url?: string | null;
  package?: string;
  package_quantity?: string | number | null;
  package_unit?: string | null;
  is_demo?: boolean;
  fuel_type?: string | null;
  group_code?: string | null;
  source_url?: string | null;
  source_product_code?: string | null;
};
export const MAX_BASKET_ITEMS = 100;
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
  if (!existing && items.length >= MAX_BASKET_ITEMS) return items;
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
        i.product.category_code === "home" ||
        !Number.isInteger(i.quantity) ||
        i.quantity < 1 ||
        i.quantity > 99 ||
        seen.has(i.product.id)
      )
        return false;
      seen.add(i.product.id);
      return true;
    })
    .slice(0, MAX_BASKET_ITEMS);
}
// Never treat demo fixtures or prices for another locality as purchasable offers.
export function lowestPrice(
  product: Product,
  prices: Price[],
  stores: Store[],
  now = Date.now(),
): number | null {
  if (product.is_demo) return null;
  return indexLowestPrices(prices, stores, now).products.get(product.id) ?? null;
}

export function indexLowestPrices(prices: Price[], stores: Store[], now = Date.now()) {
  const ids = new Set(stores.map(store => store.id));
  const products = new Map<string, number>();
  const branches = new Map<string, Map<string, number>>();
  for (const row of prices) {
    const price = Number(row.price_eur);
    if (!ids.has(row.branch_id) || !Number.isFinite(price) || price <= 0 ||
        (row.expires_at && !(Date.parse(row.expires_at) > now))) continue;
    products.set(row.product_id, Math.min(price, products.get(row.product_id) ?? Infinity));
    const branch = branches.get(row.branch_id) ?? new Map<string, number>();
    branch.set(row.product_id, Math.min(price, branch.get(row.product_id) ?? Infinity));
    branches.set(row.branch_id, branch);
  }
  return { products, branches };
}

export function productName(p: Product) {
  return p.name.replace(/^Демо:\s*/i, "");
}
export function searchText(value: string) {
  const units:Record<string,string>={"кг":"kg","гр":"g","г":"g","мл":"ml","л":"l",kg:"kg",g:"g",ml:"ml",l:"l"};
  return value.normalize("NFKC").toLocaleLowerCase("bg").replace(/,/g,".").replace(/[–—-]/g," ").replace(/(\d)\s*(кг|гр|мл|г|л|kg|ml|g|l)(?=\s|$|[.,;%()])/g,(_,number:string,unit:string)=>number+units[unit]).replace(/\s+/g," ").trim();
}
export function matchesProduct(p: Product, query: string) {
  const text=searchText([productName(p),p.package_quantity == null ? "" : Number(p.package_quantity),p.package_unit].filter(Boolean).join(" "));
  return searchText(query).split(" ").every(token=>text.includes(token));
}
export function filterLocalities<
  T extends {
    name: string;
    name_bg?: string | null;
    name_latin?: string | null;
  },
>(rows: T[], query: string): T[] {
  const normalize = (name: string) =>
    name.trim().toLocaleLowerCase("bg").replace(/ia/g, "ija");
  const q = normalize(query);
  return rows.filter((l) =>
    [l.name, l.name_bg, l.name_latin].some(
      (n) => n && normalize(n).includes(q),
    ),
  );
}
