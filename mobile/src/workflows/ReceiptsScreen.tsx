import React, { useEffect, useRef, useState } from "react";
import {
  ActivityIndicator,
  Alert,
  Image,
  Platform,
  Pressable,
  View,
} from "react-native";
import * as ImagePicker from "expo-image-picker";
import * as FileSystem from "expo-file-system/legacy";
import { useSession } from "./session";
import { Button } from "../Action";
import { Text, useUI } from "../ui";
import { useCatalog } from "../catalog/useCatalog";
import { ReceiptItemReview } from "./ReceiptItemReview";
import { s } from "../styles";
type Summary = {
  id: string;
  status: string;
  created_at: string;
  branch_id: string | null;
};
type Receipt = {
  id: string;
  branch_id: string | null;
  status: string;
  extracted_text: string | null;
  items: {
    id: string;
    description: string;
    line_total_eur: string | null;
    status: string;
  }[];
};
export function ReceiptsScreen({
  localityId,
  onLogin,
}: {
  localityId: string | undefined;
  onLogin: () => void;
}) {
  const catalogue = useCatalog("groceries", localityId, false, false);
  const stores = catalogue.stores;
  const session = useSession(),
    { t } = useUI();
  const [rows, setRows] = useState<Summary[]>([]),
    [selected, setSelected] = useState<Receipt | null>(null),
    [draft, setDraft] = useState<ImagePicker.ImagePickerAsset | null>(null),
    [branch, setBranch] = useState<string | null>(null),
    [busy, setBusy] = useState(false),
    [error, setError] = useState(false),
    [submitted, setSubmitted] = useState(false),
    [note, setNote] = useState<
      "" | "receiptCameraDenied" | "receiptUploadedRefreshFailed"
    >("");
  const mounted = useRef(true),
    requestKey = useRef(""),
    draftRef = useRef<ImagePicker.ImagePickerAsset | null>(null);
  function discard() {
    const asset = draftRef.current;
    draftRef.current = null;
    setDraft(null);
    requestKey.current = "";
    if (
      asset?.uri &&
      FileSystem.cacheDirectory &&
      asset.uri.startsWith(FileSystem.cacheDirectory)
    )
      void FileSystem.deleteAsync(asset.uri, { idempotent: true }).catch(
        () => {},
      );
  }
  useEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
      const asset = draftRef.current;
      if (
        asset?.uri &&
        FileSystem.cacheDirectory &&
        asset.uri.startsWith(FileSystem.cacheDirectory)
      )
        void FileSystem.deleteAsync(asset.uri, { idempotent: true }).catch(
          () => {},
        );
    };
  }, []);
  async function load(quiet = false): Promise<boolean> {
    if (!quiet) {
      setError(false);
      setNote("");
      setBusy(true);
    }
    try {
      const r = await session.request<Summary[]>("/api/v1/receipts");
      if (mounted.current) setRows(r);
      return true;
    } catch {
      if (mounted.current && !quiet) setError(true);
      return false;
    } finally {
      if (mounted.current && !quiet) setBusy(false);
    }
  }
  useEffect(() => {
    setSubmitted(false);
  }, [selected?.id]);
  useEffect(() => {
    setRows([]);
    setSelected(null);
    discard();
    if (session.user) void load();
  }, [session.user?.id]);
  useEffect(() => {
    if (branch && !stores.some((s) => s.id === branch)) setBranch(null);
  }, [stores, branch]);
  async function pick(camera: boolean) {
    setError(false);
    setNote("");
    try {
      if (camera) {
        const p = await ImagePicker.requestCameraPermissionsAsync();
        if (!p.granted) {
          setNote("receiptCameraDenied");
          return;
        }
      }
      const result = await (
        camera
          ? ImagePicker.launchCameraAsync
          : ImagePicker.launchImageLibraryAsync
      )({ mediaTypes: ["images"], quality: 0.85, exif: false });
      if (result.canceled) return;
      const asset = result.assets[0];
      if (asset.fileSize && asset.fileSize > 8 * 1024 * 1024) {
        setError(true);
        return;
      }
      discard();
      draftRef.current = asset;
      setDraft(asset);
      requestKey.current =
        "receipt-" + Date.now() + "-" + Math.random().toString(36).slice(2);
    } catch {
      setError(true);
    }
  }
  async function upload() {
    if (!draft || busy) return;
    setBusy(true);
    setError(false);
    setNote("");
    let created: { id: string };
    try {
      const form = new FormData();
      if (Platform.OS === "web")
        form.append(
          "file",
          await (await fetch(draft.uri)).blob(),
          draft.fileName ?? "receipt.jpg",
        );
      else
        form.append("file", {
          uri: draft.uri,
          name: draft.fileName ?? "receipt.jpg",
          type: draft.mimeType ?? "image/jpeg",
        } as unknown as Blob);
      if (branch) form.append("branch_id", branch);
      created = await session.request<{ id: string }>("/api/v1/receipts", {
        method: "POST",
        headers: { "Idempotency-Key": requestKey.current },
        body: form,
      });
    } catch {
      // Nothing was accepted: keep the draft and its idempotency key so retrying cannot duplicate.
      if (mounted.current) {
        setError(true);
        setBusy(false);
      }
      return;
    }
    // From here the receipt exists on the server; a refresh problem must not look like a failed upload.
    if (!mounted.current) return;
    discard();
    let refreshed = false;
    try {
      const detailed = await session.request<Receipt>(
        "/api/v1/receipts/" + created.id,
      );
      if (mounted.current) setSelected(detailed);
      refreshed = await load(true);
    } catch {
      refreshed = false;
    }
    if (mounted.current) {
      if (!refreshed) setNote("receiptUploadedRefreshFailed");
      setBusy(false);
    }
  }
  async function detail(id: string) {
    setBusy(true);
    setError(false);
    try {
      const data = await session.request<Receipt>("/api/v1/receipts/" + id);
      if (mounted.current) setSelected(data);
    } catch {
      if (mounted.current) setError(true);
    } finally {
      if (mounted.current) setBusy(false);
    }
  }
  async function remove(id: string) {
    setBusy(true);
    setError(false);
    try {
      await session.request<void>("/api/v1/receipts/" + id, {
        method: "DELETE",
      });
      if (mounted.current) {
        setSelected(null);
        await load();
      }
    } catch {
      if (mounted.current) setError(true);
    } finally {
      if (mounted.current) setBusy(false);
    }
  }
  const status = (value: string) =>
    t(
      value === "DELETING"
        ? "receiptDeleting"
        : value === "NEEDS_REVIEW"
          ? "receiptReview"
          : value === "FAILED"
            ? "receiptFailed"
            : value === "PROCESSING"
              ? "receiptProcessing"
              : "receiptQueued",
    );
  if (!session.ready) return <ActivityIndicator />;
  if (!session.user)
    return (
      <View style={s.panel}>
        <Text style={s.meta}>{t("receiptLogin")}</Text>
        <Button primary label={t("login")} onPress={onLogin} />
      </View>
    );
  return (
    <View style={{ gap: 12 }}>
      <Text style={s.meta}>{t("receiptPrivacy")}</Text>
      <View style={s.row}>
        <Button
          label={t("takeReceipt")}
          disabled={busy}
          onPress={() => pick(true)}
        />
        <Button
          label={t("chooseReceipt")}
          disabled={busy}
          onPress={() => pick(false)}
        />
      </View>
      {draft && (
        <View style={s.panel}>
          <Image
            accessibilityLabel={t("receiptPreview")}
            source={{ uri: draft.uri }}
            style={{ height: 220, width: "100%", resizeMode: "contain" }}
          />
          <Text style={s.meta}>{t("receiptBranch")}</Text>
          <Pressable
            style={s.choice}
            accessibilityRole="radio"
            accessibilityState={{ checked: !branch }}
            aria-checked={!branch}
            onPress={() => setBranch(null)}
          >
            <Text>{t("branchUnknown")}</Text>
          </Pressable>
          {stores.map((store) => (
            <Pressable
              key={store.id}
              style={[s.choice, branch === store.id && s.selectedChoice]}
              accessibilityRole="radio"
              accessibilityState={{ checked: branch === store.id }}
              aria-checked={branch === store.id}
              onPress={() => setBranch(store.id)}
            >
              <Text>
                {store.retailer_name} · {store.address}
              </Text>
            </Pressable>
          ))}
          <Button
            primary
            label={t("uploadReceipt")}
            disabled={busy}
            onPress={upload}
          />
          <Button label={t("cancel")} disabled={busy} onPress={discard} />
        </View>
      )}
      <Button
        label={t("refresh")}
        disabled={busy}
        onPress={() => {
          if (selected) void detail(selected.id);
          else void load();
        }}
      />
      {submitted && <Text style={s.notice}>{t("receiptSubmitted")}</Text>}
      {busy && <ActivityIndicator />}
      {error && (
        <Text accessibilityRole="alert" style={s.notice}>
          {t("receiptError")}
        </Text>
      )}
      {note !== "" && (
        <Text accessibilityRole="alert" style={s.notice}>
          {t(note)}
        </Text>
      )}
      {selected && (
        <View style={s.panel}>
          <Text style={s.productName}>{status(selected.status)}</Text>
          <Text style={s.meta}>{t("receiptReviewHelp")}</Text>
          {selected.items.map((item) => (
            <View key={item.id}>
              <Text>{item.description}</Text>
              {item.line_total_eur && (
                <Text style={s.meta}>
                  {item.line_total_eur} EUR · {t("unverified")}
                </Text>
              )}
              {item.status === "UNMATCHED" &&
                selected.status === "NEEDS_REVIEW" && (
                  <ReceiptItemReview
                    receiptId={selected.id}
                    itemId={item.id}
                    receiptBranch={selected.branch_id}
                    products={catalogue.products}
                    stores={stores}
                    onSubmitted={async () => {
                      setSubmitted(true);
                      await detail(selected.id);
                    }}
                  />
                )}
              {item.status === "PENDING_REVIEW" && (
                <Text style={s.meta}>{t("receiptSubmitted")}</Text>
              )}
              {item.status === "VERIFIED" && (
                <Text style={s.meta}>{t("receiptVerified")}</Text>
              )}
              {item.status === "REJECTED" && (
                <Text style={s.meta}>{t("receiptRejected")}</Text>
              )}
            </View>
          ))}
          {selected.extracted_text && (
            <Text selectable style={s.meta}>
              {selected.extracted_text}
            </Text>
          )}
          <Button
            label={t("deleteReceipt")}
            disabled={busy || selected.status === "PROCESSING"}
            onPress={() => {
              if (Platform.OS === "web") {
                if (window.confirm(t("deleteReceiptConfirm")))
                  void remove(selected.id);
              } else
                Alert.alert(t("deleteReceipt"), t("deleteReceiptConfirm"), [
                  { text: t("cancel"), style: "cancel" },
                  {
                    text: t("deleteReceipt"),
                    style: "destructive",
                    onPress: () => remove(selected.id),
                  },
                ]);
            }}
          />
        </View>
      )}
      {!rows.length && !busy && <Text style={s.meta}>{t("noReceipts")}</Text>}
      {rows.map((row) => (
        <Button
          key={row.id}
          label={
            new Date(row.created_at).toLocaleDateString() +
            " · " +
            status(row.status)
          }
          disabled={busy}
          onPress={() => detail(row.id)}
        />
      ))}
    </View>
  );
}
