import { useEffect, useState } from "react";
import { Image, View } from "react-native";
import Ionicons from "@expo/vector-icons/Ionicons";
import { s } from "../styles";
export function ProductThumbnail({ id, name, uri }: { id: string; name: string; uri?: string | null }) {
  const [failed, setFailed] = useState(false);
  const [loadedUri, setLoadedUri] = useState<string | null>(null);
  useEffect(() => setFailed(false), [uri]);
  return uri && !failed ? <Image key={uri} testID={`thumbnail-${loadedUri === uri ? "loaded" : "loading"}-${id}`} onLoad={() => setLoadedUri(uri)} accessibilityLabel={name} source={{ uri }} style={s.photo} resizeMode="contain" onError={() => setFailed(true)} /> :
    <View testID={`thumbnail-fallback-${id}`} style={s.photo}>
      <Ionicons name="cube-outline" size={48} color="#63816a" />
    </View>;
}
