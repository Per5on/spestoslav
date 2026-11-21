const ts = require("typescript"),
  fs = require("node:fs"),
  assert = require("node:assert/strict");
let saved = null,
  calls = 0,
  fail = false,
  pageCalls = [];
const product = {
  id: "p1",
  name: "Мляко",
  category_code: "groceries",
  price_eur: 999,
  private_token: "never-save",
};
const storage = {
  getItem: async () => saved,
  setItem: async (key, value) => {
    saved = value;
  },
};
const mockApi = {
  API_BASE_URL: "https://simulation.invalid",
  api: async (path) => {
    calls++;
    if (fail) throw new Error("HTTP 503");
    if (path === "/api/v1/catalog/groceries")
      return { schema_version: 1, products: [product] };
    throw new Error("Unexpected path");
  },
};
const code = ts.transpileModule(
  fs.readFileSync("src/catalog/cache.ts", "utf8"),
  { compilerOptions: { module: ts.ModuleKind.CommonJS } },
).outputText;
const m = { exports: {} };
new Function("exports", "require", "module", code)(
  m.exports,
  (name) => (name.includes("async-storage") ? { default: storage } : mockApi),
  m,
);
(async () => {
  const { loadProducts, parseCatalogCache } = m.exports;
  const signal = new AbortController().signal;
  let result = await loadProducts(signal, false, () => {});
  assert.equal(result.cached, false);
  assert.equal(calls, 1);
  assert(!saved.includes("price_eur") && !saved.includes("private_token"));
  result = await loadProducts(signal, false, (rows) =>
    assert.equal(rows.length, 1),
  );
  assert.equal(result.cached, true);
  assert.equal(calls, 1);
  fail = true;
  result = await loadProducts(signal, true, () => {});
  assert.equal(result.cached, true);
  assert.equal(calls, 2);
  const expired = JSON.stringify({
    schema_version: 1,
    saved_at: Date.now() - 8 * 86400000,
    products: [product],
  });
  assert.equal(parseCatalogCache(expired), null);
  assert.equal(parseCatalogCache("{broken"), null);
  assert.equal(
    parseCatalogCache(
      JSON.stringify({
        schema_version: 1,
        saved_at: Date.now(),
        products: [product, product],
      }),
    ),
    null,
  );
  assert.equal(
    parseCatalogCache(
      JSON.stringify({
        schema_version: 1,
        saved_at: Date.now(),
        products: [{ ...product, is_demo: true }],
      }),
    ),
    null,
  );
  assert.equal(
    parseCatalogCache(
      JSON.stringify({
        schema_version: 1,
        saved_at: Date.now() + 86400000,
        products: [product],
      }),
    ),
    null,
  );
  saved = null;
  fail = false;
  mockApi.api = async (path) => {
    if (path.includes("/catalog/")) throw new Error("HTTP 404");
    pageCalls.push(path);
    const offset = Number(
      new URL("https://simulation.invalid" + path).searchParams.get("offset"),
    );
    return Array.from({ length: offset < 1000 ? 100 : 0 }, (_, i) => ({
      ...product,
      id: "p" + (offset + i),
    }));
  };
  result = await loadProducts(signal, true, () => {});
  assert.equal(result.products.length, 1000);
  assert.equal(pageCalls.length, 11);
  assert.equal(result.products[999].id, "p999");
  console.log(
    "Cache checks passed: fresh/offline/forced refresh, metadata only, expiry/corruption/duplicates, complete 1,000-item fallback pagination.",
  );
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
