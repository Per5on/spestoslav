// Regression tests for native photo barcode decoding without a device or build.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const ts = require("typescript");
const root = path.join(__dirname, "..", "src", "workflows");
const compile = (name, mockRequire) => {
  const source = fs.readFileSync(path.join(root, name), "utf8");
  const js = ts.transpileModule(source, {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 },
  }).outputText;
  const module = { exports: {} };
  vm.runInNewContext(js, { module, exports: module.exports, require: mockRequire, console: { info() {} } }, { filename: name });
  return module.exports;
};
const barcode = compile("barcode.ts", () => { throw Error("Unexpected import"); });
let result;
const scan = compile("scanImage.ts", (id) => {
  if (id === "./barcode") return barcode;
  if (id === "expo-camera") return { scanFromURLAsync: async () => result };
  throw Error("Unexpected import " + id);
});
(async () => {
  result = [{ type: 32, data: "4006381333931" }];
  assert.equal(await scan.decodeBarcodeImage("file://photo"), "4006381333931");
  result = [{ type: "EAN_13", data: "4006381333931" }];
  assert.equal(await scan.decodeBarcodeImage("file://photo"), "4006381333931");
  result = [{ type: "UPC_A", data: "036000291452" }];
  assert.equal(await scan.decodeBarcodeImage("file://photo"), "036000291452");
  result = [{ type: 64, data: "96385074" }];
  assert.equal(await scan.decodeBarcodeImage("file://photo"), "96385074");
  result = [{ type: "QR_CODE", data: "4006381333931" }];
  assert.equal(await scan.decodeBarcodeImage("file://photo"), null);
  result = [{ type: 32, data: "4006381333932" }];
  assert.equal(await scan.decodeBarcodeImage("file://photo"), null);
  result = [];
  assert.equal(await scan.decodeBarcodeImage("file://photo"), null);
  result = null;
  assert.equal(await scan.decodeBarcodeImage("file://null-result"), null);
  result = [{ type: 32, data: null }, null, { type: 32, data: "4006381333931" }];
  assert.equal(await scan.decodeBarcodeImage("file://mixed-results"), "4006381333931");
  result = { unexpected: "not an array" };
  assert.equal(await scan.decodeBarcodeImage("file://malformed-result"), null);
  // A rejected native image decoder must return no scan, not crash the UI.
  const broken = compile("scanImage.ts", (id) => id === "./barcode" ? barcode :
    { scanFromURLAsync: async () => { throw Error("Unreadable photo"); } });
  assert.equal(await broken.decodeBarcodeImage("file://bad-photo"), null);
  console.log("Native photo barcode regression tests passed");
})().catch((err) => { console.error(err); process.exitCode = 1; });
