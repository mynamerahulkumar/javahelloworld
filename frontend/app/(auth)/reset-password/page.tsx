"use client";

import { Suspense, useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Lock, Loader2, KeyRound, CheckCircle2 } from "lucide-react";
import { toast } from "sonner";
import { useAuth, useUser } from "@/lib/auth/supabase/hooks";
import Image from "next/image";

function ResetPasswordContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { changePassword, isLoading } = useAuth();
  const { user, isLoading: userLoading } = useUser();
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isSuccess, setIsSuccess] = useState(false);

  useEffect(() => {
    // Check if we have a valid recovery session
    // Supabase automatically creates a session when user clicks the reset link
    if (!userLoading) {
      const accessToken = searchParams.get("access_token");
      const type = searchParams.get("type");
      
      // If no valid token or session, redirect to login
      if (!accessToken || type !== "recovery") {
        if (!user) {
          toast.error("Invalid or expired reset link. Please request a new one.");
          router.push("/login");
        }
      }
    }
  }, [searchParams, router, user, userLoading]);

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!newPassword || !confirmPassword) {
      toast.error("Please enter both password fields");
      return;
    }

    if (newPassword !== confirmPassword) {
      toast.error("Passwords do not match");
      return;
    }

    if (newPassword.length < 6) {
      toast.error("Password must be at least 6 characters");
      return;
    }

    const { error } = await changePassword(newPassword);

    if (error) {
      toast.error(error.message || "Failed to reset password");
    } else {
      toast.success("Password reset successfully! Redirecting to login...");
      setIsSuccess(true);
      setTimeout(() => {
        router.push("/login");
      }, 2000);
    }
  };

  return (
    <div className="min-h-screen relative flex items-center justify-center overflow-hidden">
      {/* Background Image with Overlay */}
      <div className="absolute inset-0 z-0">
        <Image
          src="/images/main_logo.png"
          alt="SRP Algo Trading Background"
          fill
          className="object-cover"
          priority
          quality={90}
        />
        <div className="absolute inset-0 bg-gradient-to-br from-slate-900/80 via-blue-900/70 to-indigo-900/80 backdrop-blur-sm" />
        <div className="absolute inset-0 bg-gradient-to-br from-blue-600/20 via-transparent to-indigo-600/20 animate-pulse" />
      </div>

      {/* Content */}
      <div className="relative z-10 w-full max-w-md mx-auto px-4 sm:px-6 lg:px-8">
        <Card className="shadow-2xl border-0 bg-white/95 backdrop-blur-xl rounded-2xl overflow-hidden">
          {/* Card Header with Gradient */}
          <div className="bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 p-6">
            <CardHeader className="text-center pb-4 space-y-4">
              <div className="flex justify-center">
                <div className="w-20 h-20 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center shadow-xl border-2 border-white/30">
                  <KeyRound className="w-10 h-10 text-white" />
                </div>
              </div>
              <div className="space-y-2">
                <CardTitle className="text-3xl font-bold text-white">
                  Reset Password
                </CardTitle>
                <CardDescription className="text-blue-100 text-base">
                  Enter your new password
                </CardDescription>
              </div>
            </CardHeader>
          </div>

          <CardContent className="p-8">
            {userLoading ? (
              <div className="text-center py-8">
                <Loader2 className="w-8 h-8 animate-spin mx-auto text-blue-600 mb-4" />
                <p className="text-gray-600">Verifying reset link...</p>
              </div>
            ) : isSuccess ? (
              <div className="text-center space-y-4 py-8">
                <div className="flex justify-center">
                  <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
                    <CheckCircle2 className="w-10 h-10 text-green-600" />
                  </div>
                </div>
                <h3 className="text-xl font-semibold text-gray-800">
                  Password Reset Successful!
                </h3>
                <p className="text-gray-600">
                  Your password has been reset. Redirecting to login...
                </p>
              </div>
            ) : (
              <form onSubmit={handleResetPassword} className="space-y-5">
                <div className="space-y-2">
                  <Label htmlFor="new-password" className="text-sm font-semibold text-gray-700 flex items-center gap-2">
                    <Lock className="w-4 h-4 text-gray-500" />
                    New Password
                  </Label>
                  <Input
                    id="new-password"
                    type="password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    required
                    placeholder="Enter new password"
                    className="h-12 text-base border-gray-300 focus:border-blue-500 focus:ring-blue-500 transition-colors"
                    disabled={isLoading}
                    minLength={6}
                  />
                  <p className="text-xs text-gray-500">Password must be at least 6 characters</p>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="confirm-new-password" className="text-sm font-semibold text-gray-700 flex items-center gap-2">
                    <Lock className="w-4 h-4 text-gray-500" />
                    Confirm New Password
                  </Label>
                  <Input
                    id="confirm-new-password"
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                    placeholder="Confirm new password"
                    className="h-12 text-base border-gray-300 focus:border-blue-500 focus:ring-blue-500 transition-colors"
                    disabled={isLoading}
                    minLength={6}
                  />
                </div>
                <Button
                  type="submit"
                  disabled={isLoading}
                  className="w-full h-12 text-base font-semibold bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 hover:from-blue-700 hover:via-indigo-700 hover:to-purple-700 text-white shadow-lg hover:shadow-xl transform hover:scale-[1.02] transition-all duration-200 disabled:opacity-70 disabled:cursor-not-allowed disabled:transform-none"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                      Resetting Password...
                    </>
                  ) : (
                    <>
                      <KeyRound className="w-5 h-5 mr-2" />
                      Reset Password
                    </>
                  )}
                </Button>
              </form>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        </div>
      }
    >
      <ResetPasswordContent />
    </Suspense>
  );
}
