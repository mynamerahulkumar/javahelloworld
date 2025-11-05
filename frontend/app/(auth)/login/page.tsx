"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/auth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "sonner";
import { login } from "@/lib/api/trading";
import { Lock, Mail, User, Loader2 } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const setAuthenticated = useAuthStore((state) => state.setAuthenticated);
  const [formData, setFormData] = useState({
    srpClientId: "",
    srpClientEmail: "",
    srpPassword: "",
  });
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.srpClientId || !formData.srpClientEmail || !formData.srpPassword) {
      toast.error("Please provide all required credentials");
      return;
    }

    setIsLoading(true);
    try {
      const response = await login({
        srp_client_id: formData.srpClientId,
        srp_client_email: formData.srpClientEmail,
        srp_password: formData.srpPassword,
      });

      if (response.success) {
        setAuthenticated(true);
        toast.success("Login successful");
        // Clear form data immediately after successful login for privacy
        setFormData({ srpClientId: "", srpClientEmail: "", srpPassword: "" });
        router.push("/dashboard");
      } else {
        toast.error(response.error || "Login failed");
      }
    } catch (error: any) {
      toast.error(error.detail || "Login failed. Please check your credentials.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 p-4">
      <Card className="w-full max-w-md shadow-2xl border-2 border-slate-200 bg-white">
        <CardHeader className="text-center pb-6 space-y-4">
          <div className="flex justify-center">
            <div className="w-20 h-20 bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg">
              <span className="text-white font-bold text-2xl">AT</span>
            </div>
          </div>
          <div className="space-y-2">
            <CardTitle className="text-3xl font-bold bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 bg-clip-text text-transparent">
              Algo Trading Platform
            </CardTitle>
            <CardDescription className="text-base">
              Secure login to access your trading dashboard
            </CardDescription>
          </div>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-2">
              <Label htmlFor="srpClientId" className="text-sm font-semibold flex items-center gap-2">
                <User className="w-4 h-4" />
                SRP Client ID *
              </Label>
              <Input
                id="srpClientId"
                type="password"
                value={formData.srpClientId}
                onChange={(e) => setFormData({ ...formData, srpClientId: e.target.value })}
                required
                placeholder="Enter your SRP Client ID"
                className="h-12 text-base"
                disabled={isLoading}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="srpClientEmail" className="text-sm font-semibold flex items-center gap-2">
                <Mail className="w-4 h-4" />
                SRP Client Email *
              </Label>
              <Input
                id="srpClientEmail"
                type="password"
                value={formData.srpClientEmail}
                onChange={(e) => setFormData({ ...formData, srpClientEmail: e.target.value })}
                required
                placeholder="Enter your SRP Client Email"
                className="h-12 text-base"
                disabled={isLoading}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="srpPassword" className="text-sm font-semibold flex items-center gap-2">
                <Lock className="w-4 h-4" />
                SRP Password *
              </Label>
              <Input
                id="srpPassword"
                type="password"
                value={formData.srpPassword}
                onChange={(e) => setFormData({ ...formData, srpPassword: e.target.value })}
                required
                placeholder="Enter your SRP Password"
                className="h-12 text-base"
                disabled={isLoading}
              />
            </div>
            <Button 
              type="submit" 
              className="w-full h-12 text-base font-semibold bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 shadow-lg" 
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Logging in...
                </>
              ) : (
                <>
                  <Lock className="w-4 h-4 mr-2" />
                  Login
                </>
              )}
            </Button>
            <p className="text-xs text-center text-slate-500 pt-2">
              Your credentials are never stored for privacy protection
            </p>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}

