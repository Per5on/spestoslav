import { Linking, View } from "react-native";
import * as Application from "expo-application";
import { Pressable, Text, useUI } from "../ui";
import { Button } from "../Action";
import { s } from "../styles";
import { sampleCredits } from "../catalog/samples";
export const OWNER_NOTICE = "© 2026 Vimp. All rights reserved.";
export function AboutScreen({ onFeedback }: { onFeedback: () => void }) {
  const { t } = useUI();
  // These are read from Android PackageInfo (versionName/versionCode), not config literals.
  const version = Application.nativeApplicationVersion,
    build = Application.nativeBuildVersion;
  return (
    <View testID="about-screen" style={s.panel}>
      <Text style={s.heading}>Спестовник</Text>
      <Text style={s.meta}>
        {version
          ? `${t("version")} ${version}${build ? ` (${build})` : ""}`
          : t("browserVersion")}
      </Text>
      <Text style={s.meta}>{OWNER_NOTICE}</Text>
      <Button label={t("feedback")} onPress={onFeedback} />
      {sampleCredits.map(row => (
        <View key={row.code}>
          <Pressable
            accessibilityRole="link"
            onPress={() => void Linking.openURL(row.source_url).catch(() => undefined)}
          >
            <Text style={[s.meta, { color: "#19562a", textDecorationLine: "underline" }]}>
              {row.name}
            </Text>
          </Pressable>
          <Text style={s.meta}>{row.author} · {row.license}</Text>
        </View>
      ))}
    </View>
  );
}
