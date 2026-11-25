import AsyncStorage from "@react-native-async-storage/async-storage";
import * as BackgroundTask from "expo-background-task";
import * as TaskManager from "expo-task-manager";
import { Platform } from "react-native";
import { SIMULATION_MODE } from "../api";
import { savedListKey } from "../localData";
import { syncCatalogs } from "./catalogData";

const taskName = "spestovnik-catalog-sync";
const enabled = Platform.OS === "android" && !SIMULATION_MODE;

if (enabled) {
  TaskManager.defineTask(taskName, async () => {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 40000);
    try {
      const raw = await AsyncStorage.getItem(savedListKey);
      const locality = raw ? JSON.parse(raw)?.locality?.id : undefined;
      const ok = await syncCatalogs(typeof locality === "string" ? locality : undefined, controller.signal);
      return ok ? BackgroundTask.BackgroundTaskResult.Success : BackgroundTask.BackgroundTaskResult.Failed;
    } catch {
      return BackgroundTask.BackgroundTaskResult.Failed;
    } finally {
      clearTimeout(timer);
    }
  });
}

export async function enableCatalogSync() {
  if (!enabled || !await TaskManager.isAvailableAsync()) return;
  if (await BackgroundTask.getStatusAsync() !== BackgroundTask.BackgroundTaskStatus.Available) return;
  if (!await TaskManager.isTaskRegisteredAsync(taskName)) {
    await BackgroundTask.registerTaskAsync(taskName, { minimumInterval: 60 });
  }
}
