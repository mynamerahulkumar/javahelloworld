"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useUser, useAuth } from "@/lib/auth/supabase/hooks";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { cn } from "@/lib/utils";
import { Menu, LogOut, LayoutDashboard, ShoppingCart, Target, Settings as SettingsIcon, Flame } from "lucide-react";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/orders", label: "Orders", icon: ShoppingCart },
  { href: "/strategies", label: "Strategies", icon: Target },
  { href: "/settings", label: "Settings", icon: SettingsIcon },
  { href: "/heatmap", label: "Heat Map", icon: Flame },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const { user: supabaseUser, isLoading: supabaseLoading } = useUser();
  const { logout } = useAuth();

  const isAuthenticated = !!supabaseUser;
  const [isMobileOpen, setIsMobileOpen] = useState(false);

  useEffect(() => {
    if (!supabaseLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [isAuthenticated, supabaseLoading, router]);

  const handleLogout = async () => {
    try {
      const result = await logout();
      if (result?.error) {
        router.push("/login");
        router.refresh();
      }
    } catch {
      router.push("/login");
      router.refresh();
    }
  };

  if (!supabaseLoading && !isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-50">
      <nav className="bg-white/80 backdrop-blur-md border-b border-gray-200 shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center space-x-4 lg:space-x-8">
              <button
                onClick={() => setIsMobileOpen(true)}
                className="inline-flex h-10 w-10 items-center justify-center rounded-lg border border-gray-200 bg-white text-gray-600 shadow-sm transition hover:bg-gray-100 lg:hidden"
                aria-label="Open navigation"
              >
                <Menu className="h-5 w-5" />
              </button>
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">AT</span>
                </div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                  SRP Algo Trading
                </h1>
              </div>
              <div className="hidden space-x-1 lg:flex">
                {NAV_ITEMS.map((item) => {
                  const isActive = pathname === item.href;
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      className={cn(
                        "px-4 py-2 rounded-lg text-sm font-medium transition",
                        isActive ? "bg-blue-100 text-blue-700 shadow-sm" : "text-gray-600 hover:bg-gray-100"
                      )}
                    >
                      {item.label}
                    </Link>
                  );
                })}
              </div>
            </div>
            <div className="flex items-center space-x-4">
              {supabaseUser && (
                <span className="hidden text-sm text-gray-600 sm:inline">
                  {supabaseUser.user_metadata?.name || supabaseUser.user_metadata?.full_name || supabaseUser.email}
                </span>
              )}
              <Button variant="outline" onClick={handleLogout} className="hidden sm:inline-flex">
                Logout
              </Button>
              <Button
                variant="outline"
                onClick={handleLogout}
                className="sm:hidden inline-flex items-center justify-center"
                aria-label="Logout"
              >
                <LogOut className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </nav>
      {isMobileOpen && (
        <div className="lg:hidden">
          <div
            className="fixed inset-0 z-40 bg-slate-900/50 backdrop-blur-sm"
            onClick={() => setIsMobileOpen(false)}
          />
          <div className="fixed inset-y-0 left-0 z-50 flex h-full w-72 flex-col border-r border-slate-200 bg-white shadow-xl">
            <div className="flex items-center justify-between px-5 py-4 border-b border-slate-200">
              <div>
                <p className="text-lg font-semibold text-slate-800">SRP Algo Trading</p>
                <p className="text-xs text-slate-500">Navigation</p>
              </div>
              <button
                onClick={() => setIsMobileOpen(false)}
                className="rounded-lg border border-slate-200 bg-white px-2 py-1 text-sm text-slate-600 shadow-sm hover:bg-slate-100"
                aria-label="Close navigation"
              >
                Close
              </button>
            </div>
            <nav className="flex-1 space-y-1 px-4 py-4 overflow-y-auto">
              {NAV_ITEMS.map((item) => {
                const Icon = item.icon;
                const isActive = pathname === item.href;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={() => setIsMobileOpen(false)}
                    className={cn(
                      "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition",
                      isActive ? "bg-blue-600 text-white" : "text-slate-600 hover:bg-slate-100"
                    )}
                  >
                    <Icon className="h-4 w-4" />
                    <span>{item.label}</span>
                  </Link>
                );
              })}
            </nav>
            <div className="border-t border-slate-200 px-5 py-4 space-y-3">
              {supabaseUser && (
                <p className="text-xs text-slate-500">
                  Signed in as{" "}
                  <span className="font-semibold text-slate-700">
                    {supabaseUser.user_metadata?.name ||
                      supabaseUser.user_metadata?.full_name ||
                      supabaseUser.email}
                  </span>
                </p>
              )}
              <Button onClick={handleLogout} className="w-full justify-center">
                <LogOut className="mr-2 h-4 w-4" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      )}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">{children}</main>
    </div>
  );
}


