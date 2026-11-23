import { View } from "react-native";
import * as Application from "expo-application";
import { Text, useUI } from "../ui";
import { Button } from "../Action";
export const OWNER_NOTICE = "© 2026 Vimp. All rights reserved.";
export function AboutScreen({ onFeedback, onThirdParties }: {
  onFeedback: () => void;
  onThirdParties: () => void;
}) {
  const { t, styles: s } = useUI();
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
      <Button label={t("thirdParties")} onPress={onThirdParties} />
    </View>
  );
}
