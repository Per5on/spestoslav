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
  { name: "Sofia", name_bg: "София", postal_codes: ["1000"] },
  { name: "Varna", name_bg: "Варна", postal_codes: ["9000"] },
];
assert.equal(filterLocalities(cities, "100", "postal")[0].name_bg, "София");
assert.equal(filterLocalities(cities, "СОФ", "name")[0].name_bg, "София");
assert.equal(filterLocalities(cities, "1000", "name").length, 0);
console.log(
  "Model checks passed: basket restoration/quantity bounds, demo and locality price isolation, expiry, search modes.",
);
