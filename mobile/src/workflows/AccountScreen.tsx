import React, { useState } from "react";
import { View, ActivityIndicator } from "react-native";
import { useSession } from "./session";
import { Button } from "../Action";
import { Input, Text, useUI } from "../ui";
import { s } from "../styles";
export function AccountScreen() {
  const { user, ready, signIn, signOut } = useSession(),
    { t } = useUI();
  const [email, setEmail] = useState(""),
    [password, setPassword] = useState(""),
    [register, setRegister] = useState(false),
    [busy, setBusy] = useState(false),
    [error, setError] = useState(false);
  async function submit() {
    setBusy(true);
    setError(false);
    try {
      await signIn(email, password, register);
      setPassword("");
    } catch {
      setError(true);
    } finally {
      setBusy(false);
    }
  }
  if (!ready) return <ActivityIndicator />;
  return (
    <View style={s.panel}>
      {user ? (
        <>
          <Text style={s.productName}>{user.email}</Text>
          <Button
            label={t("signOut")}
            disabled={busy}
            onPress={() => {
              setBusy(true);
              signOut()
                .catch(() => setError(true))
                .finally(() => setBusy(false));
            }}
          />
        </>
      ) : (
        <>
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
      {error && (
        <Text accessibilityRole="alert" style={s.notice}>
          {t("authError")}
        </Text>
      )}
    </View>
  );
}
