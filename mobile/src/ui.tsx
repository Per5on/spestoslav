import React, {
  createContext,
  useContext,
  useEffect,
  useMemo,
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
  Pressable as NativePressable,
  PressableProps,
  StyleProp,
  ImageStyle,
  ViewStyle,
  TextStyle,
  useWindowDimensions,
} from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { Language, languages, messages, MessageKey } from "./i18n";
import { preferencesKey } from "./localData";
import { appFontSize } from "./font";
import { appearanceColor, appearanceStyle, palettes } from "./appearance";
import { s } from "./styles";
type UI = {
  language: Language;
  setLanguage: (language: Language) => void;
  fontScale: number;
  setFontScale: (scale: number) => void;
  palette: number;
  setPalette: (palette: number) => void;
  dark: boolean;
  setDark: (dark: boolean) => void;
  styles: typeof s;
  color: (value: string, background?: boolean) => string;
  localStyle: <T extends ViewStyle | TextStyle | ImageStyle>(value: T) => T;
  t: (key: MessageKey) => string;
};
const Context = createContext<UI | null>(null);
export function UIProvider({ children }: { children: React.ReactNode }) {
  const [language, setLanguage] = useState<Language>("bg"),
    [fontScale, setFontScale] = useState(1),
    [loaded, setLoaded] = useState(false),
    [palette, setPalette] = useState(0),
    [dark, setDark] = useState(false);
  useEffect(() => {
    let alive = true;
    AsyncStorage.getItem(preferencesKey)
      .then((raw) => {
        if (!raw || !alive) return;
        const saved = JSON.parse(raw);
        if (languages.some((l) => l.code === saved.language))
          setLanguage(saved.language);
        if ([0.9, 1, 1.15, 1.3].includes(saved.fontScale))
          setFontScale(saved.fontScale);
        if (Number.isInteger(saved.palette) && saved.palette >= 0 && saved.palette < palettes.length)
          setPalette(saved.palette);
        if (typeof saved.dark === "boolean") setDark(saved.dark);
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
        preferencesKey,
        JSON.stringify({ language, fontScale, palette, dark }),
      ).catch(() => {});
  }, [loaded, language, fontScale, palette, dark]);
  const theme = useMemo(() => ({
    styles: Object.fromEntries(Object.entries(s).map(([key, value]) =>
      [key, appearanceStyle(StyleSheet.flatten(value), palette, dark)],
    )) as typeof s,
    color: (value: string, background = false) => appearanceColor(value, palette, dark, background),
    localStyle: <T extends ViewStyle | TextStyle | ImageStyle>(value: T) =>
      appearanceStyle(value, palette, dark),
  }), [palette, dark]);
  return (
    <Context.Provider
      value={{
        language,
        setLanguage,
        fontScale,
        setFontScale,
        palette, setPalette, dark, setDark, ...theme,
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
  const { fontScale, localStyle, dark } = useUI();
  const style = StyleSheet.flatten(props.style) || {};
  return (
    <NativeText
      {...props}
      style={[
        dark && { color: "#d4e4da" },
        localStyle(style),
        { fontSize: appFontSize(style.fontSize ?? 14, fontScale, 11) },
        style.lineHeight ? { lineHeight: style.lineHeight * fontScale + 1 } : null,
      ]}
    />
  );
}
export function Pressable({
  style, onFocus, onBlur, focusOutline = true, ...props
}: PressableProps & { focusOutline?: boolean }) {
  const { localStyle, color } = useUI();
  const [focused, setFocused] = useState(false);
  return (
    <NativePressable
      {...props}
      onFocus={(event) => {
        setFocused(true);
        onFocus?.(event);
      }}
      onBlur={(event) => {
        setFocused(false);
        onBlur?.(event);
      }}
      style={(state) => [
        localStyle(StyleSheet.flatten(typeof style === "function" ? style(state) : style) || {}),
        Platform.OS === "web" && {
          outlineStyle: "solid",
          outlineColor: color("#267133"),
          outlineWidth: focused && focusOutline ? 2 : 0,
        },
      ]}
    />
  );
}
export function Input(props: TextInputProps) {
  const { fontScale, localStyle, dark } = useUI();
  const style = StyleSheet.flatten(props.style) || {};
  return (
    <NativeInput
      {...props}
      placeholderTextColor={props.placeholderTextColor ?? (dark ? "#a9beb1" : undefined)}
      style={[
        dark && { color: "#d4e4da" },
        localStyle(style),
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
  const { fontScale, localStyle, dark } = useUI();
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
      style={[dark && { color: "#d4e4da" }, localStyle(StyleSheet.flatten(style) || {}), { fontSize: fitted, flexShrink: 1 }]}
    >
      {label}
    </NativeText>
  );
}
