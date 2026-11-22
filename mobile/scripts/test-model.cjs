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
  restoreBasket,
  lowestPrice,
  matchesProduct,
  filterLocalities,
} = moduleObject.exports;
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
// Directory search must use its own localized prompt, not the product search prompt.
const directoryScreen = fs.readFileSync("src/catalog/MerchantDirectoryScreen.tsx", "utf8");
assert.match(directoryScreen, /accessibilityLabel=\\{t\\("searchMerchant"\\)\\}/);
assert.match(directoryScreen, /placeholder=\\{t\\("searchMerchant"\\)\\}/);
for (const language of translations.exports.languages) {
  const labels = translations.exports.messages[language.code];
  assert.ok(labels.searchMerchant.trim(), `Missing merchant search prompt: ${language.code}`);
  assert.notEqual(labels.searchMerchant, labels.searchProduct);
}


function loadTS(path, dependencies = {}) {
  const code = ts.transpileModule(fs.readFileSync(path, "utf8"), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2018 },
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

const merchantDirectory = loadTS("src/catalog/merchantDirectory.ts", { "../api": { api: () => { throw new Error("Network must not be used by local filtering"); } } });
const merchantRows = [
  { id: "1", category_code: "groceries", retailer_code: "market", retailer_name: "Магазин", branch_name: null, address: "ул. Главна 1", locality_name: "София", municipality: "Столична", region: "София" },
  { id: "2", category_code: "fuel", retailer_code: "fuel", retailer_name: "Бензиностанция", branch_name: "Център", address: "бул. България 5", locality_name: "Варна", municipality: null, region: null },
];
assert.deepEqual(merchantDirectory.filterMerchantDirectory(merchantRows, "  "), merchantRows);
assert.deepEqual(merchantDirectory.filterMerchantDirectory(merchantRows, "СОФИЯ магазин").map(x => x.id), ["1"]);
assert.deepEqual(merchantDirectory.filterMerchantDirectory(merchantRows, "Варна ЦЕНТЪР").map(x => x.id), ["2"]);
assert.deepEqual(merchantDirectory.filterMerchantDirectory(merchantRows, "несъществуващ"), []);
assert.deepEqual(merchantDirectory.filterMerchantDirectory(merchantRows, "Варна, ЦЕНТЪР").map(x => x.id), ["2"]);
assert.deepEqual(merchantDirectory.filterMerchantDirectory(merchantRows, "ул Главна").map(x => x.id), ["1"]);
assert.deepEqual(merchantDirectory.filterMerchantDirectory(merchantRows, "София—Магазин").map(x => x.id), ["1"]);
assert.deepEqual(merchantDirectory.filterMerchantDirectory(merchantRows, "„Магазин“").map(x => x.id), ["1"]);
assert.deepEqual(merchantDirectory.filterMerchantDirectory(merchantRows, "ул. № Главна").map(x => x.id), ["1"]);
assert.deepEqual(merchantDirectory.filterMerchantDirectory(merchantRows, "‘Център’").map(x => x.id), ["2"]);
console.log("Merchant directory checks passed: empty query, mixed fields, case folding, no synthetic results.");

// Grouping must not reorder the caller's cached branch records.
const unsortedMerchantRows = [
  { ...merchantRows[1], id: "z", locality_id: "varna", retailer_name: "Zeta" },
  { ...merchantRows[1], id: "a", locality_id: "varna", retailer_name: "Alpha" },
];
const originalMerchantOrder = unsortedMerchantRows.map(row => row.id);
const merchantGroups = merchantDirectory.groupMerchantDirectory(unsortedMerchantRows);
assert.deepEqual(merchantGroups[0].localities[0].branches.map(row => row.id), ["a", "z"]);
assert.deepEqual(unsortedMerchantRows.map(row => row.id), originalMerchantOrder);
assert.deepEqual(merchantDirectory.groupMerchantDirectory(unsortedMerchantRows)[0].localities[0].branches.map(row => row.id), ["a", "z"]);
console.log("Merchant directory grouping checks passed: stable sorted display without input mutation.");


// Canonical locality identity must not collapse homonymous towns, and
// identical locality IDs in different categories must remain separate.
const homonymousMerchantRows = [
  { ...merchantRows[0], id: "town-a", locality_id: "locality-a", locality_name: "Ново село", category_code: "groceries" },
  { ...merchantRows[0], id: "town-b", locality_id: "locality-b", locality_name: "Ново село", category_code: "groceries" },
  { ...merchantRows[1], id: "town-fuel", locality_id: "locality-a", locality_name: "Ново село", category_code: "fuel" },
];
const homonymousGroups = merchantDirectory.groupMerchantDirectory(homonymousMerchantRows);
const foodGroup = homonymousGroups.find(group => group.category_code === "groceries");
const fuelGroup = homonymousGroups.find(group => group.category_code === "fuel");
assert.deepEqual(foodGroup.localities.map(locality => locality.locality_id), ["locality-a", "locality-b"]);
assert.deepEqual(foodGroup.localities.map(locality => locality.branches.map(branch => branch.id)), [["town-a"], ["town-b"]]);
assert.deepEqual(fuelGroup.localities.map(locality => locality.branches.map(branch => branch.id)), [["town-fuel"]]);
assert.deepEqual(homonymousMerchantRows.map(row => row.id), ["town-a", "town-b", "town-fuel"]);
console.log("Merchant locality identity checks passed: homonymous localities and category isolation.");

// Search normalization must not mutate source records, and punctuation-only
// queries must behave like an empty search rather than hide all merchants.
const merchantRowsSnapshot = JSON.stringify(merchantRows);
assert.deepEqual(merchantDirectory.filterMerchantDirectory(merchantRows, "„“ № — /"), merchantRows);
assert.deepEqual(merchantDirectory.filterMerchantDirectory(merchantRows, "СОФИЯ / ул. № Главна").map(row => row.id), ["1"]);
assert.deepEqual(merchantDirectory.filterMerchantDirectory(merchantRows, "БЪЛГАРИЯ").map(row => row.id), ["2"]);
assert.equal(JSON.stringify(merchantRows), merchantRowsSnapshot);
console.log("Merchant search regressions passed: punctuation-only input, compound address, immutable records.");


// Search must cover category, municipality, region and retailer code without
// changing the order or contents of the verified branch rows.
const geographicMerchantRows = [
  { ...merchantRows[0], id: "regional", retailer_code: "regional-chain", municipality: "Родопи", region: "Пловдив" },
  { ...merchantRows[1], id: "station", retailer_code: "fuel-network", municipality: "Варна", region: "Варна" },
];
const geographicSnapshot = JSON.stringify(geographicMerchantRows);
assert.deepEqual(merchantDirectory.filterMerchantDirectory(geographicMerchantRows, "РОДОПИ Пловдив").map(row => row.id), ["regional"]);
assert.deepEqual(merchantDirectory.filterMerchantDirectory(geographicMerchantRows, "fuel fuel-network").map(row => row.id), ["station"]);
assert.deepEqual(merchantDirectory.filterMerchantDirectory(geographicMerchantRows, "regional-chain София").map(row => row.id), ["regional"]);
assert.deepEqual(merchantDirectory.filterMerchantDirectory(geographicMerchantRows, "fuel Родопи"), []);
assert.equal(JSON.stringify(geographicMerchantRows), geographicSnapshot);
console.log("Merchant geographic/category search checks passed: municipality, region, category, retailer code, immutable source.");

// Homonymous localities must show their municipality/region to avoid ambiguous navigation.
assert.equal(merchantDirectory.merchantLocalityLabel({ locality_name: "Ново село", municipality: "Родопи", region: "Пловдив" }), "Ново село · Родопи · Пловдив");
assert.equal(merchantDirectory.merchantLocalityLabel({ locality_name: "София", municipality: " София ", region: "София" }), "София");
assert.equal(merchantDirectory.merchantLocalityLabel({ locality_name: "Варна", municipality: null, region: null }), "Варна");
assert.equal(merchantDirectory.merchantLocalityLabel({ locality_name: "Ново село", municipality: "  Община   Родопи  ", region: " Област  Пловдив " }), "Ново село · Община Родопи · Област Пловдив");
assert.equal(merchantDirectory.merchantLocalityLabel({ locality_name: "  Ново   село  ", municipality: "Ново село", region: " Пловдив " }), "Ново село · Пловдив");
assert.equal(merchantDirectory.merchantLocalityLabel({ locality_name: "  София  ", municipality: " София ", region: null }), "София");
console.log("Merchant locality labels passed: geographic disambiguation and duplicate suppression.");

// Geographic details may be absent from the first branch of a locality.
// Grouping should use verified details from another branch without changing records.
const incompleteLocalityRows = [
  { ...merchantRows[0], id: "first", locality_id: "same-place", municipality: null, region: " " },
  { ...merchantRows[0], id: "second", locality_id: "same-place", municipality: "Родопи", region: "Пловдив" },
];
const incompleteSnapshot = JSON.stringify(incompleteLocalityRows);
const enrichedLocality = merchantDirectory.groupMerchantDirectory(incompleteLocalityRows)[0].localities[0];
assert.equal(enrichedLocality.municipality, "Родопи");
assert.equal(enrichedLocality.region, "Пловдив");
assert.equal(enrichedLocality.branches.length, 2);
assert.equal(JSON.stringify(incompleteLocalityRows), incompleteSnapshot);
console.log("Merchant locality metadata checks passed: later verified branch fills missing details without mutation.");

// Retailer names may contain ampersands or plus signs; queries with spaces
// should still match those verified names without rewriting source records.
const symbolMerchantRows = [
  { ...merchantRows[0], id: "ampersand", retailer_name: "A&B Market" },
  { ...merchantRows[1], id: "plus", retailer_name: "Fuel+Go" },
];
const symbolSnapshot = JSON.stringify(symbolMerchantRows);
assert.deepEqual(merchantDirectory.filterMerchantDirectory(symbolMerchantRows, "A B Market").map(row => row.id), ["ampersand"]);
assert.deepEqual(merchantDirectory.filterMerchantDirectory(symbolMerchantRows, "Fuel Go").map(row => row.id), ["plus"]);
assert.deepEqual(merchantDirectory.filterMerchantDirectory(symbolMerchantRows, "A&B").map(row => row.id), ["ampersand"]);
assert.equal(JSON.stringify(symbolMerchantRows), symbolSnapshot);
console.log("Merchant symbol search checks passed: ampersand/plus separators and immutable verified records.");

