import { useState, type ReactNode } from "react";
import { Text as NativeText, View, useWindowDimensions } from "react-native";
import { appFontSize } from "../font";
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
  const { t, styles: s, fontScale } = useUI();
  const { fontScale: systemScale } = useWindowDimensions();
  const [availableWidth, setAvailableWidth] = useState(0);
  const [labelWidths, setLabelWidths] = useState<Partial<Record<FuelChoice, number>>>({});
  const gap = s.headingRow.gap;
  const padding = 8;

  let firstCount = 0;
  let usedWidth = 0;
  for (const value of fuelChoices) {
    const labelWidth = labelWidths[value];
    if (labelWidth === undefined) break;
    const nextWidth = usedWidth + (firstCount ? gap : 0) + Math.max(44, Math.ceil(labelWidth) + 2 * padding + 1);
    if (nextWidth > availableWidth) break;
    usedWidth = nextWidth;
    firstCount += 1;
  }

  function choice(value: FuelChoice) {
    const selected = fuel === value;
    return <Pressable key={value} accessibilityRole="radio" accessibilityLabel={t(value)}
      accessibilityState={{ checked: selected }} aria-checked={selected} onPress={() => onFuel(value)}
      style={[s.button, { flexGrow: 1, flexShrink: 1, minWidth: 44, paddingHorizontal: padding }, selected && s.primary]}>
      <AutoFitLabel label={t(value)} baseSize={13} allowWrap
        style={{ color: selected ? "#111" : "#19562a", textAlign: "center", fontWeight: "600" }} />
    </Pressable>;
  }

  return (
    <View testID="catalog-toolbar" style={{ gap: 6 }} accessibilityRole={fuel ? "radiogroup" : undefined}>
      <View style={[s.headingRow, { alignItems: "stretch" }]}>
        {fuel
          ? <View key="fuel-choices" testID="fuel-first-row" onLayout={event => setAvailableWidth(event.nativeEvent.layout.width)}
              style={[s.headingRow, { flex: 1, minWidth: 0, alignItems: "stretch" }]}>
              {fuelChoices.slice(0, firstCount).map(choice)}
            </View>
          : <View style={{ flex: 1, minWidth: 0 }}>{children}</View>}
        <Button compactRefresh label={t("refresh")} onPress={onRefresh} />
      </View>
      {fuel && firstCount < fuelChoices.length &&
        <View testID="fuel-second-row" style={[s.headingRow, { alignItems: "stretch", flexWrap: "wrap" }]}>
          {fuelChoices.slice(firstCount).map(choice)}
        </View>}
      {fuel && <View pointerEvents="none" aria-hidden importantForAccessibility="no-hide-descendants"
        style={{ position: "absolute", left: 0, top: 0, opacity: 0, alignItems: "flex-start" }}>
        {fuelChoices.map(value => <View key={value} onLayout={event => {
          const width = event.nativeEvent.layout.width;
          setLabelWidths(previous => previous[value] === width ? previous : { ...previous, [value]: width });
        }}>
          <NativeText numberOfLines={1} allowFontScaling={false}
            style={{ fontSize: appFontSize(13, fontScale, 11) * systemScale, fontWeight: "600" }}>
            {t(value)}
          </NativeText>
        </View>)}
      </View>}
    </View>
  );
}
