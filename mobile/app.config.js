const base = require("./app.json").expo;
const preview = require("./preview.json");
if (!/^[0-9]{3}$/.test(preview.sequence) || Number(preview.sequence) < 1)
  throw new Error("Invalid preview sequence");
if (!/^\d+\.\d+\.\d+$/.test(preview.version))
  throw new Error("Invalid app version");
module.exports = {
  ...base,
  name: `Спестовник ${String(Number(preview.sequence)).padStart(2, "0")}`,
  version: preview.version,
  android: { ...base.android, versionCode: Number(preview.sequence) },
};
