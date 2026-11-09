import { createContext, useContext } from "react";

/** See authContext for why the hook lives apart from the provider. */
export type ToastTone = "success" | "error" | "info";

export type ToastValue = { show: (tone: ToastTone, message: string) => void };

export const ToastContext = createContext<ToastValue | null>(null);

export function useToast(): ToastValue {
  const value = useContext(ToastContext);
  if (!value) throw new Error("useToast must be used inside ToastProvider");
  return value;
}
