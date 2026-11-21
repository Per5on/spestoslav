import { useEffect, useState } from "react";
import { Image, View } from "react-native";
import Ionicons from "@expo/vector-icons/Ionicons";
import { useUI } from "../ui";
import { sampleThumbnail } from "./samples";
import { cachedThumbnail } from "./thumbnailCache";
export function ProductThumbnail({ id, name, uri }: { id: string; name: string; uri?: string | null }) {
  const { styles: s, color } = useUI();
  const [failed, setFailed] = useState(false);
  const [loadedUri, setLoadedUri] = useState<string | null>(null);
  const sample = sampleThumbnail(id);
  const key = sample ? id : uri;
  const [resolved, setResolved] = useState<{ original: string; uri: string }>();
  useEffect(() => {
    if (sample || !uri) return;
    let alive = true;
    const pending = cachedThumbnail(uri);
    void (pending ?? Promise.resolve(uri)).catch(() => uri).then(value => {
      if (alive) setResolved({ original: uri, uri: value });
    });
    return () => { alive = false; };
  }, [sample, uri]);
  const remote = resolved?.original === uri ? resolved?.uri : undefined;
  const source = sample ?? (remote ? { uri: remote } : undefined);
  useEffect(() => { setFailed(false); setLoadedUri(null); }, [key]);
  return source && !failed ? <Image key={key} testID={`thumbnail-${loadedUri === key ? "loaded" : "loading"}-${id}`} onLoad={() => setLoadedUri(key ?? null)} accessibilityLabel={name} source={source} style={s.photo} resizeMode="contain" onError={() => {
    if (uri && remote && remote !== uri) setResolved({ original: uri, uri });
    else setFailed(true);
  }} /> :
    <View testID={`thumbnail-fallback-${id}`} style={s.photo}>
      <Ionicons name="cube-outline" size={48} color={color("#63816a")} />
    </View>;
}
