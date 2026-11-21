// GitHub environment/outputs come from validated metadata, never a handwritten label.
const fs = require("node:fs");
const { sequence, label = sequence } = require("../preview.json");
if (!/^[0-9]{3}$/.test(sequence) || Number(sequence) < 1)
  throw new Error("Invalid preview sequence");
if (!/^\d+(?:\.\d+)?$/.test(label)) throw new Error("Invalid preview label");
for (const [variable, value] of [["GITHUB_ENV", `PREVIEW_SEQUENCE=${label}\n`], ["GITHUB_OUTPUT", `sequence=${label}\n`]]) {
  if (process.env[variable]) fs.appendFileSync(process.env[variable], value);
}
console.log(`Preview ${label}`);
