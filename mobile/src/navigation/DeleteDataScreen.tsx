import { Alert, Platform, View } from "react-native";
import { Button } from "../Action";
import { Text, useUI } from "../ui";
import { useSession } from "../workflows/session";

import type { CloudErasure } from "../localData";
type Props = { onErase: (cloud: Promise<CloudErasure>) => void };

export function DeleteDataScreen({ onErase }: Props) {
  const { t, styles: s } = useUI();
  const { eraseServerData } = useSession();
  function confirm() {
    const erase = () => onErase(eraseServerData());
    if (Platform.OS === "web") {
      if (window.confirm(t("deleteDataConfirm"))) erase();
    } else {
      Alert.alert(t("deleteData"), t("deleteDataConfirm"), [
        { text: t("cancel"), style: "cancel" },
        { text: t("deleteData"), style: "destructive", onPress: erase },
      ]);
    }
  }
  return (
    <View style={s.panel}>
      <Text style={s.meta}>{t("deleteDataHelp")}</Text>
      <Button label={t("deleteData")} onPress={confirm} />
    </View>
  );
}
