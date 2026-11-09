import { createContext, useContext } from "react";
import type { User } from "@/lib/types";

/**
 * The auth context and its hook, kept apart from the provider component.
 *
 * Not a stylistic split: a module that exports both a component and a
 * plain function cannot be hot-reloaded reliably, because React Refresh
 * cannot tell which exports are components. Splitting them means editing
 * a page keeps its state instead of remounting the whole tree.
 */
export type AuthValue = {
  user: User | null;
  /** True until the stored token has been checked against the API. */
  loading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  signOut: () => void;
};

export const AuthContext = createContext<AuthValue | null>(null);

export function useAuth(): AuthValue {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth must be used inside AuthProvider");
  return value;
}
