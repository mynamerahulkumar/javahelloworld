"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import SupabaseLoginButton from "@/components/auth/supabase/LoginButton";
import Image from "next/image";
import { TrendingUp, Shield, Zap } from "lucide-react";
import { useUser } from "@/lib/auth/supabase/hooks";

interface Particle {
  left: string;
  top: string;
  delay: string;
  duration: string;
}

export default function LoginPage() {
  const router = useRouter();
  const { user, isLoading } = useUser();
  const [particles, setParticles] = useState<Particle[]>([]);

  // Redirect if already authenticated
  useEffect(() => {
    if (!isLoading && user) {
      router.push("/dashboard");
    }
  }, [user, isLoading, router]);

  // Generate particles only on client side to avoid hydration mismatch
  useEffect(() => {
    const generatedParticles: Particle[] = Array.from({ length: 6 }, () => ({
      left: `${Math.random() * 100}%`,
      top: `${Math.random() * 100}%`,
      delay: `${Math.random() * 3}s`,
      duration: `${3 + Math.random() * 2}s`,
    }));
    setParticles(generatedParticles);
  }, []);

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-white">Loading...</div>
      </div>
    );
  }

  // Don't render login page if user is already authenticated
  if (user) {
    return null;
  }

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
        {/* Dark overlay for better text readability */}
        <div className="absolute inset-0 bg-gradient-to-br from-slate-900/80 via-blue-900/70 to-indigo-900/80 backdrop-blur-sm" />
        {/* Animated gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-600/20 via-transparent to-indigo-600/20 animate-pulse" />
      </div>

      {/* Content */}
      <div className="relative z-10 w-full max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid lg:grid-cols-2 gap-8 items-center">
          {/* Left Side - Branding and Features */}
          <div className="hidden lg:block space-y-8 text-white">
            <div className="space-y-4 animate-fade-in">
              <div className="flex items-center gap-3">
                <div className="w-16 h-16 bg-gradient-to-br from-blue-500 via-indigo-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-2xl transform hover:scale-110 transition-transform duration-300">
                  <TrendingUp className="w-8 h-8 text-white" />
                </div>
                <div>
                  <h1 className="text-4xl font-bold bg-gradient-to-r from-white via-blue-100 to-indigo-100 bg-clip-text text-transparent">
                    SRP Algo Trading
                  </h1>
                  <p className="text-blue-200 text-sm font-medium">Professional Trading Platform</p>
                </div>
              </div>
              
              <div className="space-y-6 pt-8">
                <div className="flex items-start gap-4 group">
                  <div className="w-12 h-12 rounded-xl bg-blue-500/20 backdrop-blur-sm flex items-center justify-center group-hover:bg-blue-500/30 transition-colors">
                    <Zap className="w-6 h-6 text-blue-300" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold mb-1">Advanced Algorithms</h3>
                    <p className="text-blue-100/80 text-sm">Powerful trading strategies powered by cutting-edge algorithms</p>
                  </div>
                </div>
                
                <div className="flex items-start gap-4 group">
                  <div className="w-12 h-12 rounded-xl bg-indigo-500/20 backdrop-blur-sm flex items-center justify-center group-hover:bg-indigo-500/30 transition-colors">
                    <Shield className="w-6 h-6 text-indigo-300" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold mb-1">Secure & Reliable</h3>
                    <p className="text-blue-100/80 text-sm">Enterprise-grade security with real-time risk management</p>
                  </div>
                </div>
                
                <div className="flex items-start gap-4 group">
                  <div className="w-12 h-12 rounded-xl bg-purple-500/20 backdrop-blur-sm flex items-center justify-center group-hover:bg-purple-500/30 transition-colors">
                    <TrendingUp className="w-6 h-6 text-purple-300" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold mb-1">Real-Time Analytics</h3>
                    <p className="text-blue-100/80 text-sm">Monitor your positions and performance with live data</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Side - Login Card */}
          <div className="w-full flex justify-center lg:justify-end">
            <Card className="w-full max-w-md shadow-2xl border-0 bg-white/95 backdrop-blur-xl rounded-2xl overflow-hidden transform hover:scale-[1.02] transition-transform duration-300">
              {/* Card Header with Gradient */}
              <div className="bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 p-6">
                <CardHeader className="text-center pb-4 space-y-4">
                  <div className="flex justify-center">
                    <div className="w-20 h-20 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center shadow-xl border-2 border-white/30">
                      <TrendingUp className="w-10 h-10 text-white" />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <CardTitle className="text-3xl font-bold text-white">
                      Welcome Back
                    </CardTitle>
                    <CardDescription className="text-blue-100 text-base">
                      Sign in to your trading account
                    </CardDescription>
                  </div>
                </CardHeader>
              </div>

              <CardContent className="p-8">
                <div className="space-y-6">
                  <SupabaseLoginButton />
                  
                  <div className="pt-4 border-t border-gray-200">
                    <p className="text-xs text-center text-gray-500">
                      <Shield className="w-3 h-3 inline mr-1" />
                      Your credentials are securely managed by Supabase
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Mobile Branding */}
        <div className="lg:hidden text-center text-white mb-8 space-y-4">
          <div className="flex items-center justify-center gap-3">
            <div className="w-14 h-14 bg-gradient-to-br from-blue-500 via-indigo-500 to-purple-600 rounded-xl flex items-center justify-center shadow-xl">
              <TrendingUp className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold">SRP Algo Trading</h1>
              <p className="text-blue-200 text-sm">Professional Trading Platform</p>
            </div>
          </div>
        </div>
      </div>

      {/* Floating particles effect - client-side only */}
      {particles.length > 0 && (
        <div className="absolute inset-0 z-[5] pointer-events-none overflow-hidden">
          {particles.map((particle, i) => (
            <div
              key={i}
              className="absolute w-2 h-2 bg-blue-400/30 rounded-full animate-float"
              style={{
                left: particle.left,
                top: particle.top,
                animationDelay: particle.delay,
                animationDuration: particle.duration,
              }}
            />
          ))}
        </div>
      )}
    </div>
  );
}

