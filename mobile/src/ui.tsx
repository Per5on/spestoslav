import React, { createContext, useContext, useEffect, useState } from "react";
import {
  Text as NativeText,
  TextInput as NativeInput,
  TextProps,
  TextInputProps,
  StyleSheet,
} from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { Language, languages, messages, MessageKey } from "./i18n";
type UI = {
  language: Language;
  setLanguage: (language: Language) => void;
  fontScale: number;
  setFontScale: (scale: number) => void;
  t: (key: MessageKey) => string;
};
const Context = createContext<UI | null>(null);
export function UIProvider({ children }: { children: React.ReactNode }) {
  const [language, setLanguage] = useState<Language>("bg"),
    [fontScale, setFontScale] = useState(1),
    [loaded, setLoaded] = useState(false);
  useEffect(() => {
    let alive = true;
    AsyncStorage.getItem("spestovnik-preferences")
      .then((raw) => {
        if (!raw || !alive) return;
        const saved = JSON.parse(raw);
        if (languages.some((l) => l.code === saved.language))
          setLanguage(saved.language);
        if ([0.9, 1, 1.15, 1.3].includes(saved.fontScale))
          setFontScale(saved.fontScale);
      })
      .catch(() => {})
      .finally(() => {
        if (alive) setLoaded(true);
      });
    return () => {
      alive = false;
    };
  }, []);
  useEffect(() => {
    if (loaded)
      AsyncStorage.setItem(
        "spestovnik-preferences",
        JSON.stringify({ language, fontScale }),
      ).catch(() => {});
  }, [loaded, language, fontScale]);
  return (
    <Context.Provider
      value={{
        language,
        setLanguage,
        fontScale,
        setFontScale,
        t: (key) => messages[language][key],
      }}
    >
      {children}
    </Context.Provider>
  );
}
export function useUI() {
  const value = useContext(Context);
  if (!value) throw Error("UIProvider is required");
  return value;
}
export function Text(props: TextProps) {
  const { fontScale } = useUI();
  const style = StyleSheet.flatten(props.style) || {};
  return (
    <NativeText
      {...props}
      style={[
        props.style,
        { fontSize: Math.max(11, (style.fontSize ?? 14) * fontScale) },
        style.lineHeight ? { lineHeight: style.lineHeight * fontScale } : null,
      ]}
    />
  );
}
export function Input(props: TextInputProps) {
  const { fontScale } = useUI();
  const style = StyleSheet.flatten(props.style) || {};
  return (
    <NativeInput
      {...props}
      style={[
        props.style,
        { fontSize: Math.max(16, (style.fontSize ?? 16) * fontScale) },
      ]}
    />
  );
}
