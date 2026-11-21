import { useEffect, useState } from "react";
type Permission = { granted: boolean; canAskAgain: boolean };
export function useCameraPermissions() {
  const [permission, setPermission] = useState<Permission | null>(null);
  useEffect(() => {
    let alive = true;
    navigator.permissions
      ?.query({ name: "camera" as PermissionName })
      .then((value) => {
        if (alive)
          setPermission({
            granted: value.state === "granted",
            canAskAgain: value.state !== "denied",
          });
      })
      .catch(() => {
        if (alive) setPermission({ granted: false, canAskAgain: true });
      });
    return () => {
      alive = false;
    };
  }, []);
  async function request() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: false,
        video: true,
      });
      stream.getTracks().forEach((track) => track.stop());
      const value = { granted: true, canAskAgain: true };
      setPermission(value);
      return value;
    } catch {
      const value = { granted: false, canAskAgain: true };
      setPermission(value);
      return value;
    }
  }
  return [permission, request] as const;
}
