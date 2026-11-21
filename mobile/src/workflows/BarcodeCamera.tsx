import React from "react";
import { CameraView } from "expo-camera";
import { scannedGTIN } from "./barcode";
export function BarcodeCamera({
  onCode,
  onError,
}: {
  onCode: (code: string) => void;
  onError: () => void;
}) {
  return (
    <CameraView
      testID="barcode-camera"
      style={{ height: 240, borderRadius: 12 }}
      facing="back"
      barcodeScannerSettings={{ barcodeTypes: ["ean13", "ean8", "upc_a"] }}
      onMountError={onError}
      onBarcodeScanned={(r) => {
        const code = scannedGTIN(r.data, r.type);
        if (code) onCode(code);
      }}
    />
  );
}
