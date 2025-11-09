/**
 * Supabase Auth Provider
 * 
 * Provides Supabase authentication context to the application.
 * Note: Supabase handles session management via cookies automatically,
 * so we don't need a complex provider like Auth0.
 */
"use client";

import { ReactNode, useEffect } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "./client";

interface SupabaseProviderProps {
  children: ReactNode;
}

export function SupabaseProvider({ children }: SupabaseProviderProps) {
  const router = useRouter();

  useEffect(() => {
    // Listen for auth state changes and refresh router
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((event) => {
      // Refresh router on auth state changes to update server components
      if (event === "SIGNED_IN" || event === "SIGNED_OUT" || event === "TOKEN_REFRESHED") {
        router.refresh();
      }
    });

    return () => {
      subscription.unsubscribe();
    };
  }, [router]);

  return <>{children}</>;
}






