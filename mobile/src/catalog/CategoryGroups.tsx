import { useState } from "react";
import { ScrollView, View } from "react-native";
import { Button } from "../Action";
import { useUI } from "../ui";

type Group = { code: string | null; label: string };
const technologyRows = [
  [null, "tv-computing"],
  ["smart-home-mobility", "small-appliances", "major-appliances"],
];

export function CategoryGroups({ technology, groups, selected, onSelect }: {
  technology: boolean;
  groups: Group[];
  selected: string | null;
  onSelect: (code: string | null) => void;
}) {
  const { t, styles: s } = useUI();
  const [expanded, setExpanded] = useState(false);
  const foodRows = [groups.slice(0, 3), groups.slice(3, 6)];
  const rows = technology
    ? technologyRows.map(codes => codes.flatMap(code => groups.filter(group => group.code === code)))
    : foodRows;
  const shown = new Set(rows.flat().map(group => group.code));
  const overflow = groups.filter(group => !shown.has(group.code));
  function render(group: Group) {
    return <Button key={group.code ?? "all"} label={group.label} labelSize={13}
      primary={selected === group.code} onPress={() => onSelect(group.code)} />;
  }
  return (
    <View testID="category-groups" style={{ gap: 6 }}>
      {rows.map((row, index) => (
        <View key={index} style={s.headingRow}>
          <ScrollView horizontal keyboardShouldPersistTaps="handled"
            style={{ flex: 1 }} contentContainerStyle={{ flexGrow: 1, gap: 6 }}>
            {row.map(render)}
          </ScrollView>
          {index === 1 && overflow.length > 0 &&
            <Button label="⋯" accessibilityLabel={t("moreGroups")} expanded={expanded}
              primary={overflow.some(group => group.code === selected)}
              onPress={() => setExpanded(value => !value)} />}
        </View>
      ))}
      {expanded && <View style={s.row}>{overflow.map(render)}</View>}
    </View>
  );
}
