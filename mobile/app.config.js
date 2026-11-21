const base = require("./app.json").expo;
const preview = require("./preview.json");
if (!/^[0-9]{3}$/.test(preview.sequence) || Number(preview.sequence) < 1)
  throw new Error("Invalid preview sequence");
if (preview.label !== undefined && !/^\d+(?:\.\d+)?$/.test(preview.label))
  throw new Error("Invalid preview label");
if (!/^\d+\.\d+\.\d+$/.test(preview.version))
  throw new Error("Invalid app version");
// Local dry builds can vary one packaging setting at a time.
const dryAbi = process.env.SPESTOVNIK_DRY_ANDROID_ABI;
const dryShrink = process.env.SPESTOVNIK_DRY_ANDROID_SHRINK === "1";
if (dryAbi && !["arm64-v8a", "x86_64", "armeabi-v7a"].includes(dryAbi))
  throw new Error("Unsupported dry-test Android ABI");

module.exports = {
  ...base,
  name: `Спестовник ${preview.label ?? String(Number(preview.sequence)).padStart(2, "0")}`,
  version: preview.version,
  android: { ...base.android, versionCode: Number(preview.sequence) },
  plugins: base.plugins.map(plugin => {
    if (!Array.isArray(plugin) || plugin[0] !== "expo-build-properties") return plugin;
    return [plugin[0], {
      ...plugin[1],
      android: {
        ...plugin[1].android,
        ...(dryAbi ? { buildArchs: [dryAbi] } : {}),
        ...(dryShrink ? {
          enableMinifyInReleaseBuilds: true,
          enableShrinkResourcesInReleaseBuilds: true,
        } : {}),
      },
    }];
  }),
};
