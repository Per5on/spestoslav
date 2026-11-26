import { useEffect, useState } from "react";
import { api, API_BASE_URL } from "../api";

import hashes from "../../../data/catalogue-thumbnails/sha256.json";

const bundledHashes: Readonly<Record<string, string>> = hashes;
type ThumbnailUrls = Readonly<Record<string, string>>;

export function parseThumbnailManifest(value: unknown): ThumbnailUrls {
  if (!value || typeof value !== "object" || !("schema_version" in value) || value.schema_version !== 1 ||
      !("images" in value) || !value.images || typeof value.images !== "object") return {};
  const entries = Object.entries(value.images).filter(([code, path]) => {
    if (!/^[a-z0-9-]+$/.test(code) || typeof path !== "string") return false;
    const prefix = `/api/v1/thumbnails/catalogue/${code}?v=`;
    const digest = path.slice(prefix.length);
    return Boolean(bundledHashes[code]) && path.startsWith(prefix) &&
      /^[a-f0-9]{64}$/.test(digest) && digest !== bundledHashes[code];
  });
  return Object.fromEntries(entries.map(([code, path]) => [code, API_BASE_URL + path]));
}

export function useThumbnailManifest(refresh: number, ready: boolean) {
  const [images, setImages] = useState<ThumbnailUrls>({});
  useEffect(() => {
    if (!ready) return;
    const controller = new AbortController();
    const load = () => {
      void api<unknown>("/api/v1/thumbnails/catalogue", { signal: controller.signal }, 5000)
        .then(result => {
          if (!controller.signal.aborted) setImages(parseThumbnailManifest(result));
        })
        .catch(() => { /* The bundled pack is immediately available. */ });
    };
    let cancel: () => void;
    if (typeof requestIdleCallback === "function") {
      const timer = requestIdleCallback(load, { timeout: 1200 });
      cancel = () => cancelIdleCallback(timer);
    } else {
      const timer = setTimeout(load, 250);
      cancel = () => clearTimeout(timer);
    }
    return () => {
      cancel();
      controller.abort();
    };
  }, [refresh, ready]);
  return images;
}
