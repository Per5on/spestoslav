import { contrastingInk } from "./appearance";
import { useState } from "react";
import { Pressable, AutoFitLabel, useUI } from "./ui";
export function Button({
  label,
  accessibilityLabel,
  onPress,
  primary = false,
  disabled = false,
  expanded,
  labelSize = 14,
  compactRefresh = false,
}: {
  label: string;
  accessibilityLabel?: string;
  onPress: () => void;
  primary?: boolean;
  disabled?: boolean;
  expanded?: boolean;
  labelSize?: number;
  compactRefresh?: boolean;
}) {
  const { styles: s, palette, color } = useUI();
  const [focused, setFocused] = useState(false);
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={accessibilityLabel}
      focusOutline={false}
      disabled={disabled}
      accessibilityState={{ disabled, expanded }}
      aria-expanded={expanded}
      onPress={onPress}
      onFocus={() => setFocused(true)}
      onBlur={() => setFocused(false)}
      style={[
        s.button,
        compactRefresh && {
          flexShrink: 0,
          paddingHorizontal: 7,
          minWidth: 44,
          maxWidth: "34%",
        },
        primary && s.primary,
        focused && { backgroundColor: primary ? "#de7300" : "#dbead3" },
        disabled && { opacity: 0.45 },
      ]}
    >
      <AutoFitLabel
        label={label}
        allowWrap={true}
        baseSize={labelSize}
        style={{
          color: primary ? (palette === 0 ? "#fff" : contrastingInk(color("#ff8500", true))) : "#19562a",
          fontWeight: "600",
          textAlign: "center",
        }}
      />
    </Pressable>
  );
}
