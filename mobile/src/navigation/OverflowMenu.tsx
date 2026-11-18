import { useState } from "react";
import { Modal, View } from "react-native";
import Ionicons from "@expo/vector-icons/Ionicons";
import { Pressable, Text, useUI } from "../ui";
import { overflowMenu, Screen } from "./menu";

export function OverflowMenu({ top, onSelect }: { top: number; onSelect: (screen: Screen) => void }) {
  const { t, styles: s, color } = useUI();
  const [open, setOpen] = useState(false);
  const close = () => setOpen(false);
  return (
    <>
      <Pressable
        accessibilityRole="button"
        accessibilityLabel={t("openMenu")}
        accessibilityState={{ expanded: open }}
        style={s.settingsButton}
        onPress={() => setOpen(true)}
      >
        <Ionicons name="ellipsis-vertical" size={25} color="#fff" />
      </Pressable>
      <Modal transparent visible={open} animationType="none" onRequestClose={close}>
        <View style={{ flex: 1 }}>
          <Pressable
            accessibilityRole="button"
            accessibilityLabel={t("cancel")}
            style={s.menuBackdrop}
            onPress={close}
          />
          <View accessibilityRole="menu" style={[s.menu, { top }]}>
            {overflowMenu.map(item => (
              <Pressable
                key={item.id}
                accessibilityRole="menuitem"
                accessibilityLabel={t(item.label)}
                style={s.menuItem}
                onPress={() => {
                  close();
                  onSelect(item.id);
                }}
              >
                <Ionicons name={item.icon} color={color("#19562a")} size={22} />
                <Text style={s.menuText}>{t(item.label)}</Text>
              </Pressable>
            ))}
          </View>
        </View>
      </Modal>
    </>
  );
}
