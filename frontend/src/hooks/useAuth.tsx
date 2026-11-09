import { useCallback, useEffect, useMemo, useState, type ReactNode } from "react";
import { getToken, request, setToken } from "@/lib/api";
import type { User } from "@/lib/types";
import { AuthContext } from "@/hooks/authContext";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  /**
   * A token in localStorage is not proof of anything: it may be expired, or
   * belong to an account that has since been disabled. The only way to know
   * is to ask, so the application starts by asking and treats a 401 as
   * signed out rather than as an error worth showing.
   */
  useEffect(() => {
    if (!getToken()) {
      setLoading(false);
      return;
    }
    let cancelled = false;
    request<User>("/users/me")
      .then((me) => {
        if (!cancelled) setUser(me);
      })
      .catch(() => {
        if (!cancelled) {
          setToken(null);
          setUser(null);
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const signIn = useCallback(async (email: string, password: string) => {
    const { access_token } = await request<{ access_token: string }>("/auth/login", {
      method: "POST",
      body: { email, password },
    });
    setToken(access_token);
    setUser(await request<User>("/users/me"));
  }, []);

  const register = useCallback(
    async (email: string, password: string) => {
      await request<User>("/users", { method: "POST", body: { email, password } });
      // Registering does not sign you in - the API returns the account, not
      // a token - so this signs in straight afterwards rather than leaving
      // the customer on a form they have just completed.
      await signIn(email, password);
    },
    [signIn],
  );

  const signOut = useCallback(() => {
    setToken(null);
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({ user, loading, signIn, register, signOut }),
    [user, loading, signIn, register, signOut],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
