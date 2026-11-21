import { Pressable, View, useWindowDimensions } from "react-native";
import Ionicons from "@expo/vector-icons/Ionicons";
import { Text, useUI } from "../ui";
import { appFontSize } from "../font";
export function SettingsChoices({ items, selected, onSelect, radio = false }: {
  items: { value: string; label: string; icon?: "text-outline" | "language-outline" | "document-text-outline" | "shield-checkmark-outline" }[];
  selected?: string; onSelect: (value: string) => void; radio?: boolean;
}) {
  const { width, fontScale: systemScale } = useWindowDimensions();
  const { fontScale } = useUI();
  const columns = width >= 360 && fontScale * systemScale <= 1.15;
  return <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 8 }}>
    {items.map(item => <Pressable key={item.value}
      accessibilityRole={radio ? "radio" : "button"}
      accessibilityLabel={item.label}
      accessibilityState={radio ? { checked: selected === item.value } : undefined}
      aria-checked={radio ? selected === item.value : undefined}
      onPress={() => onSelect(item.value)}
      style={{ width: columns ? "48%" : "100%", minHeight: 44, borderWidth: selected === item.value ? 2 : 1,
        borderColor: "#555", backgroundColor: "#fff", borderRadius: 4, padding: 6,
        flexDirection: "row", alignItems: "center", gap: 6 }}>
      {item.icon && <Ionicons name={item.icon} size={appFontSize(15, fontScale, 11)} color="#111" />}
      <Text style={{ fontSize: 15, color: "#111", flex: 1 }}>{item.label}</Text>
      {selected === item.value && <Ionicons name="checkmark" color="#111" size={appFontSize(15, fontScale, 11)} />}
    </Pressable>)}
  </View>;
}
