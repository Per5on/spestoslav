import AsyncStorage from "@react-native-async-storage/async-storage";
import * as FileSystem from "expo-file-system/legacy";
import * as SecureStore from "expo-secure-store";
import { Platform } from "react-native";
import { API_BASE_URL } from "./api";

export type CloudErasure = "guest" | "deleted" | "unconfirmed";

export const savedListKey = "spestovnik-preview-001";
export const preferencesKey = "spestovnik-preferences";
export const sessionKey =
  "spestovnik-private-session-" + API_BASE_URL.replace(/[^a-zA-Z0-9._-]/g, "_");

export async function eraseLocalData() {
  const work = [AsyncStorage.multiRemove([savedListKey, preferencesKey])];
  if (Platform.OS !== "web") {
    work.push(SecureStore.deleteItemAsync(sessionKey));
    if (FileSystem.cacheDirectory) {
      work.push(FileSystem.deleteAsync(FileSystem.cacheDirectory + "ImagePicker", {
        idempotent: true,
      }));
    }
  }
  const outcomes = await Promise.allSettled(work);
  return outcomes.every(result => result.status === "fulfilled");
}
