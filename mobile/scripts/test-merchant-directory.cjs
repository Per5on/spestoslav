// Merchant-directory pagination regression tests; no network or Android build required.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const ts = require("typescript");

const source = fs.readFileSync(path.join(__dirname, "../src/catalog/merchantDirectory.ts"), "utf8");
const compiled = ts.transpileModule(source, {
  compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 },
}).outputText;
const rows = Array.from({ length: 100 }, (_, i) => ({ id: String(i), locality_id: "one" }));
let calls = [];
let pages = [];
const moduleObject = { exports: {} };
new Function("exports", "require", "module", compiled)(
  moduleObject.exports,
  name => {
    assert.equal(name, "../api");
    return { api: async (url, options) => {
      calls.push({ url, signal: options.signal });
      return pages.shift() ?? [];
    } };
  },
  moduleObject,
);
const { loadMerchantDirectory } = moduleObject.exports;

(async () => {
  const signal = new AbortController().signal;
  pages = [rows, [rows[0], { id: "100", locality_id: "two" }]];
  calls = [];
  const result = await loadMerchantDirectory(signal);
  assert.equal(result.length, 101);
  assert.deepEqual(result.map(row => row.id), [...rows.map(row => row.id), "100"]);
  assert.deepEqual(calls.map(call => call.url), [
    "/api/v1/merchant-directory?limit=100&offset=0",
    "/api/v1/merchant-directory?limit=100&offset=100",
  ]);
  assert(calls.every(call => call.signal === signal));

  // A short first page terminates pagination without requesting extra pages.
  pages = [[{ id: "short" }]];
  calls = [];
  assert.deepEqual((await loadMerchantDirectory()).map(row => row.id), ["short"]);
  assert.equal(calls.length, 1);

  // Empty directories must return without requesting another page.
  pages = [[]];
  calls = [];
  assert.deepEqual(await loadMerchantDirectory(), []);
  assert.equal(calls.length, 1);

  // A continuously full directory must stop at the documented 100-page safety cap.
  // Reusing the same records keeps the fixture small while testing the cap itself.
  pages = Array.from({ length: 100 }, () => rows);
  calls = [];
  await assert.rejects(loadMerchantDirectory(), /exceeded the supported page limit/);
  assert.equal(calls.length, 100);
  assert.equal(calls.at(-1).url, "/api/v1/merchant-directory?limit=100&offset=9900");

  // An API failure must propagate, not silently present an incomplete directory.
  pages = [];
  calls = [];
  const error = new Error("API unavailable");
  const failingModule = { exports: {} };
  new Function("exports", "require", "module", compiled)(
    failingModule.exports,
    () => ({ api: async () => { throw error; } }),
    failingModule,
  );
  await assert.rejects(failingModule.exports.loadMerchantDirectory(), err => err === error);
  console.log("Merchant directory pagination checks passed: bounded offsets, deduplication, abort forwarding and errors.");
})().catch(error => { console.error(error); process.exitCode = 1; });
