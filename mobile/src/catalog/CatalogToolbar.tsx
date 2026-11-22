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
  function choice(value: FuelChoice) {
    const selected = fuel === value;
    return <Pressable key={value} accessibilityRole="radio" accessibilityLabel={t(value)}
      accessibilityState={{ checked: selected }} aria-checked={selected} onPress={() => onFuel(value)}
      style={[s.button, { flexShrink: 1, minWidth: 0, paddingHorizontal: 8 }, selected && s.primary]}>
      <AutoFitLabel label={t(value)} baseSize={13} allowWrap
        style={{ color: selected ? "#111" : "#19562a", textAlign: "center", fontWeight: "600" }} />
    </Pressable>;
  }
  return (
    <View testID="catalog-toolbar" style={{ gap: 6 }} accessibilityRole={fuel ? "radiogroup" : undefined}>
      <View style={[s.headingRow, { alignItems: "stretch" }]}>
        {fuel
          ? <View testID="fuel-first-row" style={[s.headingRow, { alignItems: "stretch", flexShrink: 1 }]}>
              {fuelChoices.slice(0, 2).map(choice)}
            </View>
          : <View style={{ flex: 1, minWidth: 0 }}>{children}</View>}
        <Button compactRefresh label={t("refresh")} onPress={onRefresh} />
      </View>
      {fuel && <View testID="fuel-second-row" style={[s.headingRow, { alignItems: "stretch" }]}>
        {fuelChoices.slice(2).map(choice)}
      </View>}
    </View>
  );
}
