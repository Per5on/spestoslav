import React, { useEffect, useState } from "react";
import { View } from "react-native";
import * as Application from "expo-application";
import { Text, useUI } from "../ui";
import { Button } from "../Action";
import { s } from "../styles";
import { api } from "../api";
export const OWNER_NOTICE = "© 2026 Vimp. All rights reserved.";
export function AboutScreen({ onFeedback }: { onFeedback: () => void }) {
  const { t } = useUI();
  const [credits, setCredits] = useState<{ code: string; author: string; license: string; source_url: string }[]>([]);
  useEffect(() => {
    const controller = new AbortController();
    api<typeof credits>("/api/v1/demo/credits", { signal: controller.signal }).then(rows => {
      if (!controller.signal.aborted) setCredits(rows.filter(r => r.source_url.startsWith("https://commons.wikimedia.org/")));
    }).catch(() => {});
    return () => controller.abort();
  }, []);
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
      {credits.map(row => <Text key={row.code} style={s.meta}>
        {row.code}: {row.author} · {row.license}{"\n"}{row.source_url}
      </Text>)}
    </View>
  );
}
