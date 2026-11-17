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
  require,
  translations,
);
const keys = Object.keys(translations.exports.messages.bg).sort();
assert.equal(translations.exports.languages.length, 6);
for (const value of Object.values(translations.exports.messages))
  assert.deepEqual(Object.keys(value).sort(), keys);
