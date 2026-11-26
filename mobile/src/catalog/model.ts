export type Retailer = { code: string; name: string; category_code: string; website_url?: string | null };
export type Product = {
  id: string;
  name: string;
  category_code: string;
  brand?: string | null;
  barcode?: string | null;
  identityQualifier?: string;
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
  retailer_code?: string;
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
export type OnlinePrice = {
  product_id: string;
  retailer_code: string;
  price_eur: string;
  valid_until: string;
  source_reference?: string;
  price_scope: "NATIONAL_ONLINE";
};

export function indexIndicativePrices(offers: OnlinePrice[], stores?: Store[], now = Date.now()) {
  const retailers = stores && new Set(stores.map(store => store.retailer_code));
  const products = new Map<string, number>();
  const chains = new Map<string, Map<string, OnlinePrice>>();
  for (const row of offers) {
    const price = Number(row.price_eur);
    if (row.price_scope !== "NATIONAL_ONLINE" || (retailers && !retailers.has(row.retailer_code)) ||
        !Number.isFinite(price) || price <= 0 || !(Date.parse(row.valid_until) > now)) continue;
    products.set(row.product_id, Math.min(price, products.get(row.product_id) ?? Infinity));
    const chain = chains.get(row.retailer_code) ?? new Map<string, OnlinePrice>();
    const previous = chain.get(row.product_id);
    if (!previous || price < Number(previous.price_eur)) chain.set(row.product_id, row);
    chains.set(row.retailer_code, chain);
  }
  return { products, chains };
}

type OnlineQuoteItem = {
  product_id: string;
  quantity: number;
  unit_price_eur: string | null;
  subtotal_eur: string | null;
};
type OnlineQuote = {
  retailer_code: string;
  retailer_name: string;
  complete: boolean;
  total_eur: string | null;
  items: OnlineQuoteItem[];
};
export type Comparison = { quotes: OnlineQuote[]; cheapest: OnlineQuote | null; quoted_at: string };

export function comparePublishedBasket(basket: BasketItem[], offers: OnlinePrice[], localStores: Store[], now = Date.now()): Comparison {
  const { chains } = indexIndicativePrices(offers, localStores, now);
  const names = new Map(localStores.map(store => [store.retailer_code, store.retailer_name]));
  // National offers have at most four decimal places. Multiply in integer
  // units so each line and basket total preserve the published amount.
  const scale = BigInt(10000);
  const toEUR = (amount: bigint) => `${amount / scale}.${String(amount % scale).padStart(4, "0")}`;
  const candidates = Array.from(chains, ([retailer_code, retailerOffers]) => {
    let total = BigInt(0);
    let complete = true;
    let priced = false;
    const items = basket.map(({ product, quantity }) => {
      const offer = retailerOffers.get(product.id);
      const match = offer && /^(\d{1,8})(?:\.(\d{1,4}))?$/.exec(offer.price_eur);
      if (!match) {
        complete = false;
        return { product_id: product.id, quantity, unit_price_eur: null, subtotal_eur: null };
      }
      priced = true;
      const amount = BigInt(match[1]) * scale + BigInt((match[2] ?? "").padEnd(4, "0"));
      const subtotal = amount * BigInt(quantity);
      total += subtotal;
      return {
        product_id: product.id, quantity, unit_price_eur: toEUR(amount),
        subtotal_eur: toEUR(subtotal),
      };
    });
    const quote: OnlineQuote = {
      retailer_code, retailer_name: names.get(retailer_code) ?? retailer_code, complete,
      total_eur: complete ? toEUR(total) : null, items,
    };
    return { total, quote, priced };
  });
  const quotes = candidates.filter(row => row.priced).sort((a, b) => {
    if (a.quote.complete !== b.quote.complete) return a.quote.complete ? -1 : 1;
    if (a.quote.complete && a.total !== b.total) return a.total < b.total ? -1 : 1;
    return a.quote.retailer_code.localeCompare(b.quote.retailer_code);
  }).map(row => row.quote);
  return { quotes, cheapest: quotes[0]?.complete ? quotes[0] : null, quoted_at: new Date(now).toISOString() };
}

export function groupFuelResults(
  stores: Store[],
  productId: string | undefined,
  branchPrices: ReadonlyMap<string, ReadonlyMap<string, number>>,
  chainPrices: ReadonlyMap<string, ReadonlyMap<string, OnlinePrice>>,
) {
  type FuelResult = {
    key: string;
    name: string;
    estimate?: OnlinePrice;
    branchCount: number;
    stations: { store: Store; price: number | undefined }[];
  };
  const results = new Map<string, FuelResult>();
  for (const store of stores) {
    const price = productId ? branchPrices.get(store.id)?.get(productId) : undefined;
    const estimate = productId && store.retailer_code
      ? chainPrices.get(store.retailer_code)?.get(productId)
      : undefined;
    const key = estimate ? `chain:${estimate.retailer_code}` : `station:${store.id}`;
    const result = results.get(key) ?? {
      key, name: store.retailer_name, estimate, branchCount: 0, stations: [],
    };
    if (estimate && (price === undefined || price.toFixed(2) === Number(estimate.price_eur).toFixed(2))) {
      result.branchCount += 1;
    } else {
      result.stations.push({ store, price });
    }
    results.set(key, result);
  }
  return Array.from(results.values());
}

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

export function prioritizePricedProducts(
  products: Product[],
  published: ReadonlyMap<string, number>,
) {
  if (!published.size) return products;
  const priced: Product[] = [];
  const remaining: Product[] = [];
  for (const product of products) {
    const available = !product.is_demo && published.has(product.id);
    (available ? priced : remaining).push(product);
  }
  return [...priced, ...remaining];
}

export function productName(p: Product) {
  return p.name.replace(/^Демо:\s*/i, "");
}
export function duplicateProductQualifiers(products: Product[]) {
  const groups = new Map<string, Map<string, Product>>();
  for (const product of products) {
    const key = `${product.category_code}:${productName(product).normalize("NFKC").trim().replace(/\s+/g, " ").toLowerCase()}`;
    const group = groups.get(key) ?? new Map<string, Product>();
    group.set(product.id, product);
    groups.set(key, group);
  }
  const qualifiers = new Map<string, string>();
  for (const group of Array.from(groups.values())) {
    if (group.size < 2) continue;
    const rows = Array.from(group.values());
    const details = rows.map(product => [
      product.brand,
      product.package || [product.package_quantity, product.package_unit].filter(Boolean).join(" "),
    ].filter(Boolean).join(" · "));
    const barcodes = rows.map(product => product.barcode);
    const codes = rows.map(product => product.source_product_code);
    rows.forEach((product, index) => {
      const detail = details[index];
      const barcode = barcodes[index];
      const code = codes[index];
      const qualifier = detail && details.indexOf(detail) === details.lastIndexOf(detail)
        ? detail
        : barcode && barcodes.indexOf(barcode) === barcodes.lastIndexOf(barcode)
          ? barcode
          : code && codes.indexOf(code) === codes.lastIndexOf(code)
            ? code
            : product.id;
      qualifiers.set(product.id, qualifier);
    });
  }
  return qualifiers;
}

const units: Record<string, string> = {
  "кг": "kg", "гр": "g", "г": "g", "мл": "ml", "л": "l", kg: "kg", g: "g", ml: "ml", l: "l",
};

export function searchText(value: string) {
  return value.normalize("NFKC").toLocaleLowerCase("bg").replace(/,/g,".").replace(/[–—-]/g," ").replace(/(\d)\s*(кг|гр|мл|г|л|kg|ml|g|l)(?=\s|$|[.,;%()])/g,(_,number:string,unit:string)=>number+units[unit]).replace(/\s+/g," ").trim();
}
export function productSearchText(p: Product, name = productName(p)) {
  return searchText([
    name, p.package_quantity == null ? "" : Number(p.package_quantity), p.package_unit,
  ].filter(Boolean).join(" "));
}

export function matchesSearchText(text: string, tokens: string[]) {
  return tokens.every(token => text.includes(token));
}

export function matchesProduct(p: Product, query: string, name = productName(p)) {
  return matchesSearchText(productSearchText(p, name), searchText(query).split(" "));
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
