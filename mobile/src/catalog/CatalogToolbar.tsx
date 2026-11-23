import type { ReactNode } from "react";
import { View } from "react-native";
import { Button } from "../Action";
import { AutoFitLabel, Pressable, useUI } from "../ui";

const fuelChoices = ["petrol", "petrol98", "diesel", "dieselPlus", "lpg"] as const;
export type FuelChoice = (typeof fuelChoices)[number];

export function CatalogToolbar({ children, onRefresh, fuel, onFuel }: {
  children: ReactNode;
  onRefresh: () => void;
  fuel?: FuelChoice;
  onFuel: (fuel: FuelChoice) => void;
}) {
  const { t, styles: s } = useUI();
  if (fuel) {
    return (
      <View testID="catalog-toolbar" accessibilityRole="radiogroup"
        style={[s.headingRow, { alignItems: "stretch", gap: 4 }]}>
        {fuelChoices.map(value => {
          const selected = fuel === value;
          return (
            <Pressable key={value} accessibilityRole="radio" accessibilityLabel={t(value)}
              accessibilityState={{ checked: selected }} aria-checked={selected}
              onPress={() => onFuel(value)}
              style={[s.button, { flex: 1, minWidth: 44, paddingHorizontal: 3 }, selected && s.primary]}>
              <AutoFitLabel label={t(value)} baseSize={13} allowWrap
                style={{ width: "100%", color: selected ? "#111" : "#19562a", textAlign: "center", fontWeight: "600" }} />
            </Pressable>
          );
        })}
      </View>
    );
  }

  return (
    <View testID="catalog-toolbar" style={[s.headingRow, { alignItems: "stretch" }]}>
      <View style={{ flex: 1, minWidth: 0 }}>{children}</View>
      <Button compactRefresh label={t("refresh")} onPress={onRefresh} />
    </View>
  );
}
