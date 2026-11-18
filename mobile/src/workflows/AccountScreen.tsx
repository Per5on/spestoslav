import React, { useState } from "react";
import { Alert, Platform, View, ActivityIndicator } from "react-native";
import { httpStatus } from "../api";
import type { MessageKey } from "../i18n";
import { useSession } from "./session";
import { Button } from "../Action";
import { Input, Text, useUI } from "../ui";
import { s } from "../styles";

/** Map the backend's distinct sign-in answers to specific, translated guidance. */
export function authMessage(error: unknown, register: boolean): MessageKey {
  const status = httpStatus(error);
  if (status === null || status === 502 || status === 503 || status === 504)
    return "authUnavailable";
  if (status === 403) return "authVerifyEmail";
  if (status === 409) return "authExists";
  if (status === 429) return "authRateLimited";
  if (status === 401 || (status === 400 && !register)) return "authRejected";
  return "authError";
}
function deleteMessage(error: unknown): MessageKey {
  const status = httpStatus(error);
  if (status === 409) return "deleteAccountBusy";
  if (status === 502) return "deleteAccountPartial";
  return "deleteAccountError";
}
export function AccountScreen() {
  const { user, ready, restoreUnavailable, retryRestore, signIn, signOut, deleteAccount } = useSession(),
    { t } = useUI();
  const [email, setEmail] = useState(""),
    [password, setPassword] = useState(""),
    [register, setRegister] = useState(false),
    [busy, setBusy] = useState(false),
    [notice, setNotice] = useState<MessageKey | "">("");
  async function submit() {
    setBusy(true);
    setNotice("");
    try {
      await signIn(email, password, register);
      setPassword("");
    } catch (error) {
      setNotice(authMessage(error, register));
    } finally {
      setBusy(false);
    }
  }
  async function leave() {
    setBusy(true);
    setNotice("");
    try {
      if (!(await signOut())) setNotice("signOutPending");
    } finally {
      setBusy(false);
    }
  }
  async function erase() {
    setBusy(true);
    setNotice("");
    try {
      await deleteAccount();
      setNotice("deleteAccountDone");
    } catch (error) {
      setNotice(deleteMessage(error));
    } finally {
      setBusy(false);
    }
  }
  function confirmErase() {
    if (Platform.OS === "web") {
      if (window.confirm(t("deleteAccountConfirm"))) void erase();
      return;
    }
    Alert.alert(t("deleteAccount"), t("deleteAccountConfirm"), [
      { text: t("cancel"), style: "cancel" },
      { text: t("deleteAccount"), style: "destructive", onPress: () => void erase() },
    ]);
  }
  if (!ready) return <ActivityIndicator />;
  return (
    <View style={s.panel}>
      {user ? (
        <>
          <Text style={s.productName}>{user.email}</Text>
          <Button label={t("signOut")} disabled={busy} onPress={leave} />
          <Button label={t("deleteAccount")} disabled={busy} onPress={confirmErase} />
        </>
      ) : (
        <>
          {restoreUnavailable && (
            <>
              <Text accessibilityRole="alert" style={s.notice}>{t("authUnavailable")}</Text>
              <Button label={t("retry")} onPress={() => void retryRestore()} />
            </>
          )}
          <Text style={s.meta}>{t("accountPurpose")}</Text>
          <Input
            accessibilityLabel={t("email")}
            placeholder={t("email")}
            value={email}
            onChangeText={setEmail}
            keyboardType="email-address"
            autoCapitalize="none"
            autoComplete="email"
            style={s.input}
          />
          <Input
            accessibilityLabel={t("password")}
            placeholder={t("password")}
            value={password}
            onChangeText={setPassword}
            secureTextEntry
            autoComplete={register ? "new-password" : "current-password"}
            style={s.input}
          />
          <Button
            primary
            label={t(busy ? "working" : register ? "register" : "login")}
            disabled={busy || password.length < 8 || !email.includes("@")}
            onPress={submit}
          />
          <Button
            label={t(register ? "haveAccount" : "createAccount")}
            disabled={busy}
            onPress={() => setRegister(!register)}
          />
        </>
      )}
      {notice !== "" && (
        <Text accessibilityRole="alert" style={s.notice}>
          {t(notice)}
        </Text>
      )}
    </View>
  );
}
