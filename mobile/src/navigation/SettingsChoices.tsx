import { View, useWindowDimensions } from "react-native";
import Ionicons from "@expo/vector-icons/Ionicons";
import { Pressable, Text, useUI } from "../ui";
import { appFontSize } from "../font";
export function SettingsChoices({ items, selected, onSelect, radio = false, singleColumn = false }: {
  items: { value: string; label: string; icon?: "text-outline" | "language-outline" | "document-text-outline" | "shield-checkmark-outline" | "color-palette-outline" | "trash-outline" }[];
  selected?: string; onSelect: (value: string) => void; radio?: boolean; singleColumn?: boolean;
}) {
  const { width, fontScale: systemScale } = useWindowDimensions();
  const { fontScale, styles: s, color } = useUI();
  const columns = !singleColumn && width >= 360 && fontScale * systemScale <= 1.15;
  return <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 8 }}>
    {items.map(item => <Pressable key={item.value}
      accessibilityRole={radio ? "radio" : "button"}
      accessibilityLabel={item.label}
      accessibilityState={radio ? { checked: selected === item.value } : undefined}
      aria-checked={radio ? selected === item.value : undefined}
      onPress={() => onSelect(item.value)}
      style={[s.button, { width: columns ? "48%" : "100%", borderRadius: 14,
        flexDirection: "row", alignItems: "center", gap: 6 },
        selected === item.value && { backgroundColor: "#dbead3" }]}>
      {item.icon && <Ionicons name={item.icon} size={appFontSize(15, fontScale, 11)} color={color("#111")} />}
      <Text style={{ fontSize: 15, color: "#111", flex: 1 }}>{item.label}</Text>
      {selected === item.value && <Ionicons name="checkmark" color={color("#111")} size={appFontSize(15, fontScale, 11)} />}
    </Pressable>)}
  </View>;
}
