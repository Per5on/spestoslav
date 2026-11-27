// GitHub environment/outputs come from validated metadata, never a handwritten label.
const fs = require("node:fs");
const { validLabel } = require("./preview-label.cjs");
const { sequence, label = sequence } = require("../preview.json");
if (!/^[0-9]{3}$/.test(sequence) || Number(sequence) < 1)
  throw new Error("Invalid preview sequence");
if (!validLabel(label)) throw new Error("Invalid preview label");
const abi = process.env.PREVIEW_ABI ?? "universal";
if (!["universal", "arm64-v8a", "armeabi-v7a"].includes(abi)) throw new Error("Invalid preview ABI");
const artifact = abi === "universal" ? label : `${label}-${abi}`;
for (const [variable, value] of [["GITHUB_ENV", `PREVIEW_SEQUENCE=${label}\nPREVIEW_ARTIFACT=${artifact}\n`], ["GITHUB_OUTPUT", `sequence=${label}\n`]]) {
  if (process.env[variable]) fs.appendFileSync(process.env[variable], value);
}
console.log(`Preview ${label}`);
