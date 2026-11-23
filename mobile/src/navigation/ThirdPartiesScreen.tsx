import { useState } from "react";
import { Linking, View } from "react-native";
import Ionicons from "@expo/vector-icons/Ionicons";

import { Pressable, Text, useUI } from "../ui";
import { type Credit, dataCredits, photoCredits, softwareCredits, storeCredits } from "./thirdPartySources";

const sections = [
  { label: "creditData", credits: dataCredits },
  { label: "creditStores", credits: storeCredits },
  { label: "creditPhotos", credits: photoCredits },
  { label: "creditSoftware", credits: softwareCredits },
] as const;

function CreditLink({ label, url }: { label: string; url: string }) {
  const { styles: s } = useUI();
  return (
    <Pressable accessibilityRole="link" onPress={() => void Linking.openURL(url).catch(() => undefined)}>
      <Text style={[s.productName, { textDecorationLine: "underline" }]}>{label}</Text>
    </Pressable>
  );
}

function CreditRow({ credit }: { credit: Credit }) {
  const { t, styles: s } = useUI();
  const details = [credit.author, !credit.licenseUrl && credit.license, credit.resized && t("creditResized")]
    .filter(Boolean).join(" · ");
  return (
    <View style={{ gap: 3 }}>
      <CreditLink label={credit.name} url={credit.url} />
      {!!details && <Text style={s.meta}>{details}</Text>}
      {credit.license && credit.licenseUrl && <CreditLink label={credit.license} url={credit.licenseUrl} />}
    </View>
  );
}

export function ThirdPartiesScreen() {
  const { t, styles: s } = useUI();
  const [expanded, setExpanded] = useState<(typeof sections)[number]["label"] | null>(null);
  return (
    <View testID="third-parties-screen" style={{ gap: 10 }}>
      {sections.map(section => (
        <View key={section.label} style={s.panel}>
          <Pressable accessibilityRole="button" accessibilityLabel={t(section.label)}
            aria-expanded={expanded === section.label}
            onPress={() => setExpanded(expanded === section.label ? null : section.label)}
            style={[s.button, { flexDirection: "row", justifyContent: "space-between", gap: 12 }]}>
            <Text style={[s.productName, { flexShrink: 1 }]}>{t(section.label)}</Text>
            <Ionicons name={expanded === section.label ? "chevron-up" : "chevron-down"} size={17} color="#19562a" />
          </Pressable>
          {expanded === section.label && section.credits.map(credit => <CreditRow key={credit.url} credit={credit} />)}
        </View>
      ))}
    </View>
  );
}
