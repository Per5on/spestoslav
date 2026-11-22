import { useEffect, useState } from "react";
import { Image, Modal, View, useWindowDimensions, type ImageSourcePropType } from "react-native";
import { Pressable, Text, useUI } from "../ui";
import { sampleThumbnail } from "./samples";
import { cachedThumbnail } from "./thumbnailCache";

type Props = {
  id: string;
  name: string;
  uri?: string | null;
  fallback: ImageSourcePropType;
  symbolic: boolean;
};

export function ProductThumbnail(props: Props) {
  return <Thumbnail key={props.uri ?? ""} {...props} />;
}

function Thumbnail({ id, name, uri, fallback, symbolic }: Props) {
  const { styles: s, t } = useUI();
  const sample = sampleThumbnail(id);
  const [resolved, setResolved] = useState<string>();
  const [loaded, setLoaded] = useState<string>();
  useEffect(() => {
    if (sample || !uri) return;
    let active = true;
    const pending = cachedThumbnail(uri);
    void (pending ?? Promise.resolve(uri)).then(
      value => { if (active) setResolved(value); },
      () => { if (active) setResolved(uri); },
    );
    return () => { active = false; };
  }, [sample, uri]);
  const remote = resolved ? { uri: resolved } : undefined;
  const source = sample ?? remote ?? fallback;
  const imageKey = resolved ?? id;
  const photoName = !remote && (symbolic || !sample)
    ? `${name} · ${t(symbolic ? "symbolicImage" : "representativePhoto")}` : name;
  const [enlarged, setEnlarged] = useState(false);
  const { height } = useWindowDimensions();
  const close = () => setEnlarged(false);
  const handleError = () => {
    if (resolved) setResolved(resolved === uri ? undefined : uri ?? undefined);
  };
  return (
    <>
      <Pressable accessibilityRole="button" accessibilityLabel={`${t("enlargePhoto")}: ${photoName}`}
        testID={`thumbnail-${loaded === imageKey ? "loaded" : "loading"}-${id}`}
        onPress={() => setEnlarged(true)}>
        <Image key={imageKey} accessibilityLabel={photoName}
          source={source} style={s.photo}
          resizeMode="contain" onLoad={() => setLoaded(imageKey)} onError={handleError} />
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
