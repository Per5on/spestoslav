import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  useRef,
} from "react";
import {
  Text as NativeText,
  TextInput as NativeInput,
  TextProps,
  TextInputProps,
  StyleSheet,
  Platform,
  StyleProp,
  TextStyle,
  useWindowDimensions,
} from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { Language, languages, messages, MessageKey } from "./i18n";
import { appFontSize } from "./font";
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
        { fontSize: appFontSize(style.fontSize ?? 14, fontScale, 11) },
        style.lineHeight ? { lineHeight: style.lineHeight * fontScale + 1 } : null,
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
        { fontSize: appFontSize(style.fontSize ?? 16, fontScale, 16) },
      ]}
    />
  );
}

// Native text fitting plus an exact font-metric fallback for browser previews.
export function AutoFitLabel({
  label,
  style,
  baseSize = 14,
  intrinsic = false,
  allowWrap = false,
}: {
  label: string;
  style?: StyleProp<TextStyle>;
  baseSize?: number;
  intrinsic?: boolean;
  allowWrap?: boolean;
}) {
  const { fontScale } = useUI();
  const { fontScale: systemScale } = useWindowDimensions();
  const reference = useRef<React.ComponentRef<typeof NativeText>>(null);
  const [width, setWidth] = useState(0);
  useEffect(() => setWidth(0), [label, baseSize, fontScale, systemScale]);
  const desired = appFontSize(baseSize, fontScale, 11) * systemScale;
  let fitted = desired;
  if (
    !intrinsic &&
    Platform.OS === "web" &&
    typeof document !== "undefined" &&
    width > 0 &&
    reference.current
  ) {
    const node = reference.current as unknown as HTMLElement;
    const context = document.createElement("canvas").getContext("2d");
    if (context && node instanceof HTMLElement) {
      const font = window.getComputedStyle(node);
      context.font = `${font.fontWeight} ${desired}px ${font.fontFamily}`;
      const measured = context.measureText(label).width;
      if (measured > 0)
        fitted = Math.max(
          12,
          Math.min(desired, (desired * (width - 1)) / measured),
        );
    }
  }
  return (
    <NativeText
      ref={reference}
      onLayout={(e) => setWidth(e.nativeEvent.layout.width)}
      numberOfLines={allowWrap ? 2 : 1}
      allowFontScaling={false}
      {...(Platform.OS === "web"
        ? {}
        : {
            adjustsFontSizeToFit: !intrinsic,
            minimumFontScale: Math.min(1, 12 / desired),
          })}
      style={[style, { fontSize: fitted, flexShrink: 1 }]}
    >
      {label}
    </NativeText>
  );
}
