import { useEffect, useState } from "react";
import { Image, Modal, StyleSheet, View, useWindowDimensions, type ImageSourcePropType } from "react-native";
import { Pressable, Text, useUI } from "../ui";
import { cachedThumbnail } from "./thumbnailCache";

type Props = {
  id: string;
  name: string;
  uri?: string | null;
  representativeUri?: string;
  fallback: ImageSourcePropType;
  symbolic: boolean;
};

export function ProductThumbnail({ id, name, uri, representativeUri, fallback, symbolic }: Props) {
  const { styles: s, t } = useUI();
  const [failed, setFailed] = useState<string[]>([]);
  const url = [uri, representativeUri].find(candidate => candidate && !failed.includes(candidate));
  const [resolved, setResolved] = useState<{ url: string; path: string }>();
  const [loadedPath, setLoadedPath] = useState<string>();
  const [fallbackLoaded, setFallbackLoaded] = useState(false);
  const [enlarged, setEnlarged] = useState(false);
  const { height } = useWindowDimensions();
  useEffect(() => {
    if (!url) return;
    let active = true;
    void (cachedThumbnail(url) ?? Promise.resolve(url)).then(
      path => { if (active) setResolved({ url, path }); },
      () => { if (active) setResolved({ url, path: url }); },
    );
    return () => { active = false; };
  }, [url]);

  const remote = resolved && resolved.url === url ? resolved : undefined;
  const remoteLoaded = Boolean(remote && loadedPath === remote.path);
  const source = remoteLoaded && remote ? { uri: remote.path } : fallback;
  const photoName = (remoteLoaded && remote?.url === uri) || (id.startsWith("demo-") && !symbolic)
    ? name : `${name} · ${t(symbolic ? "symbolicImage" : "representativePhoto")}`;
  const close = () => setEnlarged(false);

  function handleError() {
    if (!remote) return;
    setLoadedPath(undefined);
    if (remote.path !== remote.url) {
      setResolved({ url: remote.url, path: remote.url });
    } else {
      setFailed(previous => [...previous, remote.url]);
    }
  }

  return (
    <>
      <Pressable accessibilityRole="button" accessibilityLabel={`${t("enlargePhoto")}: ${photoName}`}
        testID={`thumbnail-${fallbackLoaded || remoteLoaded ? "loaded" : "loading"}-${id}`}
        onPress={() => setEnlarged(true)}>
        <Image accessibilityLabel={photoName} aria-hidden={remoteLoaded}
          source={fallback} style={[s.photo, remoteLoaded && { opacity: 0 }]}
          resizeMode="contain" onLoad={() => setFallbackLoaded(true)} />
        {remote && <Image key={remote.path} accessibilityLabel={photoName} aria-hidden={!remoteLoaded}
          source={{ uri: remote.path }}
          style={[s.photo, StyleSheet.absoluteFillObject, { opacity: remoteLoaded ? 1 : 0 }]}
          resizeMode="contain" onLoad={() => setLoadedPath(remote.path)} onError={handleError} />}
      </Pressable>
      {enlarged && (
        <Modal transparent visible onRequestClose={close}>
          <View style={{ flex: 1, alignItems: "center", justifyContent: "center", backgroundColor: "rgba(0,0,0,0.65)" }}>
            <View testID="thumbnail-viewer" accessibilityViewIsModal
              style={[s.panel, { width: "92%", maxWidth: 640 }]}>
              <Text style={s.productName}>{photoName}</Text>
              <Text style={s.meta}>{t("illustrativePhotoNotice")}</Text>
              <Image accessibilityLabel={photoName} source={source} resizeMode="contain"
                style={{ width: "100%", height: height * 0.50, backgroundColor: "#fff" }}
                onError={handleError} />
              <Pressable accessibilityRole="button" style={s.button} onPress={close}>
                <Text style={s.productName}>{t("closePhoto")}</Text>
              </Pressable>
            </View>
          </View>
        </Modal>
      )}
    </>
  );
}
