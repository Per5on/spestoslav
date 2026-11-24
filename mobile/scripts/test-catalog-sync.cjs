const assert = require("node:assert/strict");
const fs = require("node:fs");
const ts = require("typescript");

function load(name, dependencies) {
  const code = ts.transpileModule(fs.readFileSync("src/catalog/" + name + ".ts", "utf8"), {
    compilerOptions: { module: ts.ModuleKind.CommonJS },
  }).outputText;
  const exports = {};
  new Function("exports", "require", code)(exports, name => dependencies[name]);
  return exports;
}

const saved = new Map();
const storage = {
  getItem: async key => saved.get(key) ?? null,
  setItem: async (key, value) => saved.set(key, value),
  removeItem: async key => saved.delete(key),
  multiRemove: async keys => keys.forEach(key => saved.delete(key)),
};
const storageModule = { default: storage };
const scope = { category: "fuel", localityId: "sofia" };
const price = {
  product_id: "a95", branch_id: "sofia-1", price_eur: 1.31, verified_at: new Date().toISOString(),
  expires_at: new Date(Date.now() + 60000).toISOString(),
};
const offer = {
  product_id: "a95", retailer_code: "chain", price_eur: "1.31",
  valid_until: price.expires_at, price_scope: "NATIONAL_ONLINE",
};
const station = { id: "sofia-1", address: "Test address", retailer_name: "Test", retailer_code: "chain" };
const paths = [];
let fetchResult = async path => path.includes("stores?") ? [station] :
  path.includes("national-offers?") ? [offer] : [price];
const mockApi = {
  API_BASE_URL: "https://fixture.invalid",
  httpStatus: error => error.status ?? null,
  api: async path => {
    paths.push(path);
    if (path.startsWith("/api/v1/fuel-snapshot?")) throw Object.assign(new Error("HTTP 404"), { status: 404 });
    return fetchResult(path);
  },
};
const modules = { "@react-native-async-storage/async-storage": storageModule, "../api": mockApi };
const catalogue = load("catalogData", { ...modules, "./cache": load("cache", modules) });

(async () => {
  const signal = new AbortController().signal;
  const { pricesResource, storesResource, onlineResource, clearLocalCatalogs } = catalogue;
  await pricesResource.load(scope, signal);
  await storesResource.load(scope, signal);
  await onlineResource.load(scope, signal);

  let cached;
  let respond;
  fetchResult = () => new Promise(resolve => { respond = resolve; });
  const before = paths.length;
  const first = pricesResource.load(scope, signal, true, rows => { cached = rows; });
  const second = pricesResource.load(scope, signal, true);
  await new Promise(resolve => setImmediate(resolve));
  assert.deepEqual(cached, [price]);
  assert.equal(paths.length - before, 1);
  const replacement = { ...price, price_eur: 1.43 };
  respond([replacement]);
  assert.deepEqual(await Promise.all([first, second]), [[replacement], [replacement]]);

  fetchResult = async () => { throw new Error("Server unreachable"); };
  cached = undefined;
  await assert.rejects(pricesResource.load({ ...scope, localityId: "plovdiv" }, signal, false,
    rows => { cached = rows; }), /unreachable/);
  assert.equal(cached, undefined);

  await assert.rejects(pricesResource.load(scope, signal, true, rows => { cached = rows; }), /unreachable/);
  assert.deepEqual(cached, [replacement]);
  const onlineKey = Array.from(saved.keys()).find(key => key.endsWith(":online:fuel"));
  const expired = JSON.parse(saved.get(onlineKey));
  expired.rows[0].valid_until = "2020-01-01";
  saved.set(onlineKey, JSON.stringify(expired));
  await assert.rejects(onlineResource.load(scope, signal, false, rows => { cached = rows; }), /unreachable/);
  assert.deepEqual(cached, []);

  await clearLocalCatalogs();
  assert.equal(saved.size, 0);

  let task;
  let registered;
  const product = { id: "a95", name: "A95", category_code: "fuel", fuel_type: "petrol" };
  saved.set("saved-locality", JSON.stringify({ locality: { id: "sofia" } }));
  fetchResult = async path => {
    if (path.includes("products?")) return [product];
    if (path.includes("/catalog/")) return { schema_version: 1, products: [] };
    if (path.includes("stores?")) return [station];
    return path.includes("national-offers?") ? [offer] : [price];
  };
  const background = load("backgroundSync", {
    ...modules, "react-native": { Platform: { OS: "android" } },
    "expo-task-manager": {
      defineTask: (_name, perform) => { task = perform; },
      isAvailableAsync: async () => true,
      isTaskRegisteredAsync: async () => Boolean(registered),
    },
    "expo-background-task": {
      getStatusAsync: async () => 2, BackgroundTaskStatus: { Available: 2 },
      BackgroundTaskResult: { Success: 1, Failed: 2 },
      registerTaskAsync: async (name, options) => { registered = { name, ...options }; },
    },
    "../localData": { savedListKey: "saved-locality" }, "./catalogData": catalogue,
  });
  await background.enableCatalogSync();
  assert.deepEqual(registered, { name: "spestovnik-catalog-sync", minimumInterval: 60 });
  paths.length = 0;
  assert.equal(await task(), 1);
  assert.equal(paths.length, 12);
  assert.equal(paths.filter(path => path.includes("locality_id=sofia")).length, 9);
  assert(Array.from(saved.values()).some(value => value.includes('"fuel_type":"petrol"')));
  console.log("Catalogue sync checks passed: scoped first paint, shared reads, outage fallback, offer expiry, local reset and scheduled Android task.");
})().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
