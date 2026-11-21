import { useRef, useState } from "react";
import { Modal, ScrollView, View, useWindowDimensions } from "react-native";
import { Button } from "../Action";
import { Pressable, Text, useUI } from "../ui";

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
  const anchor = useRef<View>(null);
  const { height } = useWindowDimensions();
  const [popupTop, setPopupTop] = useState<number | null>(null);
  const close = () => setPopupTop(null);
  const foodRows = [groups.slice(0, 3), groups.slice(3, 6)];
  const rows = technology
    ? technologyRows.map(codes => codes.flatMap(code => groups.filter(group => group.code === code)))
    : foodRows;
  const shown = new Set(rows.flat().map(group => group.code));
  const overflow = groups.filter(group => !shown.has(group.code));
  const menuHeight = Math.min(14 + overflow.length * 48, height - 24);
  function open() {
    anchor.current?.measureInWindow((_x, y, _width, buttonHeight) => {
      const below = y + buttonHeight + 4;
      setPopupTop(below + menuHeight <= height - 12 ? below : Math.max(12, y - menuHeight - 4));
    });
  }
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
            <View ref={anchor} collapsable={false}>
              <Button label="⋯" accessibilityLabel={t("moreGroups")} expanded={popupTop !== null}
                primary={overflow.some(group => group.code === selected)} onPress={open} />
            </View>}
        </View>
      ))}
      <Modal transparent visible={popupTop !== null} onRequestClose={close}>
        <View style={{ flex: 1 }}>
          <Pressable accessibilityRole="button" accessibilityLabel={t("cancel")}
            style={s.menuBackdrop} onPress={close} />
          <View accessibilityRole="menu" style={[s.menu, { top: popupTop ?? 12, maxHeight: menuHeight }]}>
            <ScrollView keyboardShouldPersistTaps="handled">
              {overflow.map(group => (
                <Pressable key={group.code ?? "all"} accessibilityRole="menuitem"
                  accessibilityLabel={group.label} accessibilityState={{ selected: group.code === selected }}
                  style={s.menuItem} onPress={() => { close(); onSelect(group.code); }}>
                  <Text style={s.menuText}>{group.label}</Text>
                </Pressable>
              ))}
            </ScrollView>
          </View>
        </View>
      </Modal>
    </View>
  );
}
