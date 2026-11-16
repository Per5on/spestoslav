import { scanFromURLAsync } from "expo-camera";
import { scannedGTIN } from "./barcode";
export async function decodeBarcodeImage(uri: string): Promise<string | null> {
  const rows = await scanFromURLAsync(uri, ["ean13", "ean8", "upc_a"]);
  return (
    rows
      .map((row) => scannedGTIN(row.data, row.type))
      .find((code): code is string => Boolean(code)) ?? null
  );
}
