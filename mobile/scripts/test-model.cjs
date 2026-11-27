const ts = require("typescript");
const fs = require("node:fs");
const assert = require("node:assert/strict");
const source = ts.transpileModule(
  fs.readFileSync("src/catalog/model.ts", "utf8"),
  { compilerOptions: { module: ts.ModuleKind.CommonJS } },
).outputText;
const moduleObject = { exports: {} };
new Function("exports", "require", "module", source)(
  moduleObject.exports,
  require,
  moduleObject,
);
const {
  changeQuantity,
  comparePublishedBasket,
  restoreBasket,
  lowestPrice,
  indexIndicativePrices,
  indexLowestPrices,
  groupFuelResults,
  prioritizePricedProducts,
  matchesProduct,
  duplicateProductQualifiers,
  filterLocalities,
} = moduleObject.exports;
const bananas = [
  { id: "first", category_code: "groceries", name: "БАНАНИ", source_product_code: "81590" },
  { id: "second", category_code: "groceries", name: " банани ", source_product_code: "88590" },
  { id: "bio", category_code: "groceries", name: "БИО БАНАНИ" },
];
const qualifiers = duplicateProductQualifiers([...bananas, bananas[0]]);
assert.deepEqual(
  prioritizePricedProducts(bananas, new Map([["bio", 1.4], ["second", 2.4]])).map(p => p.id),
  ["second", "bio", "first"],
);
assert.equal(prioritizePricedProducts(bananas, new Map()), bananas);
assert.deepEqual([...qualifiers], [["first", "81590"], ["second", "88590"]]);
assert.equal(matchesProduct(bananas[0], "81590", "БАНАНИ · 81590"), true);
assert.equal(matchesProduct(bananas[1], "81590", "БАНАНИ · 88590"), false);
assert.equal(duplicateProductQualifiers([
  { ...bananas[0], barcode: "4006381333931" }, bananas[1],
]).get("first"), "4006381333931");
const refreshTime = Date.parse("2026-11-23T10:00:00Z");
const onlineOffer = {
  product_id: "p1", retailer_code: "local", price_eur: "2.99",
  valid_until: "2026-11-23T12:00:00Z", price_scope: "NATIONAL_ONLINE",
};
assert.deepEqual([...indexIndicativePrices([
  onlineOffer,
  { ...onlineOffer, retailer_code: "other-city", price_eur: "1.01" },
  { ...onlineOffer, valid_until: "2026-11-22T12:00:00Z", price_eur: "0.99" },
], [{ id: "a-local-branch", retailer_code: "local" }], refreshTime).products], [["p1", 2.99]]);
const fuelStores = [
  { id: "fallback", retailer_code: "local", retailer_name: "Local", address: "Fallback street" },
  { id: "same", retailer_code: "local", retailer_name: "Local", address: "Same street" },
  { id: "different", retailer_code: "local", retailer_name: "Local", address: "Different street" },
  { id: "second-chain", retailer_code: "second", retailer_name: "Second", address: "Second street" },
  { id: "unknown", retailer_code: "unknown", retailer_name: "Unknown", address: "Unknown street" },
];
const fuelOffers = indexIndicativePrices([
  onlineOffer, { ...onlineOffer, retailer_code: "second" },
], fuelStores, refreshTime);
const fuelStationPrices = indexLowestPrices([
  { branch_id: "same", product_id: "p1", price_eur: 2.9900 },
  { branch_id: "different", product_id: "p1", price_eur: 2.89 },
  { branch_id: "fallback", product_id: "p1", price_eur: 2.50, expires_at: "2026-11-22T12:00:00Z" },
], fuelStores, refreshTime);
const fuelResults = groupFuelResults(fuelStores, "p1", fuelStationPrices.branches, fuelOffers.chains);
assert.deepEqual(fuelResults.map(row => [row.name, row.branchCount, row.stations.map(({store, price}) => [store.address, price])]), [
  ["Local", 2, [["Different street", 2.89]]],
  ["Second", 1, []],
  ["Unknown", 0, [["Unknown street", undefined]]],
]);
assert.equal(groupFuelResults(fuelStores, "another-fuel", fuelStationPrices.branches, fuelOffers.chains).length, 5);
assert.equal(groupFuelResults([], "p1", fuelStationPrices.branches, fuelOffers.chains).length, 0);
const p = { id: "p1", name: "Мляко", category_code: "groceries" };
let basket = changeQuantity([], p, 1);
basket = changeQuantity(basket, p, 1);
assert.equal(basket[0].quantity, 2);
assert.equal(changeQuantity(basket, p, -2).length, 0);
assert.equal(
  changeQuantity([{ product: p, quantity: 99 }], p, 1)[0].quantity,
  99,
);
assert.deepEqual(
  restoreBasket([
    { product: p, quantity: 2 },
    { product: p, quantity: 3 },
    { product: p, quantity: -1 },
  ]),
  [{ product: p, quantity: 2 }],
);
const stores = [{ id: "s1" }];
const prices = [
  { product_id: "p1", branch_id: "s1", price_eur: 2, expires_at: "2099-01-01" },
  { product_id: "p1", branch_id: "other-city", price_eur: 1 },
  {
    product_id: "p1",
    branch_id: "s1",
    price_eur: 0.5,
    expires_at: "2020-01-01",
  },
];
assert.equal(lowestPrice(p, prices, stores), 2);
assert.equal(lowestPrice({ ...p, is_demo: true }, prices, stores), null);
assert.equal(lowestPrice(p, prices, []), null);
assert.equal(
  matchesProduct({ ...p, name: "Демо: прясно мляко" }, " МЛЯКО "),
  true,
);
const cities = [
  { name: "Sofia", name_bg: "София" },
  { name: "Varna", name_bg: "Варна" },
];
assert.equal(filterLocalities(cities, "100").length, 0);
assert.equal(filterLocalities(cities, "СОФ")[0].name_bg, "София");
assert.equal(filterLocalities(cities, "1000").length, 0);
console.log(
  "Model checks passed: basket restoration/quantity bounds, demo and locality price isolation, expiry, name-only search.",
);

assert.equal(
  filterLocalities(
    [
      {
        name: "Sofija",
        name_bg: "София",
        name_latin: "Sofija",
      },
    ],
    "Sofia",
  ).length,
  1,
);
const full = Array.from({ length: 100 }, (_, i) => ({
  product: { ...p, id: `p-${i}` },
  quantity: 1,
}));
assert.equal(changeQuantity(full, p, 1).length, 100);
assert.equal(changeQuantity(full, full[0].product, 1)[0].quantity, 2);

// Reproduce prototype poisoning through both merge arguments, including null-prototype targets.
const merge = require("deepmerge");
for (const [target, source] of [
  [JSON.parse('{"__proto__":{"polluted":true}}'), {}],
  [Object.create(null), JSON.parse('{"__proto__":{"polluted":true}}')],
  [{}, JSON.parse('{"constructor":{"prototype":{"polluted":true}}}')],
]) {
  const result = merge(target, source);
  assert.equal(Object.getPrototypeOf(result), Object.prototype);
  assert.equal(result.polluted, undefined);
  assert.equal(Object.prototype.polluted, undefined);
}
assert.deepEqual(
  merge({ nested: { a: 1 }, list: [1] }, { nested: { b: 2 }, list: [2] }),
  { nested: { a: 1, b: 2 }, list: [1, 2] },
);
console.log(
  "Dependency regression checks passed: safe deep merges and ordinary config merging.",
);

assert.deepEqual(
  restoreBasket([{ product: { ...p, category_code: "home" }, quantity: 1 }]),
  [],
);
const i18nSource = ts.transpileModule(fs.readFileSync("src/i18n.ts", "utf8"), {
  compilerOptions: { module: ts.ModuleKind.CommonJS },
}).outputText;
const translations = { exports: {} };
new Function("exports", "require", "module", i18nSource)(
  translations.exports,
  (name) =>
    name === "./workflows/messages"
      ? loadTS("src/workflows/messages.ts")
      : name === "./experienceMessages" ? loadTS("src/experienceMessages.ts") : require(name),
  translations,
);
const keys = Object.keys(translations.exports.messages.bg).sort();
assert.equal(translations.exports.languages.length, 6);
for (const value of Object.values(translations.exports.messages))
  assert.deepEqual(Object.keys(value).sort(), keys);

function loadTS(path, dependencies = {}) {
  const code = ts.transpileModule(fs.readFileSync(path, "utf8"), {
    compilerOptions: { module: ts.ModuleKind.CommonJS },
  }).outputText;
  const m = { exports: {} };
  new Function("exports", "require", "module", code)(
    m.exports,
    (name) => (name in dependencies ? dependencies[name] : require(name)),
    m,
  );
  return m.exports;
}
const { validGTIN, scannedGTIN } = loadTS("src/workflows/barcode.ts");
for (const value of [
  "4006381333931",
  "96385074",
  "012345678905",
  "04006381333931",
])
  assert.equal(validGTIN(value), true, value);
for (const value of [
  "4006381333932",
  "12345",
  "1234567890",
  "https://example.com",
  "3800000000000",
])
  assert.equal(validGTIN(value), false, value);
assert.equal(scannedGTIN("4006381333931", "qr"), null);
assert.equal(scannedGTIN("4006381333931", "ean13"), "4006381333931");
console.log(
  "Barcode checks passed: GTIN lengths/check digits, leading zeroes and rejected QR/PLU.",
);
assert(matchesProduct({id:'yogurt',name:'КИСЕЛО КРАВЕ МЛЯКО 3,6% 400ГР',category_code:'groceries'},'кисело мляко 400 г'));
assert(matchesProduct({id:'milk',name:'Мляко',category_code:'groceries',package_quantity:'1.000',package_unit:'l'},'мляко 1л'));
assert(!matchesProduct({id:'milk',name:'Мляко 2% 1Л',category_code:'groceries'},'мляко 3.6%'));
console.log('Search checks passed: reordered words, Cyrillic/Latin units, separated quantities and decimal fat content.');

const fontModule = { exports: {} };
new Function("exports", ts.transpileModule(fs.readFileSync("src/font.ts", "utf8"), { compilerOptions: { module: ts.ModuleKind.CommonJS } }).outputText)(fontModule.exports);
for (const scale of [0.9, 1, 1.15, 1.3]) {
  for (const base of [10, 13, 14, 16, 20, 28]) {
    assert.equal(fontModule.exports.appFontSize(base, scale, 11), Math.max(11, base * scale) + 1);
  }
}
console.log("Font settings: actual text +1pt at every saved scale; minimum readable size retained.");


// Published values are independent of location. A comparison uses the town
// only for eligibility, deduplicates chains and retains four decimal places.
const sourceOffer = (product_id, retailer_code, price_eur, valid_until = "2026-11-24T12:00:00Z") => ({
  product_id, retailer_code, price_eur, valid_until, price_scope: "NATIONAL_ONLINE",
});
const sold = [
  sourceOffer("first", "outside", "0.1000"),
  sourceOffer("first", "local", "1.3333"), sourceOffer("second", "local", "0.0100"),
  sourceOffer("first", "partial", "0.5000"),
  sourceOffer("second", "partial", "0.0001", "2026-11-22T00:00:00Z"),
];
const local = [
  { retailer_code: "local", retailer_name: "Local" },
  { retailer_code: "local", retailer_name: "Local" },
  { retailer_code: "partial", retailer_name: "Partial" },
];
const basketForComparison = [
  { product: bananas[0], quantity: 3 }, { product: bananas[1], quantity: 1 },
];
const compared = comparePublishedBasket(basketForComparison, sold, local, refreshTime);
assert.equal(indexIndicativePrices(sold, undefined, refreshTime).products.get("first"), 0.1);
assert.deepEqual(compared.quotes.map(q => q.retailer_code), ["local", "partial"]);
assert.equal(compared.cheapest.total_eur, "4.0099");
assert.equal(compared.quotes[0].items[0].subtotal_eur, "3.9999");
assert.equal(compared.quotes[1].total_eur, null);

// Change the branches and eligible chains while reusing the same published feed.
const anotherTown = comparePublishedBasket(basketForComparison, sold, [
  { retailer_code: "local", retailer_name: "Local", address: "Different branch" },
  { retailer_code: "outside", retailer_name: "Outside" },
], refreshTime);
assert.deepEqual(anotherTown.quotes.map(q => q.retailer_code), ["local", "outside"]);
assert.deepEqual(anotherTown.quotes[0], compared.quotes[0]);
assert.equal(anotherTown.quotes[1].items[0].unit_price_eur, "0.1000");
