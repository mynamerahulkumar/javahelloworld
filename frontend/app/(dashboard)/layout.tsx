"use client";

import { useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useUser, useAuth } from "@/lib/auth/supabase/hooks";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { cn } from "@/lib/utils";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const { user: supabaseUser, isLoading: supabaseLoading } = useUser();
  const { logout } = useAuth();

  // Check if user is authenticated via Supabase only
  const isAuthenticated = !!supabaseUser;

  useEffect(() => {
    if (!supabaseLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [isAuthenticated, supabaseLoading, router]);

  const handleLogout = async () => {
    try {
      const result = await logout();
      if (result?.error) {
        console.error("Logout error:", result.error);
        // Force redirect even if there's an error
        router.push("/login");
        router.refresh();
      }
    } catch (error) {
      console.error("Logout failed:", error);
      // Force redirect even if there's an error
      router.push("/login");
      router.refresh();
    }
  };

  if (!supabaseLoading && !isAuthenticated) {
    return null;
  }

  const navItems = [
    { href: "/dashboard", label: "Dashboard" },
    { href: "/orders", label: "Orders" },
    { href: "/strategies", label: "Strategies" },
    { href: "/settings", label: "Settings" },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-50">
      <nav className="bg-white/80 backdrop-blur-md border-b border-gray-200 shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center space-x-8">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">AT</span>
                </div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                  SRP Algo Trading
                </h1>
              </div>
              <div className="flex space-x-1">
                {navItems.map((item) => (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={cn(
                      "px-4 py-2 rounded-lg text-sm font-medium transition-all",
                      pathname === item.href
                        ? "bg-blue-100 text-blue-700 shadow-sm"
                        : "text-gray-600 hover:bg-gray-100"
                    )}
                  >
                    {item.label}
                  </Link>
                ))}
              </div>
            </div>
            <div className="flex items-center space-x-4">
              {supabaseUser && (
                <span className="text-sm text-gray-600">
                  {supabaseUser.user_metadata?.name || 
                   supabaseUser.user_metadata?.full_name || 
                   supabaseUser.email}
                </span>
              )}
              <Button variant="outline" onClick={handleLogout}>
                Logout
              </Button>
            </div>
          </div>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">{children}</main>
    </div>
  );
}


