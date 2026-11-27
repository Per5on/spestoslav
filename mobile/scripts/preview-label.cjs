const mixedAlpha = /^alpha[1-9]\d*M$/;

function validLabel(label) {
  return typeof label === "string" &&
    (/^\d+(?:\.\d+){0,2}(?:-hybrid)?$/.test(label) || mixedAlpha.test(label));
}

function isMixedLabel(label) {
  return validLabel(label) && (label.endsWith("-hybrid") || mixedAlpha.test(label));
}

module.exports = { validLabel, isMixedLabel };
