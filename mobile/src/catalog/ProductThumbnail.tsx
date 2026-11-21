import { useEffect, useState } from "react";
import { Image, type ImageSourcePropType } from "react-native";
import { useUI } from "../ui";
import { sampleThumbnail } from "./samples";
import { cachedThumbnail } from "./thumbnailCache";

type Props = {
  id: string;
  name: string;
  uri?: string | null;
  illustration?: ImageSourcePropType;
  fallback: ImageSourcePropType;
  fallbackLabel?: string;
};

export function ProductThumbnail(props: Props) {
  return <Thumbnail key={props.uri ?? ""} {...props} />;
}

function Thumbnail({ id, name, uri, illustration, fallback, fallbackLabel }: Props) {
  const { styles: s, t } = useUI();
  const sample = sampleThumbnail(id);
  const [resolved, setResolved] = useState<string>();
  const [loaded, setLoaded] = useState<string>();
  useEffect(() => {
    if (illustration || sample || !uri) return;
    let active = true;
    const pending = cachedThumbnail(uri);
    void (pending ?? Promise.resolve(uri)).then(
      value => { if (active) setResolved(value); },
      () => { if (active) setResolved(uri); },
    );
    return () => { active = false; };
  }, [illustration, sample, uri]);
  const remote = resolved ? { uri: resolved } : undefined;
  const source = illustration ?? sample ?? remote ?? fallback;
  const symbolic = source === illustration || source === fallback;
  const imageKey = resolved ?? id;
  return <Image key={imageKey}
    testID={`thumbnail-${loaded === imageKey ? "loaded" : "loading"}-${id}`}
    accessibilityLabel={symbolic ? `${name} · ${fallbackLabel ?? t("symbolicImage")}` : name}
    source={source} style={[s.photo, { backgroundColor: "#fff" }]} resizeMode="contain" onLoad={() => setLoaded(imageKey)}
    onError={() => {
      if (resolved) setResolved(resolved === uri ? undefined : uri ?? undefined);
    }} />;
}
