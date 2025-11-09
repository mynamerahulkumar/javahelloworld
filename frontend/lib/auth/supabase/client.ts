/**
 * Supabase Client for Client-Side Usage
 * 
 * Use this for client components that need to interact with Supabase.
 */
"use client";

import { createBrowserClient } from "@supabase/ssr";
import { SupabaseUser, SupabaseSession } from "./types";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error(
    "Missing Supabase environment variables. " +
    "Please set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY in .env.local"
  );
}

export const supabase = createBrowserClient(supabaseUrl, supabaseAnonKey);

/**
 * Get current user from Supabase session
 */
export async function getCurrentUser(): Promise<SupabaseUser | null> {
  const {
    data: { user },
  } = await supabase.auth.getUser();
  return user;
}

/**
 * Get current session from Supabase
 */
export async function getCurrentSession(): Promise<SupabaseSession | null> {
  const {
    data: { session },
  } = await supabase.auth.getSession();
  return session;
}

/**
 * Sign in with email and password
 */
export async function signInWithPassword(
  email: string,
  password: string
): Promise<{ user: SupabaseUser | null; session: SupabaseSession | null; error: Error | null }> {
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password,
  });

  return {
    user: data.user,
    session: data.session,
    error: error ? new Error(error.message) : null,
  };
}

/**
 * Sign out current user
 */
export async function signOut(): Promise<{ error: Error | null }> {
  const { error } = await supabase.auth.signOut();
  return {
    error: error ? new Error(error.message) : null,
  };
}

/**
 * Sign up with email and password
 */
export async function signUpWithPassword(
  email: string,
  password: string,
  metadata?: Record<string, any>
): Promise<{ user: SupabaseUser | null; session: SupabaseSession | null; error: Error | null }> {
  const { data, error } = await supabase.auth.signUp({
    email,
    password,
    options: {
      data: metadata,
    },
  });

  return {
    user: data.user,
    session: data.session,
    error: error ? new Error(error.message) : null,
  };
}

/**
 * Resend email confirmation
 */
export async function resendConfirmationEmail(
  email: string
): Promise<{ error: Error | null }> {
  const { error } = await supabase.auth.resend({
    type: 'signup',
    email,
  });

  return {
    error: error ? new Error(error.message) : null,
  };
}

/**
 * Send password reset email
 */
export async function resetPassword(
  email: string
): Promise<{ error: Error | null }> {
  const { error } = await supabase.auth.resetPasswordForEmail(email, {
    redirectTo: `${window.location.origin}/reset-password`,
  });

  return {
    error: error ? new Error(error.message) : null,
  };
}

/**
 * Update password (for password reset flow)
 */
export async function updatePassword(
  newPassword: string
): Promise<{ error: Error | null }> {
  const { error } = await supabase.auth.updateUser({
    password: newPassword,
  });

  return {
    error: error ? new Error(error.message) : null,
  };
}


