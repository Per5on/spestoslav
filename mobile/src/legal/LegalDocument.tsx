import { useState } from "react";
import { View } from "react-native";
import { Text, useUI } from "../ui";
import { Button } from "../Action";
import policies from "./policies.json";
export function LegalDocument({ kind }: { kind: "terms" | "privacy" }) {
  const { t, language, color } = useUI();
  const [documentLanguage, setDocumentLanguage] = useState<"bg" | "en">(language === "bg" ? "bg" : "en");
  const sections = kind === "privacy" ? policies.privacy[documentLanguage] : [
    ...policies.terms[documentLanguage],
    { title: documentLanguage === "bg" ? "Политика за поверителност" : "Privacy Policy", body: "" },
    ...policies.privacy[documentLanguage],
  ];
  return <View testID={`legal-${kind}`} style={{ gap: 14, backgroundColor: color("#fff", true) }}>
    <Text style={{ color: "#606a73" }}>{t("legalDraft")} · {policies.version}</Text>
    {!['bg', 'en'].includes(language) && <Text style={{ color: "#606a73" }}>{t("legalLanguages")}</Text>}
    <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 8 }}>
      <Button label="Български" onPress={() => setDocumentLanguage("bg")} primary={documentLanguage === "bg"} />
      <Button label="English" onPress={() => setDocumentLanguage("en")} primary={documentLanguage === "en"} />
    </View>
    {sections.map((section, i) => <View key={i} style={{ gap: 7 }}>
      <Text selectable style={{ fontSize: 16, fontWeight: "700", color: "#111" }}>{section.title}</Text>
      {!!section.body && <Text selectable style={{ fontSize: 14, lineHeight: 22, color: "#222" }}>{section.body}</Text>}
    </View>)}
  </View>;
}
