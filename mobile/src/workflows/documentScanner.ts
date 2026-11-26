import { requireOptionalNativeModule } from "expo";
import type { ImagePickerAsset } from "expo-image-picker";
import { Platform } from "react-native";

export function getDocumentScanner() {
  return Platform.OS === "android"
    ? requireOptionalNativeModule<{ scanAsync(): Promise<ImagePickerAsset | null> }>("SpestovnikReceiptScanner")
    : null;
}
