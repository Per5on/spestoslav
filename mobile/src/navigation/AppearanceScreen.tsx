import { View } from "react-native";
import Ionicons from "@expo/vector-icons/Ionicons";
import { palettes } from "../appearance";
import { Pressable, Text, useUI } from "../ui";

export function AppearanceScreen() {
  const { t, palette, setPalette, dark, setDark, styles: s, color } = useUI();
  return (
    <View testID="appearance-screen" style={s.panel}>
      <Pressable accessibilityRole="switch" accessibilityState={{ checked: dark }}
        aria-checked={dark} accessibilityLabel={t("appearanceDark")}
        style={[s.button, s.option, { justifyContent: "space-between" }]}
        onPress={() => setDark(!dark)}>
        <Text style={s.productName}>{t("appearanceDark")}</Text>
        <Ionicons name={dark ? "checkbox" : "square-outline"} size={23} color={color("#267133")} />
      </Pressable>
      <Text style={s.productName}>{t("appearancePalette")}</Text>
      <View style={s.row}>
        {palettes.map((combination, index) => (
          <Pressable key={`${combination.header}/${combination.accent}`} accessibilityRole="radio"
            accessibilityLabel={`${t("appearancePalette")} ${index + 1}`}
            accessibilityState={{ checked: index === palette }} aria-checked={index === palette}
            onPress={() => setPalette(index)}
            style={[s.button, { paddingHorizontal: 8, alignItems: "center", width: "22%", minWidth: 60 }]}>
            <View style={{ flexDirection: "row", borderRadius: 10, overflow: "hidden", height: 18, width: 44 }}>
              <View style={{ flex: 1, backgroundColor: combination.header }} />
              <View style={{ flex: 1, backgroundColor: combination.accent }} />
            </View>
            <Text style={s.meta}>{index === palette ? "✓" : String(index + 1)}</Text>
          </Pressable>
        ))}
      </View>
    </View>
  );
}
