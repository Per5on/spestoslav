import { View } from "react-native";
import Ionicons from "@expo/vector-icons/Ionicons";
import { palettes } from "../appearance";
import { Pressable, Text, useUI } from "../ui";

type Props = { images: boolean; onToggleImages: (enabled: boolean) => void };

export function AppearanceScreen({ images, onToggleImages }: Props) {
  const { t, palette, setPalette, dark, setDark, styles: s, color } = useUI();
  function toggle(key: "appearanceImages" | "appearanceDark", selected: boolean, change: (value: boolean) => void) {
    return (
        <Pressable key={key} accessibilityRole="switch" accessibilityState={{ checked: selected }}
          aria-checked={selected} accessibilityLabel={t(key)}
          style={[s.button, s.option, { justifyContent: "space-between" }]}
          onPress={() => change(!selected)}>
          <Text style={s.productName}>{t(key)}</Text>
          <Ionicons name={selected ? "checkbox" : "square-outline"} size={23} color={color("#267133")} />
        </Pressable>
    );
  }
  return (
    <View testID="appearance-screen" style={s.panel}>
      {toggle("appearanceImages", images, onToggleImages)}
      <Text style={s.productName}>{t("appearancePalette")}</Text>
      <View style={[s.row, { flexWrap: "wrap" }]}>
        {palettes.map((combination, index) => (
          <Pressable key={`${combination.header}-${combination.accent}`} accessibilityRole="radio"
            accessibilityLabel={`${t("appearancePalette")} ${index + 1}`}
            accessibilityState={{ checked: index === palette }} aria-checked={index === palette}
            onPress={() => setPalette(index)}
            style={[s.button, { paddingHorizontal: 8, alignItems: "center", width: "22%" }]}>
            <View style={{ flexDirection: "row", borderRadius: 10, overflow: "hidden", height: 18, width: 44 }}>
              <View style={{ flex: 1, backgroundColor: combination.header }} />
              <View style={{ flex: 1, backgroundColor: combination.accent }} />
            </View>
            <Text style={s.meta}>{index === palette ? "✓" : String(index + 1)}</Text>
          </Pressable>
        ))}
      </View>
      {toggle("appearanceDark", dark, setDark)}
    </View>
  );
}
