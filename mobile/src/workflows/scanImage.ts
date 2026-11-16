import { scanFromURLAsync } from "expo-camera";
import { scannedGTIN } from "./barcode";

export async function decodeBarcodeImage(uri: string): Promise<string | null> {
  const rows = await scanFromURLAsync(uri, ["ean13", "ean8", "upc_a"]);
  // Log only scanner classifications and a redacted length, never a user's
  // barcode value, selected photo path, or other private media metadata.
  console.info(
    "Image barcode scan results:",
    JSON.stringify(rows.map((row) => ({
      type: row.type,
      length: row.data?.length ?? 0,
      valid: Boolean(scannedGTIN(row.data, row.type)),
    }))),
  );
  return (
    rows
      .map((row) => scannedGTIN(row.data, row.type))
      .find((code): code is string => Boolean(code)) ?? null
  );
}
