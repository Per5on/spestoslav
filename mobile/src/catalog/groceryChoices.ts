import type { ComparableOffer, Product } from "./model";

const prefix = "grocery-choice:";
export const isGroceryChoice = (product: Product) => product.id.startsWith(prefix);

const units: Record<string, string> = {
  кг: "кг", kg: "кг", гр: "г", г: "г", g: "г", мл: "мл", ml: "мл",
  л: "л", l: "л", бр: "бр.", pcs: "бр.", unit: "бр.", units: "бр.",
};

function measure(product: Product) {
  // A multipack total does not make it equivalent to a single package.
  if (/\d\s*[xх×]\s*\d/iu.test(product.name)) return;
  const quantity = Number(product.package_quantity);
  const unit = units[(product.package_unit ?? "").toLowerCase().replace(/\.$/, "")];
  if (quantity > 0 && Number.isFinite(quantity) && unit) return [quantity, unit] as const;

  for (const text of [product.package, product.name, product.source_category]) {
    if (!text) continue;
    const amounts = Array.from(text.toLowerCase().matchAll(
      /(\d+(?:[.,]\d+)?)\s*(кг|kg|гр|г|g|мл|ml|л|l|бр|pcs)(?![а-яa-z])/gu,
    ));
    if (amounts.length > 1) return;
    if (amounts.length === 1) {
      const [, amount, foundUnit] = amounts[0];
      return [Number(amount.replace(",", ".")), units[foundUnit]] as const;
    }
  }
}

function family(product: Product) {
  const source = product.source_category?.trim() ?? "";
  const name = product.name;
  const amount = measure(product);
  if (!amount) return;
  let label = "";
  if (/^банани(?:\s|$)/iu.test(source) || /^(?:(?:био|малки|мини|дребни|органични)\s+)*банани(?=$|[^\p{L}])/iu.test(name)) {
    label = "Банани";
  } else if (/^яйца(?:\s|$)/iu.test(name)) {
    const size = /(?:^|\s)(?:размер\s+)?(xl|l|m|м|s|с)(?=\s|$)/iu.exec(name)?.[1]?.toUpperCase();
    if (size && amount[1] === "бр.") label = "Яйца размер " + ({ М: "M", С: "S" }[size] ?? size);
  } else if (source && !/^(?:Каша|Колбаси|Риба|Чай|Адаптирани млека|Минерална вода|Спагети)/iu.test(source)) {
    label = source.split(/\s+(?:от\s+(?=\d)|за\s+(?=\d)|\d+[.,]?\d*\s*(?:кг|гр|г|мл|л)(?![а-я]))/u)[0]
      .replace(/[,\s]+$/u, "");
    // Keep percentages in dairy and other groceries where the label alone lacks them.
    const strength = name.match(/\d+(?:[.,]\d+)?\s*%/u)?.[0];
    if (strength) label += " " + strength.replace(/\s+/g, "").replace(",", ".");
  }
  if (!label) return;
  const [quantity, unit] = amount;
  const canonicalAmount = unit === "кг" || unit === "л" ? quantity * 1000 : quantity;
  const canonicalUnit = unit === "кг" ? "г" : unit === "л" ? "мл" : unit;
  return {
    key: JSON.stringify([label, product.group_code, canonicalAmount, canonicalUnit]),
    label,
    package: `${quantity} ${unit}`,
  };
}

export function groupGroceryChoices(products: Product[], offers: ComparableOffer[], now = Date.now()) {
  const definitions = new Map(products.flatMap(product => {
    if (product.category_code !== "groceries" || product.is_demo) return [];
    const match = family(product);
    if (!match) return [];
    const variant = JSON.stringify([match.key, product.name.normalize("NFKC").toLowerCase().trim().replace(/\s+/g, " ")]);
    return [[product.id, { ...match, variant }] as const];
  }));
  const retailers = new Map<string, Set<string>>();
  for (const offer of offers) {
    const match = definitions.get(offer.product_id);
    if (!match || !(Date.parse(offer.valid_until) > now) ||
        !Number.isFinite(Number(offer.price_eur)) || Number(offer.price_eur) <= 0) continue;
    const chains = retailers.get(match.variant) ?? new Set<string>();
    chains.add(offer.retailer_code);
    retailers.set(match.variant, chains);
  }

  const choices = new Map<string, Product>();
  const aliases = new Map<string, string>();
  const visible = products.flatMap(product => {
    const match = definitions.get(product.id);
    if (!match || (retailers.get(match.variant)?.size ?? 0) > 2) return [product];
    const id = prefix + match.key;
    aliases.set(product.id, id);
    const existing = choices.get(id);
    if (existing) {
      existing.groceryAliases?.push(product.name, product.source_product_code ?? "");
      return [];
    }
    const choice: Product = {
      ...product, id, name: match.label, package: match.package,
      barcode: undefined, identityQualifier: undefined, groceryAliases: [product.name, product.source_product_code ?? ""],
    };
    choices.set(id, choice);
    return [choice];
  });

  const groupedOffers = offers.flatMap(offer => {
    const id = aliases.get(offer.product_id);
    return id ? [{ ...offer, product_id: id }] : [];
  });
  return { products: visible, offers: [...offers, ...groupedOffers] };
}
