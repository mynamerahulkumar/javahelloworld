/**
 * Supabase Client for Server-Side Usage (Next.js App Router)
 * 
 * Use this for server components, server actions, and route handlers.
 */
import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";
import { SupabaseUser, SupabaseSession } from "./types";

const supabaseUrlEnv = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseAnonKeyEnv = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

if (!supabaseUrlEnv || !supabaseAnonKeyEnv) {
  throw new Error(
    "Missing Supabase environment variables. " +
    "Please set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY in .env.local"
  );
}

const supabaseUrl: string = supabaseUrlEnv;
const supabaseAnonKey: string = supabaseAnonKeyEnv;

/**
 * Create a Supabase client for server-side usage
 */
export async function createClient() {
  const cookieStore = await cookies();

  return createServerClient(supabaseUrl, supabaseAnonKey, {
    cookies: {
      getAll() {
        return cookieStore.getAll();
      },
      setAll(cookiesToSet) {
        try {
          cookiesToSet.forEach(({ name, value, options }) =>
            cookieStore.set(name, value, options)
          );
        } catch {
          // The `setAll` method was called from a Server Component.
          // This can be ignored if you have middleware refreshing
          // user sessions.
        }
      },
    },
  });
}

/**
 * Get current user from Supabase session (server-side)
 */
export async function getCurrentUser(): Promise<SupabaseUser | null> {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  return user;
}

/**
 * Get current session from Supabase (server-side)
 */
export async function getCurrentSession(): Promise<SupabaseSession | null> {
  const supabase = await createClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();
  return session;
}






