// Keep the locked Expo 54 toolchain compatible with patched image-size.
// Also backport the deepmerge prototype-key fix until upstream publishes it.
const fs = require("node:fs");
const path = require("node:path");
const base = path.resolve(__dirname, "..", "node_modules");
function patch(file, before, after) {
  const target = path.join(base, file);
  const source = fs.readFileSync(target, "utf8");
  if (source.includes(after)) return;
  if (!source.includes(before))
    throw Error(`Dependency changed; review patch: ${file}`);
  fs.writeFileSync(target, source.replace(before, after));
}
patch(
  "metro/src/Assets.js",
  `  const isImageInput = assetInfo.files[0].includes(".zip/")
    ? _fs.default.readFileSync(assetInfo.files[0])
    : assetInfo.files[0];
  const dimensions = isImage ? (0, _imageSize.default)(isImageInput) : null;`,
  `  const dimensions = isImage
    ? (0, _imageSize.default)(_fs.default.readFileSync(assetInfo.files[0]))
    : null;`,
);
for (const file of [
  "deepmerge/index.js",
  "deepmerge/dist/cjs.js",
  "deepmerge/dist/umd.js",
]) {
  patch(
    file,
    "return Object.keys(target).concat(getEnumerableOwnPropertySymbols(target))",
    "return Object.keys(target).concat(getEnumerableOwnPropertySymbols(target)).filter(function(key) { return key !== '__proto__' && key !== 'constructor' && key !== 'prototype' })",
  );
}
console.log(
  "Applied reviewed Metro compatibility and deepmerge prototype-key patches.",
);
