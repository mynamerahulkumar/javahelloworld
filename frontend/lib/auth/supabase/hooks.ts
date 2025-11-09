/**
 * Supabase Authentication Hooks
 * 
 * React hooks for Supabase authentication in client components
 */
"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { supabase, getCurrentUser, getCurrentSession, signInWithPassword, signOut, signUpWithPassword, resendConfirmationEmail, resetPassword, updatePassword } from "./client";
import { SupabaseUser, SupabaseSession } from "./types";
import { useAuthStore } from "@/store/auth";

function normalizeError(error: unknown, fallbackMessage: string): Error {
  if (error instanceof Error) {
    return error;
  }
  if (typeof error === "string") {
    return new Error(error);
  }
  if (
    error &&
    typeof error === "object" &&
    "message" in error &&
    typeof (error as { message?: unknown }).message === "string"
  ) {
    return new Error((error as { message: string }).message);
  }
  return new Error(fallbackMessage);
}

/**
 * Hook to get current Supabase user
 */
export function useUser(): {
  user: SupabaseUser | null;
  session: SupabaseSession | null;
  isLoading: boolean;
  error: Error | null;
} {
  const [user, setUser] = useState<SupabaseUser | null>(null);
  const [session, setSession] = useState<SupabaseSession | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const { setClientInfo, clearClientInfo } = useAuthStore();

  useEffect(() => {
    // Get initial session
    getCurrentSession()
      .then((session) => {
        setSession(session);
        const currentUser = session?.user || null;
        setUser(currentUser);
        
        // Sync client info from Supabase user metadata
        // Save email in client cache for order validation
        if (currentUser) {
          const clientId = currentUser.user_metadata?.client_id || null;
          // Use email from user object (primary) or from metadata (fallback)
          const clientEmail = currentUser.email || currentUser.user_metadata?.srp_client_email || null;
          setClientInfo(clientId, clientEmail);
        } else {
          clearClientInfo();
        }
        
        setIsLoading(false);
      })
      .catch((err) => {
        setError(err);
        clearClientInfo();
        setIsLoading(false);
      });

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
      const currentUser = session?.user || null;
      setUser(currentUser);
      
      // Sync client info from Supabase user metadata
      // Save email in client cache for order validation
      if (currentUser) {
        const clientId = currentUser.user_metadata?.client_id || null;
        // Use email from user object (primary) or from metadata (fallback)
        const clientEmail = currentUser.email || currentUser.user_metadata?.srp_client_email || null;
        setClientInfo(clientId, clientEmail);
      } else {
        clearClientInfo();
      }
      
      setIsLoading(false);
    });

    return () => {
      subscription.unsubscribe();
    };
  }, [setClientInfo, clearClientInfo]);

  return { user, session, isLoading, error };
}

/**
 * Hook for Supabase authentication functions
 */
export function useAuth() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);

  const signIn = useCallback(
    async (email: string, password: string) => {
      setIsLoading(true);
      try {
        const { user, session, error } = await signInWithPassword(email, password);
        if (error) {
          // Check for email confirmation errors
          const errorMessage = error.message.toLowerCase();
          if (errorMessage.includes("email not confirmed") || 
              errorMessage.includes("email_not_confirmed") ||
              errorMessage.includes("confirm your email")) {
            throw new Error("EMAIL_NOT_CONFIRMED");
          }
          throw error;
        }
        if (user && session) {
          // Wait a bit for the session to be fully established
          await new Promise(resolve => setTimeout(resolve, 100));
          router.refresh(); // Refresh to update server-side session
          return { user, session, error: null };
        }
        return { user: null, session: null, error: new Error("Sign in failed") };
      } catch (err) {
        const normalizedError = normalizeError(err, "Sign in failed");
        const isEmailNotConfirmed = normalizedError.message === "EMAIL_NOT_CONFIRMED";
        return {
          user: null,
          session: null,
          error: isEmailNotConfirmed ? new Error("EMAIL_NOT_CONFIRMED") : normalizedError,
        };
      } finally {
        setIsLoading(false);
      }
    },
    [router]
  );

  const signUp = useCallback(
    async (email: string, password: string, metadata?: Record<string, any>) => {
      setIsLoading(true);
      try {
        const { user, session, error } = await signUpWithPassword(email, password, metadata);
        if (error) {
          throw error;
        }
        return { user, session, error: null };
      } catch (err) {
        return {
          user: null,
          session: null,
          error: normalizeError(err, "Sign up failed"),
        };
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const logout = useCallback(async () => {
    setIsLoading(true);
    try {
      // Clear client info from store first
      useAuthStore.getState().clearClientInfo();
      
      // Sign out from Supabase
      const { error } = await signOut();
      
      // Always redirect to login, even if there's an error
      router.push("/login");
      router.refresh();
      
      // Wait a bit to ensure navigation happens
      await new Promise(resolve => setTimeout(resolve, 100));
      
      if (error) {
        console.error("Supabase sign out error:", error);
        // Still return success since we've cleared local state and redirected
        return { error: null };
      }
      
      return { error: null };
    } catch (err) {
      console.error("Logout error:", err);
      // Still redirect even on error
      router.push("/login");
      router.refresh();
      return {
        error: normalizeError(err, "Sign out failed"),
      };
    } finally {
      setIsLoading(false);
    }
  }, [router]);

  const resendConfirmation = useCallback(
    async (email: string) => {
      setIsLoading(true);
      try {
        const { error } = await resendConfirmationEmail(email);
        if (error) {
          throw error;
        }
        return { error: null };
      } catch (err) {
        return {
          error: normalizeError(err, "Failed to resend confirmation email"),
        };
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const forgotPassword = useCallback(
    async (email: string) => {
      setIsLoading(true);
      try {
        const { error } = await resetPassword(email);
        if (error) {
          throw error;
        }
        return { error: null };
      } catch (err) {
        return {
          error: normalizeError(err, "Failed to send password reset email"),
        };
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const changePassword = useCallback(
    async (newPassword: string) => {
      setIsLoading(true);
      try {
        const { error } = await updatePassword(newPassword);
        if (error) {
          throw error;
        }
        return { error: null };
      } catch (err) {
        return {
          error: normalizeError(err, "Failed to update password"),
        };
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  return {
    signIn,
    signUp,
    logout,
    resendConfirmation,
    forgotPassword,
    changePassword,
    isLoading,
  };
}

