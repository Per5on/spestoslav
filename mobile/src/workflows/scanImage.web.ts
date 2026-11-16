import { BrowserMultiFormatReader } from "@zxing/browser";
import { BarcodeFormat, DecodeHintType } from "@zxing/library";
import { validGTIN } from "./barcode";
export const barcodeHints = new Map([
  [
    DecodeHintType.POSSIBLE_FORMATS,
    [BarcodeFormat.EAN_13, BarcodeFormat.EAN_8, BarcodeFormat.UPC_A],
  ],
]);
export async function decodeBarcodeImage(uri: string): Promise<string | null> {
  const reader = new BrowserMultiFormatReader(barcodeHints);
  try {
    const result = await reader.decodeFromImageUrl(uri);
    return validGTIN(result.getText()) ? result.getText() : null;
  } catch {
    return null;
  }
}
