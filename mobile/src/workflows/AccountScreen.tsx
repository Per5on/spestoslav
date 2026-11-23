import React, { useState } from "react";
import { Alert, Platform, View, ActivityIndicator } from "react-native";
import { api, httpStatus } from "../api";
import type { MessageKey } from "../i18n";
import { useSession } from "./session";
import { Button } from "../Action";
import { Input, Pressable, Text, useUI } from "../ui";

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
    { t, styles: s } = useUI();
  const [email, setEmail] = useState(""),
    [password, setPassword] = useState(""),
    [recovery, setRecovery] = useState<"email" | "code" | null>(null),
    [otp, setOtp] = useState(""),
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
  function changeRecovery(next: typeof recovery) {
    setPassword("");
    setOtp("");
    setNotice("");
    setRecovery(next);
  }
  async function recover() {
    if (!recovery) return;
    setBusy(true);
    setNotice("");
    try {
      const resetting = recovery === "code";
      await api<void>(resetting ? "/api/v1/auth/reset-password" : "/api/v1/auth/request-password-reset", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(resetting ? { email: email.trim(), otp, password } : { email: email.trim() }),
      });
      changeRecovery(resetting ? null : "code");
      setNotice(resetting ? "passwordResetDone" : "passwordCodeSent");
    } catch (error) {
      const status = httpStatus(error);
      setNotice(status === 429 ? "authRateLimited"
        : recovery === "code" && status === 400 ? "passwordCodeRejected"
        : "passwordResetUnavailable");
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
          {recovery && <Text style={s.productName}>{t("forgotPassword")}</Text>}
          {!recovery && <Text style={s.meta}>{t("accountPurpose")}</Text>}
          <Input
            accessibilityLabel={t("email")}
            placeholder={t("email")}
            value={email}
            onChangeText={setEmail}
            editable={!busy && recovery !== "code"}
            keyboardType="email-address"
            autoCapitalize="none"
            autoComplete="email"
            style={s.input}
          />
          {recovery === "code" && (
            <Input accessibilityLabel={t("passwordCode")} placeholder={t("passwordCode")}
              value={otp} onChangeText={setOtp} keyboardType="number-pad"
              autoComplete="one-time-code" maxLength={6} style={s.input} editable={!busy} />
          )}
          {recovery !== "email" && <Input
            accessibilityLabel={t(recovery ? "newPassword" : "password")}
            placeholder={t(recovery ? "newPassword" : "password")}
            value={password}
            onChangeText={setPassword}
            secureTextEntry
            autoComplete={register || recovery ? "new-password" : "current-password"}
            style={s.input}
            editable={!busy}
          />}
          {!register && !recovery && (
            <Pressable accessibilityRole="button" disabled={busy}
              onPress={() => changeRecovery("email")}
              style={{ alignSelf: "flex-end", minHeight: 44, justifyContent: "center" }}>
              <Text style={[s.meta, { textDecorationLine: "underline" }]}>{t("forgotPassword")}</Text>
            </Pressable>
          )}
          {recovery ? <>
            <Button primary label={t(busy ? "working" : recovery === "email" ? "sendPasswordCode" : "saveNewPassword")}
              disabled={busy || !email.trim().includes("@") ||
                (recovery === "code" && (!/^[0-9]{6}$/.test(otp) || password.length < 8))}
              onPress={recover} />
            {recovery === "code" && (
              <Button label={t("requestNewPasswordCode")} disabled={busy} onPress={() => changeRecovery("email")} />
            )}
            <Button label={t("backToSignIn")} disabled={busy} onPress={() => changeRecovery(null)} />
          </> : <>
          <Button
            primary
            label={t(busy ? "working" : register ? "register" : "login")}
            disabled={busy || password.length < 8 || !email.includes("@")}
            onPress={submit}
          />
          <Button
            label={t(register ? "haveAccount" : "createAccount")}
            disabled={busy}
            onPress={() => { setNotice(""); setRegister(!register); }}
          />
          </>}
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
