import { Platform } from "react-native";
import * as FileSystem from "expo-file-system/legacy";

const directory = FileSystem.cacheDirectory && FileSystem.cacheDirectory + "thumbnails-v1/";
const maxFile = 512 * 1024;
const maxCache = 24 * 1024 * 1024;
const pending = new Map<string, Promise<string>>();
let eviction = Promise.resolve();

async function trimCache(path: string) {
  const entries = await FileSystem.readDirectoryAsync(path);
  const files = (await Promise.all(entries.filter(name => !name.includes(".partial")).map(
    name => FileSystem.getInfoAsync(path + name),
  ))).filter(file => file.exists).filter(file => !file.isDirectory);
  files.sort((a, b) => a.modificationTime - b.modificationTime);
  let bytes = files.reduce((total, file) => total + file.size, 0);
  for (const file of files) {
    if (bytes <= maxCache) break;
    await FileSystem.deleteAsync(file.uri, { idempotent: true });
    bytes -= file.size;
  }
}

async function fetchThumbnail(uri: string, target: string, path: string) {
  const working = target + ".partial";
  try {
    await FileSystem.makeDirectoryAsync(path, { intermediates: true });
    const saved = await FileSystem.getInfoAsync(target);
    if (saved.exists && !saved.isDirectory) return target;
    const task = FileSystem.createDownloadResumable(uri, working, {}, progress => {
      if (progress.totalBytesWritten > maxFile ||
          progress.totalBytesExpectedToWrite > maxFile) {
        void task.pauseAsync().catch(() => undefined);
      }
    });
    const timeout = setTimeout(() => void task.pauseAsync().catch(() => undefined), 6000);
    try {
      const response = await task.downloadAsync();
      const image = response && Object.entries(response.headers).some(
        ([key, value]) => key.toLowerCase() === "content-type" && /^image\//i.test(value),
      );
      const info = await FileSystem.getInfoAsync(working);
      if (response?.status !== 200 || !image || !info.exists || info.isDirectory ||
          info.size === 0 || info.size > maxFile) return uri;
      await FileSystem.moveAsync({ from: working, to: target });
      eviction = eviction.then(() => trimCache(path)).catch(() => undefined);
      return target;
    } finally {
      clearTimeout(timeout);
    }
  } catch {
    return uri;
  } finally {
    await FileSystem.deleteAsync(working, { idempotent: true }).catch(() => undefined);
  }
}

export function cachedThumbnail(uri: string): Promise<string> | undefined {
  if (Platform.OS === "web" || !directory || !uri.startsWith("https://")) return;
  // Preserve the complete URL as the key, including its content version.
  const filename = encodeURIComponent(uri).replace(/~/g, "%7E").replace(/%/g, "~");
  if (filename.length > 225) return;
  const target = directory + filename;
  const existing = pending.get(target);
  if (existing) return existing;
  if (pending.size >= 3) {
    // Existing files remain readable while all download slots are occupied.
    return FileSystem.getInfoAsync(target)
      .then(info => info.exists && !info.isDirectory ? target : uri)
      .catch(() => uri);
  }
  const operation = fetchThumbnail(uri, target, directory).finally(() => pending.delete(target));
  pending.set(target, operation);
  return operation;
}
