import { useEffect, useState } from "react";
import { ActivityIndicator, Modal, ScrollView, View } from "react-native";
import { LegalDocument } from "../legal/LegalDocument";
import { Button } from "../Action";
import { api, httpStatus } from "../api";
import { Pressable, Input, Text, useUI } from "../ui";
export function FeedbackScreen() {
  const { t, color } = useUI();
  const [privacyOpen, setPrivacyOpen] = useState(false);
  const [name, setName] = useState(""), [phone, setPhone] = useState(""),
    [email, setEmail] = useState(""), [message, setMessage] = useState(""),
    [available, setAvailable] = useState(false), [checking, setChecking] = useState(true),
    [busy, setBusy] = useState(false), [notice, setNotice] = useState<"feedbackAccepted" | "feedbackUnavailable" | "feedbackInvalid" | "feedbackWait" | "">("");
  useEffect(() => {
    const controller = new AbortController();
    api<{ available: boolean }>("/api/v1/feedback/availability", { signal: controller.signal })
      .then(r => { if (!controller.signal.aborted) setAvailable(r.available); })
      .catch(() => { if (!controller.signal.aborted) setAvailable(false); })
      .finally(() => { if (!controller.signal.aborted) setChecking(false); });
    return () => controller.abort();
  }, []);
  async function send() {
    if (busy || !available) return;
    if (!name.trim() || !/^[^\s<>@]+@[^\s<>@]+\.[^\s<>@]+$/.test(email.trim()) || message.trim().length < 10) {
      setNotice("feedbackInvalid"); return;
    }
    setBusy(true); setNotice("");
    try {
      const r = await api<{ status: string }>("/api/v1/feedback", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: name.trim(), phone: phone.trim() || null, email: email.trim(), message: message.trim() }),
      });
      if (r.status !== "accepted") throw new Error("Unaccepted feedback");
      setMessage(""); setNotice("feedbackAccepted");
    } catch (e) { setNotice(httpStatus(e) === 429 ? "feedbackWait" : "feedbackUnavailable"); }
    finally { setBusy(false); }
  }
  const fields = [
    { key: "feedbackName" as const, value: name, change: setName, limit: 120 },
    { key: "feedbackPhone" as const, value: phone, change: setPhone, limit: 40 },
    { key: "feedbackEmail" as const, value: email, change: setEmail, limit: 254 },
    { key: "feedbackMessage" as const, value: message, change: setMessage, limit: 5000 },
  ];
  return <View testID="feedback-screen" style={{ backgroundColor: color("#fff", true), gap: 14 }}>
    {fields.map(f => <View key={f.key} style={{ gap: 4 }}>
      <Text style={{ color: "#606a73", fontSize: 13 }}>{t(f.key)}</Text>
      <Input accessibilityLabel={t(f.key)} value={f.value} onChangeText={f.change}
        editable={!busy} maxLength={f.limit} multiline={f.key === "feedbackMessage"}
        keyboardType={f.key === "feedbackEmail" ? "email-address" : f.key === "feedbackPhone" ? "phone-pad" : "default"}
        autoCapitalize={f.key === "feedbackEmail" ? "none" : "sentences"}
        style={{ backgroundColor: color("#fff", true), color: "#111", borderWidth: 1, borderColor: "#aaa", borderRadius: 3,
          padding: 8, minHeight: f.key === "feedbackMessage" ? 110 : 44, textAlignVertical: "top" }} />
    </View>)}
    {checking && <ActivityIndicator color={color("#267133")} />}
    {!checking && !available && <Text style={{ color: "#606a73" }}>{t("feedbackUnavailable")}</Text>}
    {notice && <Text accessibilityRole="alert" style={{ color: notice === "feedbackAccepted" ? "#267133" : "#8a4200" }}>{t(notice)}</Text>}
    <Text style={{ color: "#606a73", fontSize: 12 }}>{t("feedbackPrivacy")}</Text>
    <Pressable accessibilityRole="link" onPress={() => setPrivacyOpen(true)} style={{ minHeight: 44, justifyContent: "center" }}>
      <Text style={{ color: "#19562a", textDecorationLine: "underline" }}>{t("privacy")}</Text>
    </Pressable>
    <Modal visible={privacyOpen} animationType="slide" onRequestClose={() => setPrivacyOpen(false)}>
      <ScrollView contentContainerStyle={{ padding: 16, paddingTop: 44, backgroundColor: color("#fff", true), gap: 12 }}>
        <Button label={t("closeLegal")} onPress={() => setPrivacyOpen(false)} />
        <LegalDocument kind="privacy" />
      </ScrollView>
    </Modal>
    <Pressable accessibilityRole="button" accessibilityState={{ disabled: busy || !available }}
      disabled={busy || !available} onPress={send}
      style={{ backgroundColor: "#268b28", alignSelf: "flex-start", minHeight: 44, justifyContent: "center", paddingHorizontal: 18, paddingVertical: 8, opacity: busy || !available ? .55 : 1 }}>
      <Text style={{ color: "#fff", fontSize: 17, fontWeight: "700" }}>{t(busy ? "feedbackSending" : "feedbackSend")}</Text>
    </Pressable>
  </View>;
}
