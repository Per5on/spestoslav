import { useState } from "react";
import { Pressable } from "react-native";
import { AutoFitLabel } from "./ui";
import { s } from "./styles";
export function Button({
  label,
  onPress,
  primary = false,
  disabled = false,
  layout,
  expanded,
  labelSize = 14,
  refreshOutline = false,
}: {
  label: string;
  onPress: () => void;
  primary?: boolean;
  disabled?: boolean;
  layout?: "equal" | "snug";
  expanded?: boolean;
  labelSize?: number;
  refreshOutline?: boolean;
}) {
  const [focused, setFocused] = useState(false);
  return (
    <Pressable
      accessibilityRole="button"
      disabled={disabled}
      accessibilityState={{ disabled, expanded }}
      aria-expanded={expanded}
      onPress={onPress}
      onFocus={() => setFocused(true)}
      onBlur={() => setFocused(false)}
      style={[
        s.button,
        layout === "equal" && {
          flexBasis: 0,
          flexGrow: 1,
          minWidth: 0,
          paddingHorizontal: 2,
        },
        layout === "snug" && {
          flexGrow: 0,
          flexShrink: 0,
          paddingHorizontal: refreshOutline ? 7 : 0.25,
          minWidth: 44,
          maxWidth: "34%",
        },
        primary && s.primary,
        refreshOutline && { borderWidth: 1, borderColor: "#267133", outlineWidth: 0 },
        refreshOutline && focused && { backgroundColor: "#dbead3" },
        disabled && { opacity: 0.45 },
      ]}
    >
      <AutoFitLabel
        label={label}
        intrinsic={layout === "snug" && !refreshOutline}
        allowWrap={true}
        baseSize={labelSize}
        style={{
          color: primary ? "#fff" : "#19562a",
          fontWeight: "600",
          textAlign: "center",
        }}
      />
    </Pressable>
  );
}
