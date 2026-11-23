import { useEffect, useState } from "react";
import { api, API_BASE_URL } from "../api";

type ThumbnailUrls = Readonly<Record<string, string>>;

export function parseThumbnailManifest(value: unknown): ThumbnailUrls {
  if (!value || typeof value !== "object" || !("schema_version" in value) || value.schema_version !== 1 ||
      !("images" in value) || !value.images || typeof value.images !== "object") return {};
  const entries = Object.entries(value.images).filter(([code, path]) => {
    if (!/^[a-z0-9-]+$/.test(code) || typeof path !== "string") return false;
    const prefix = `/api/v1/thumbnails/catalogue/${code}?v=`;
    return path.startsWith(prefix) && /^[a-f0-9]{64}$/.test(path.slice(prefix.length));
  });
  return Object.fromEntries(entries.map(([code, path]) => [code, API_BASE_URL + path]));
}

export function useThumbnailManifest(refresh: number) {
  const [images, setImages] = useState<ThumbnailUrls>({});
  useEffect(() => {
    const controller = new AbortController();
    void api<unknown>("/api/v1/thumbnails/catalogue", { signal: controller.signal }, 5000)
      .then(result => {
        if (!controller.signal.aborted) setImages(parseThumbnailManifest(result));
      })
      .catch(() => { /* The bundled pack is immediately available. */ });
    return () => controller.abort();
  }, [refresh]);
  return images;
}
