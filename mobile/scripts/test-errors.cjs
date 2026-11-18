const ts = require("typescript"),
  fs = require("node:fs"),
  assert = require("node:assert/strict");
const code = ts.transpileModule(fs.readFileSync("src/api.ts", "utf8"), {
  compilerOptions: {
    module: ts.ModuleKind.CommonJS,
    target: ts.ScriptTarget.ES2022,
    esModuleInterop: false,
  },
}).outputText;
let status = 200;
const mockNetwork = {
  fetchWithRetry: async (_url, _init, _opts, read) =>
    read({ ok: status < 400, status, json: async () => ({ ok: true }) }),
};
const m = { exports: {} };
new Function("exports", "require", "module", "process", code)(
  m.exports,
  () => mockNetwork,
  m,
  { env: {} },
);
const { api, ApiError, httpStatus } = m.exports;
(async () => {
  status = 409;
  const error = await api("/x").catch((e) => e);
  assert(error instanceof ApiError && error.status === 409);
  assert.equal(error.message, "HTTP 409"); // older string checks keep working
  assert.equal(httpStatus(error), 409);
  assert.equal(httpStatus(new Error("HTTP 503")), 503);
  assert.equal(httpStatus("Error: HTTP 404"), 404);
  for (const value of [new Error("Network request failed"), new TypeError("x"), null, undefined, "HTTP 4040"])
    assert.equal(httpStatus(value), null);
  status = 204;
  assert.equal(await api("/x"), undefined);
  status = 200;
  assert.deepEqual(await api("/x"), { ok: true });
  console.log("Error checks passed: typed API errors, status extraction, backward-compatible messages.");
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
