const assert = require("node:assert/strict");
const { createHash } = require("node:crypto");
const fs = require("node:fs");
const path = require("node:path");
const { createRequire } = require("node:module");
const ts = require("typescript");

const root = path.resolve(__dirname, "../..");
const resolver = path.join(root, "mobile/src/catalog/samples.ts");
const localRequire = createRequire(resolver);
const bundled = new Map();
const pack = path.join(root, "data/catalogue-thumbnails");
const expectedHashes = require(path.join(pack, "sha256.json"));
const managed = fs.readdirSync(pack).filter(name => name.endsWith(".webp"));
assert.deepEqual(managed.map(name => path.basename(name, ".webp")).sort(), Object.keys(expectedHashes).sort());
for (const name of managed) {
  const digest = createHash("sha256").update(fs.readFileSync(path.join(pack, name))).digest("hex");
  assert.equal(digest, expectedHashes[path.basename(name, ".webp")], `Stale SHA-256: ${name}`);
}
function loadAsset(relative) {
  if (!relative.endsWith(".webp")) return localRequire(relative);
  const filename = path.resolve(path.dirname(resolver), relative);
  const bytes = fs.readFileSync(filename);
  assert.equal(bytes.toString("ascii", 0, 4), "RIFF", filename);
  assert.equal(bytes.toString("ascii", 8, 12), "WEBP", filename);
  const digest = createHash("sha256").update(bytes).digest("hex");
  bundled.set(filename, { digest, bytes: bytes.length });
  return filename;
}
const { outputText } = ts.transpileModule(fs.readFileSync(resolver, "utf8"), {
  compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
});
const exportsObject = {};
new Function("exports", "require", outputText)(exportsObject, loadAsset);
const { productArtwork, sampleProducts } = exportsObject;
const known = [
  ["groceries", "БИСКВИТИ АКЦЕНТ 120ГР", "biscuits"],
  ["groceries", "ОБИКНОВЕНИ БИСКВИТИ 120ГР", "biscuits"],
  ["groceries", "БИРА АРИАНА 2Л", "beer"],
  ["technology", "Разпенител за мляко Sencor", "milk-frother"],
  ["technology", "Безжичен звънец Sencor", "doorbell"],
  ["technology", "Сушилня Beko", "tumble-dryer"],
  ["technology", "Неопознат артикул", "unclassified"],
];
for (const [category_code, name, code] of known) {
  assert.equal(productArtwork({ category_code, name }).code, code, name);
}

const baseline = { groceries: 990, technology: 436 };
const coverage = {};
for (const category of Object.keys(baseline)) {
  const snapshot = require(path.join(root, "data", category, "essential-1000.json"));
  const products = snapshot.products.map(row => ({ ...row, category_code: category }));
  let categoryOrGroup = 0;
  let neutralPlaceholder = 0;
  assert(products.length > 0, `${category} fixture is empty`);
  for (const product of products) {
    const { source, code } = productArtwork(product);
    assert(bundled.has(source), `Missing fallback for ${category} ${product.source_product_code}`);
    if (code === product.group_code || code === category) categoryOrGroup++;
    if (code === "unclassified") neutralPlaceholder++;
  }
  coverage[category] = { products: products.length, categoryOrGroup, neutralPlaceholder, baseline: baseline[category] };
}
for (const product of sampleProducts) {
  assert(bundled.has(productArtwork(product).source), `Missing demo artwork for ${product.id}`);
}
const assets = [...bundled.values()];
assert.equal(new Set(assets.map(asset => asset.digest)).size, assets.length,
  "Identical bundled WebP bytes should share a reference");
const bytes = assets.reduce((total, asset) => total + asset.bytes, 0);
console.log(JSON.stringify({
  coverage, bundledWebPs: assets.length, bundledBytes: bytes,
  bundledBytesDeltaFromPreview016: bytes - 61906,
}, null, 2));
