"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth/supabase/hooks";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { LogIn, Loader2, Mail, Lock, UserPlus, User, KeyRound } from "lucide-react";
import { toast } from "sonner";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";

export default function SupabaseLoginButton() {
  const router = useRouter();
  const { signIn, signUp, resendConfirmation, forgotPassword, isLoading } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [name, setName] = useState("");
  const [isSignUp, setIsSignUp] = useState(false);
  const [showResendConfirmation, setShowResendConfirmation] = useState(false);
  const [resendSuccess, setResendSuccess] = useState(false);
  const [forgotPasswordEmail, setForgotPasswordEmail] = useState("");
  const [isForgotPasswordOpen, setIsForgotPasswordOpen] = useState(false);
  const [forgotPasswordSuccess, setForgotPasswordSuccess] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email || !password) {
      toast.error("Please enter both email and password");
      return;
    }

    const { user, error } = await signIn(email, password);
    
    if (error) {
      if (error.message === "EMAIL_NOT_CONFIRMED") {
        toast.error("Please confirm your email before signing in. Check your inbox for the confirmation link.");
        setShowResendConfirmation(true);
      } else {
        toast.error(error.message || "Login failed");
      }
    } else if (user) {
      toast.success("Login successful");
      setShowResendConfirmation(false);
      // Redirect to dashboard after successful login
      router.push("/dashboard");
      router.refresh();
    }
  };

  const handleResendConfirmation = async () => {
    if (!email) {
      toast.error("Please enter your email address");
      return;
    }

    const { error } = await resendConfirmation(email);
    
    if (error) {
      toast.error(error.message || "Failed to resend confirmation email");
    } else {
      toast.success("Confirmation email sent! Please check your inbox.");
      setResendSuccess(true);
      setTimeout(() => {
        setResendSuccess(false);
      }, 5000);
    }
  };

  const handleForgotPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!forgotPasswordEmail) {
      toast.error("Please enter your email address");
      return;
    }

    const { error } = await forgotPassword(forgotPasswordEmail);
    
    if (error) {
      toast.error(error.message || "Failed to send password reset email");
    } else {
      toast.success("Password reset email sent! Please check your inbox.");
      setForgotPasswordSuccess(true);
      setTimeout(() => {
        setForgotPasswordSuccess(false);
        setIsForgotPasswordOpen(false);
        setForgotPasswordEmail("");
      }, 3000);
    }
  };

  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email || !password) {
      toast.error("Please enter both email and password");
      return;
    }

    if (!name || name.trim().length === 0) {
      toast.error("Please enter your name");
      return;
    }

    if (password !== confirmPassword) {
      toast.error("Passwords do not match");
      return;
    }

    if (password.length < 6) {
      toast.error("Password must be at least 6 characters");
      return;
    }

    const { user, session, error } = await signUp(email, password, {
      name: name.trim(),
      full_name: name.trim(),
    });
    
    if (error) {
      toast.error(error.message || "Sign up failed");
    } else if (user) {
      // If there's no session, email confirmation is required
      if (!session) {
        toast.success("Account created! Please check your email to confirm your account before signing in.", {
          duration: 6000,
        });
        // Reset form
        setEmail("");
        setPassword("");
        setConfirmPassword("");
        setName("");
        setIsSignUp(false);
        // Show resend confirmation option
        setShowResendConfirmation(true);
      } else {
        // Session exists, user is already confirmed
        toast.success("Account created successfully!");
        // Reset form
        setEmail("");
        setPassword("");
        setConfirmPassword("");
        setName("");
        setIsSignUp(false);
      }
    }
  };

  return (
    <Tabs value={isSignUp ? "signup" : "login"} onValueChange={(v) => setIsSignUp(v === "signup")} className="w-full">
      <TabsList className="grid w-full grid-cols-2 mb-6">
        <TabsTrigger value="login" className="flex items-center gap-2">
          <LogIn className="w-4 h-4" />
          Sign In
        </TabsTrigger>
        <TabsTrigger value="signup" className="flex items-center gap-2">
          <UserPlus className="w-4 h-4" />
          Sign Up
        </TabsTrigger>
      </TabsList>

      <TabsContent value="login" className="space-y-5 mt-0">
        <form onSubmit={handleLogin} className="space-y-5">
          <div className="space-y-2">
            <Label htmlFor="login-email" className="text-sm font-semibold text-gray-700 flex items-center gap-2">
              <Mail className="w-4 h-4 text-gray-500" />
              Email Address
            </Label>
            <Input
              id="login-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="you@example.com"
              className="h-12 text-base border-gray-300 focus:border-blue-500 focus:ring-blue-500 transition-colors"
              disabled={isLoading}
            />
          </div>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="login-password" className="text-sm font-semibold text-gray-700 flex items-center gap-2">
                <Lock className="w-4 h-4 text-gray-500" />
                Password
              </Label>
              <Dialog open={isForgotPasswordOpen} onOpenChange={setIsForgotPasswordOpen}>
                <DialogTrigger asChild>
                  <button
                    type="button"
                    className="text-xs text-blue-600 hover:text-blue-700 hover:underline font-medium"
                  >
                    Forgot Password?
                  </button>
                </DialogTrigger>
                <DialogContent className="sm:max-w-md">
                  <DialogHeader>
                    <DialogTitle className="flex items-center gap-2">
                      <KeyRound className="w-5 h-5 text-blue-600" />
                      Reset Password
                    </DialogTitle>
                    <DialogDescription>
                      Enter your email address and we'll send you a link to reset your password.
                    </DialogDescription>
                  </DialogHeader>
                  <form onSubmit={handleForgotPassword} className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="forgot-password-email" className="text-sm font-semibold text-gray-700">
                        Email Address
                      </Label>
                      <Input
                        id="forgot-password-email"
                        type="email"
                        value={forgotPasswordEmail}
                        onChange={(e) => setForgotPasswordEmail(e.target.value)}
                        required
                        placeholder="you@example.com"
                        className="h-11"
                        disabled={isLoading || forgotPasswordSuccess}
                      />
                    </div>
                    {forgotPasswordSuccess ? (
                      <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                        <p className="text-sm text-green-800">
                          Password reset email sent! Please check your inbox and follow the instructions.
                        </p>
                      </div>
                    ) : (
                      <Button
                        type="submit"
                        disabled={isLoading}
                        className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
                      >
                        {isLoading ? (
                          <>
                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                            Sending...
                          </>
                        ) : (
                          <>
                            <Mail className="w-4 h-4 mr-2" />
                            Send Reset Link
                          </>
                        )}
                      </Button>
                    )}
                  </form>
                </DialogContent>
              </Dialog>
            </div>
            <Input
              id="login-password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="Enter your password"
              className="h-12 text-base border-gray-300 focus:border-blue-500 focus:ring-blue-500 transition-colors"
              disabled={isLoading}
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
                Signing in...
              </>
            ) : (
              <>
                <LogIn className="w-5 h-5 mr-2" />
                Sign In to Dashboard
              </>
            )}
          </Button>
          
          {showResendConfirmation && (
            <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <p className="text-sm text-yellow-800 mb-3">
                Your email address hasn't been confirmed yet. Please check your inbox for the confirmation link.
              </p>
              <Button
                type="button"
                onClick={handleResendConfirmation}
                disabled={isLoading || resendSuccess}
                variant="outline"
                className="w-full text-sm bg-white hover:bg-yellow-50 border-yellow-300 text-yellow-800"
              >
                {resendSuccess ? (
                  <>
                    <Mail className="w-4 h-4 mr-2" />
                    Email Sent!
                  </>
                ) : (
                  <>
                    <Mail className="w-4 h-4 mr-2" />
                    Resend Confirmation Email
                  </>
                )}
              </Button>
            </div>
          )}
        </form>
      </TabsContent>

      <TabsContent value="signup" className="space-y-5 mt-0">
        <form onSubmit={handleSignUp} className="space-y-5">
          <div className="space-y-2">
            <Label htmlFor="signup-name" className="text-sm font-semibold text-gray-700 flex items-center gap-2">
              <User className="w-4 h-4 text-gray-500" />
              Full Name
            </Label>
            <Input
              id="signup-name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              placeholder="John Doe"
              className="h-12 text-base border-gray-300 focus:border-blue-500 focus:ring-blue-500 transition-colors"
              disabled={isLoading}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="signup-email" className="text-sm font-semibold text-gray-700 flex items-center gap-2">
              <Mail className="w-4 h-4 text-gray-500" />
              Email Address
            </Label>
            <Input
              id="signup-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="you@example.com"
              className="h-12 text-base border-gray-300 focus:border-blue-500 focus:ring-blue-500 transition-colors"
              disabled={isLoading}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="signup-password" className="text-sm font-semibold text-gray-700 flex items-center gap-2">
              <Lock className="w-4 h-4 text-gray-500" />
              Password
            </Label>
            <Input
              id="signup-password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="At least 6 characters"
              className="h-12 text-base border-gray-300 focus:border-blue-500 focus:ring-blue-500 transition-colors"
              disabled={isLoading}
              minLength={6}
            />
            <p className="text-xs text-gray-500">Password must be at least 6 characters</p>
          </div>
          <div className="space-y-2">
            <Label htmlFor="signup-confirm-password" className="text-sm font-semibold text-gray-700 flex items-center gap-2">
              <Lock className="w-4 h-4 text-gray-500" />
              Confirm Password
            </Label>
            <Input
              id="signup-confirm-password"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              placeholder="Confirm your password"
              className="h-12 text-base border-gray-300 focus:border-blue-500 focus:ring-blue-500 transition-colors"
              disabled={isLoading}
            />
          </div>
          <Button
            type="submit"
            disabled={isLoading}
            className="w-full h-12 text-base font-semibold bg-gradient-to-r from-green-600 via-emerald-600 to-teal-600 hover:from-green-700 hover:via-emerald-700 hover:to-teal-700 text-white shadow-lg hover:shadow-xl transform hover:scale-[1.02] transition-all duration-200 disabled:opacity-70 disabled:cursor-not-allowed disabled:transform-none"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                Creating account...
              </>
            ) : (
              <>
                <UserPlus className="w-5 h-5 mr-2" />
                Create Account
              </>
            )}
          </Button>
          
          {showResendConfirmation && (
            <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <p className="text-sm text-yellow-800 mb-3">
                Please check your inbox for the confirmation email. If you didn't receive it, you can resend it.
              </p>
              <Button
                type="button"
                onClick={handleResendConfirmation}
                disabled={isLoading || resendSuccess}
                variant="outline"
                className="w-full text-sm bg-white hover:bg-yellow-50 border-yellow-300 text-yellow-800"
              >
                {resendSuccess ? (
                  <>
                    <Mail className="w-4 h-4 mr-2" />
                    Email Sent!
                  </>
                ) : (
                  <>
                    <Mail className="w-4 h-4 mr-2" />
                    Resend Confirmation Email
                  </>
                )}
              </Button>
            </div>
          )}
        </form>
      </TabsContent>
    </Tabs>
  );
}

