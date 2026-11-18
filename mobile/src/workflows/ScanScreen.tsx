import React, { useEffect, useRef, useState } from "react";
import { AppState, ActivityIndicator, Linking, View } from "react-native";
import { useCameraPermissions } from "./cameraPermissions";
import { BarcodeCamera } from "./BarcodeCamera";
import { decodeBarcodeImage } from "./scanImage";
import * as ImagePicker from "expo-image-picker";
import { api, httpStatus } from "../api";
import { Product } from "../catalog/model";
import { Text, Input, useUI } from "../ui";
import { Button } from "../Action";
import { useSession } from "./session";
import { validGTIN } from "./barcode";
export function ScanScreen({ onAdd }: { onAdd: (p: Product) => boolean }) {
  const { t, styles: s } = useUI(),
    session = useSession();
  const [permission, requestPermission] = useCameraPermissions();
  const [camera, setCamera] = useState(false),
    [active, setActive] = useState(AppState.currentState === "active"),
    [barcode, setBarcode] = useState(""),
    [busy, setBusy] = useState(false),
    [found, setFound] = useState<Product | null>(null),
    [notice, setNotice] = useState<
      | ""
      | "invalidBarcode"
      | "unknownBarcode"
      | "searchError"
      | "cameraError"
      | "cameraDenied"
      | "noBarcodeInImage"
      | "identificationSent"
      | "added"
    >(""),
    [sent, setSent] = useState(false);
  const lock = useRef(false),
    controller = useRef<AbortController | null>(null),
    mounted = useRef(true);
  useEffect(() => {
    mounted.current = true;
    const sub = AppState.addEventListener("change", (v) =>
      setActive(v === "active"),
    );
    return () => {
      mounted.current = false;
      sub.remove();
      controller.current?.abort();
    };
  }, []);
  async function find(code: string) {
    if (lock.current) return;
    if (!validGTIN(code)) {
      setNotice("invalidBarcode");
      return;
    }
    lock.current = true;
    setBarcode(code);
    setCamera(false);
    setFound(null);
    setSent(false);
    setNotice("");
    setBusy(true);
    const abort = new AbortController();
    controller.current = abort;
    try {
      const product = await api<Product>("/api/v1/products/barcode/" + code, {
        signal: abort.signal,
      });
      if (mounted.current) setFound(product);
    } catch (e) {
      if (mounted.current && !abort.signal.aborted)
        setNotice(httpStatus(e) === 404 ? "unknownBarcode" : "searchError");
    } finally {
      lock.current = false;
      if (mounted.current) setBusy(false);
    }
  }
  async function startCamera() {
    try {
      const p = permission?.granted ? permission : await requestPermission();
      if (p.granted) {
        setCamera(true);
        setNotice("");
      } else {
        setNotice("cameraDenied");
      }
    } catch {
      setNotice("cameraError");
    }
  }
  async function fromImage() {
    try {
      const image = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ["images"],
        quality: 1,
        exif: false,
      });
      if (image.canceled) return;
      const code = await decodeBarcodeImage(image.assets[0].uri);
      if (code) await find(code);
      else setNotice("noBarcodeInImage");
    } catch (error) {
      // Keep the real native picker/decoder failure visible in CI logcat.
      // Do not log the selected image URI or any user-owned media metadata.
      console.warn("Image barcode scan failed:", error instanceof Error ? error.message : String(error));
      setNotice("cameraError");
    }
  }
  async function identify() {
    setBusy(true);
    try {
      await session.request("/api/v1/product-identification-requests", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ barcode }),
      });
      setSent(true);
      setNotice("identificationSent");
    } catch {
      setNotice("searchError");
    } finally {
      if (mounted.current) setBusy(false);
    }
  }
  return (
    <View style={{ gap: 12 }}>
      <Text style={s.meta}>{t("scanHelp")}</Text>
      <View style={s.row}>
        <Button label={t("openCamera")} disabled={busy} onPress={startCamera} />
        <Button label={t("scanImage")} disabled={busy} onPress={fromImage} />
      </View>
      {permission && !permission.granted && !permission.canAskAgain && (
        <>
          <Text style={s.notice}>{t("cameraDenied")}</Text>
          <Button
            label={t("openSettings")}
            onPress={() => {
              Linking.openSettings().catch(() => setNotice("cameraError"));
            }}
          />
        </>
      )}
      {camera && permission?.granted && active && (
        <>
          <BarcodeCamera
            onCode={(code) => {
              void find(code);
            }}
            onError={() => {
              setCamera(false);
              setNotice("cameraError");
            }}
          />
          <Button label={t("cancel")} onPress={() => setCamera(false)} />
        </>
      )}
      <Input
        accessibilityLabel={t("barcode")}
        value={barcode}
        editable={!busy}
        onChangeText={(value) => {
          setBarcode(value);
          setFound(null);
          setNotice("");
          setSent(false);
        }}
        keyboardType="number-pad"
        maxLength={14}
        style={s.input}
        placeholder={t("barcodePlaceholder")}
      />
      <Button
        primary
        label={t(busy ? "searching" : "findProduct")}
        disabled={busy}
        onPress={() => find(barcode.trim())}
      />
      {busy && <ActivityIndicator />}
      {notice && (
        <Text accessibilityRole="alert" style={s.notice}>
          {t(notice)}
        </Text>
      )}
      {found && (
        <View style={s.panel}>
          <Text style={s.productName}>{found.name}</Text>
          <Text style={s.meta}>
            {found.package_quantity} {found.package_unit}
          </Text>
          <Button
            primary
            label={t("add")}
            onPress={() => {
              if (onAdd(found)) setNotice("added");
            }}
          />
        </View>
      )}
      {notice === "unknownBarcode" &&
        !sent &&
        (session.user ? (
          <Button
            label={t("requestIdentification")}
            disabled={busy}
            onPress={identify}
          />
        ) : (
          <Text style={s.meta}>{t("identifyLogin")}</Text>
        ))}
    </View>
  );
}
