// GS1 check digit: preserve leading zeroes; never turn a retailer PLU into a GTIN.
export function validGTIN(value: string): boolean {
  if (!/^(?:\d{8}|\d{12}|\d{13}|\d{14})$/.test(value)) return false;
  const body = value.slice(0, -1).split("").reverse();
  const sum = body.reduce(
    (n, d, i) => n + Number(d) * (i % 2 === 0 ? 3 : 1),
    0,
  );
  return (10 - (sum % 10)) % 10 === Number(value[value.length - 1]);
}
export function scannedGTIN(value: string, type: string): string | null {
  if (!["ean13", "ean8", "upc_a"].includes(type)) return null;
  const code = value.trim();
  return validGTIN(code) ? code : null;
}
