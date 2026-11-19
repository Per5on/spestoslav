import { scanFromURLAsync } from "expo-camera";
import { scannedGTIN } from "./barcode";

// Android ML Kit's static image scanner can return native integer format
// constants instead of the Expo string BarcodeType used by camera callbacks.
// EAN_13=32, EAN_8=64, UPC_A=512 (ML Kit Barcode.FORMAT_*).
function normalizedImageBarcodeType(type: string | number): string {
  if (type === 32 || type === "32") return "ean13";
  if (type === 64 || type === "64") return "ean8";
  if (type === 512 || type === "512") return "upc_a";
  // Some native decoders report symbolic enum names rather than Expo names.
  const symbolic = String(type).toLowerCase().replace(/[^a-z0-9]/g, "");
  if (symbolic === "ean13" || symbolic === "ean8" || symbolic === "upca") {
    return symbolic === "upca" ? "upc_a" : symbolic;
  }
  return String(type).toLowerCase();
}

export async function decodeBarcodeImage(uri: string): Promise<string | null> {
  // An unreadable or unsupported photo is not a successful scan. Match the
  // browser decoder contract and let the UI show its normal no-result state.
  let rows: Awaited<ReturnType<typeof scanFromURLAsync>>;
  try {
    rows = await scanFromURLAsync(uri, ["ean13", "ean8", "upc_a"]);
  } catch {
    return null;
  }
  const candidates = rows.map((row) => {
    const type = normalizedImageBarcodeType(row.type);
    return { type, code: scannedGTIN(row.data, type) };
  });
  // Never log scanned values, image URIs, or other user media metadata.
  console.info(
    "Image barcode scan results:",
    JSON.stringify(candidates.map((row) => ({
      type: row.type,
      valid: Boolean(row.code),
    }))),
  );
  return candidates.find((row) => row.code)?.code ?? null;
}
