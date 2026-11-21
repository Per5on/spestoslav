import type { ImageStyle, TextStyle, ViewStyle } from "react-native";

// Keys retain the original zero-based IDs stored in user preferences.
export const palettes: Readonly<Record<number, {
  header: string;
  accent: string;
  tint: string;
  ink: string;
}>> = {
  0: { header: "#195b27", accent: "#ff8500", tint: "#edf3e5", ink: "#19562a" },
  5: { header: "#31445a", accent: "#3e6c53", tint: "#e9edf3", ink: "#30455c" },
  8: { header: "#b9ceac", accent: "#f2eee7", tint: "#f2eee7", ink: "#202820" },
  10: { header: "#022f40", accent: "#38aecc", tint: "#e0f3f7", ink: "#202820" },
  11: { header: "#a29f61", accent: "#383615", tint: "#efeedf", ink: "#202820" },
  12: { header: "#f7da83", accent: "#073368", tint: "#faf0d8", ink: "#202820" },
  14: { header: "#1B263B", accent: "#FF7F50", tint: "#fff0e8", ink: "#202820" },
  15: { header: "#1B263B", accent: "#F4C7C3", tint: "#F4C7C3", ink: "#202820" },
};

export function contrastingInk(background: string) {
  const value = background.slice(1);
  const channels = [0, 2, 4].map(offset => {
    const channel = parseInt(value.slice(offset, offset + 2), 16) / 255;
    return channel <= 0.04045 ? channel / 12.92 : ((channel + 0.055) / 1.055) ** 2.4;
  });
  const luminance = channels[0] * 0.2126 + channels[1] * 0.7152 + channels[2] * 0.0722;
  return luminance > 0.179 ? "#000" : "#fff";
}

const greens = new Set(["#19562a", "#234b2d", "#267133", "#1a5228", "#263e2d", "#243d2b", "#283f2e"]);
const pale = new Set(["#edf3e5", "#eaf1dd", "#eff4e8", "#dbead3"]);
const accentColors = new Set(["#ff8500", "#f48100", "#de7300"]);
const foreground = new Set(["#111", "#606a73", "#617363", "#526e4d", "#63816a", "#8a4200", "#855511"]);
const borders = new Set(["#d9e2d3", "#dce4d6", "#dfe5d8", "#dae2d6", "#edf0e9", "#e7ebdf", "#aaa"]);

export function appearanceColor(color: string, index: number, dark: boolean, background = false) {
  if (!dark && index === 0) return color;
  const palette = palettes[index] ?? palettes[0];
  const value = color.toLowerCase();
  if (value === "#195b27") return palette.header;
  if (accentColors.has(value)) {
    if (dark && !background) return "#ffc073";
    return dark && index === 0 ? "#9b4e00" : palette.accent;
  }
  if (pale.has(value)) return dark ? (value === "#dbead3" ? "#45564c" : "#293831") : palette.tint;
  if (dark && borders.has(value)) return "#53655b";
  if (background && dark && (value === "#fff" || value === "#ffffff")) return "#161e1a";
  if (background && dark && value === "#fff6e7") return "#392d1e";
  if (greens.has(value)) return dark && !background ? "#c1edcf" : palette.ink;
  if (dark && !background && foreground.has(value)) return "#d4e4da";
  return color;
}

export function appearanceStyle<T extends ViewStyle | TextStyle | ImageStyle>(style: T, index: number, dark: boolean): T {
  if (!dark && index === 0) return style;
  const themed = { ...style };
  for (const key of Object.keys(themed)) {
    const value = themed[key as keyof T];
    if (key.toLowerCase().endsWith("color") && typeof value === "string") {
      Object.assign(themed, { [key]: appearanceColor(value, index, dark, key === "backgroundColor") });
    }
  }
  return themed;
}
