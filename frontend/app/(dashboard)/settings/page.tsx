"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useCredentialsStore } from "@/store/credentials";
import { useDeltaConnection } from "@/hooks/useDeltaConnection";
import { testConnection as testDeltaConnection } from "@/lib/api/delta-direct";
import { Eye, EyeOff, Save, Key, Lock, Trash2, CheckCircle2, XCircle, Loader2, TestTube } from "lucide-react";
import { toast } from "sonner";
import { useAuthStore } from "@/store/auth";

export default function SettingsPage() {
  const { setCredentials, getCredentials, clearCredentials, hasCredentials } = useCredentialsStore();
  const { connectionStatus, isConnected, isTesting, testConnection: testConnectionHook, lastConnectionTest } = useDeltaConnection();
  const { srpClientEmail } = useAuthStore();
  const [mounted, setMounted] = useState(false);
  const [showApiKey, setShowApiKey] = useState(false);
  const [showApiSecret, setShowApiSecret] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isTestingConnection, setIsTestingConnection] = useState(false);
  const [formData, setFormData] = useState({
    deltaApiKey: "",
    deltaApiSecret: "",
    deltaBaseUrl: "https://api.india.delta.exchange",
    srpClientEmail: "",
  });

  // Load credentials only after mount to prevent hydration errors
  useEffect(() => {
    setMounted(true);
    const existingCredentials = getCredentials();
    if (existingCredentials) {
      setFormData({
        deltaApiKey: existingCredentials.deltaApiKey || "",
        deltaApiSecret: existingCredentials.deltaApiSecret || "",
        deltaBaseUrl: existingCredentials.deltaBaseUrl || "https://api.india.delta.exchange",
        srpClientEmail: existingCredentials.srpClientEmail || srpClientEmail || "",
      });
    } else {
      // Pre-fill SRP client email from auth store if available
      setFormData((prev) => ({
        ...prev,
        srpClientEmail: srpClientEmail || "",
      }));
    }
  }, [getCredentials, srpClientEmail]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.deltaApiKey || !formData.deltaApiSecret) {
      toast.error("Please provide API Key and API Secret");
      return;
    }

    if (!formData.srpClientEmail) {
      toast.error("Please provide SRP Client Email");
      return;
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.srpClientEmail)) {
      toast.error("Please enter a valid email address");
      return;
    }

    setIsSaving(true);
    try {
      setCredentials({
        deltaApiKey: formData.deltaApiKey.trim(),
        deltaApiSecret: formData.deltaApiSecret.trim(),
        deltaBaseUrl: formData.deltaBaseUrl.trim() || "https://api.india.delta.exchange",
        srpClientEmail: formData.srpClientEmail.trim(),
      });
      toast.success("Delta API credentials saved successfully (client-side only)");
      // Test connection after saving
      setTimeout(() => {
        testConnectionHook();
      }, 500);
    } catch (error) {
      toast.error("Failed to save credentials");
    } finally {
      setIsSaving(false);
    }
  };

  const handleTestConnection = async () => {
    if (!formData.deltaApiKey || !formData.deltaApiSecret) {
      toast.error("Please provide API Key and API Secret before testing");
      return;
    }

    setIsTestingConnection(true);
    try {
      const result = await testDeltaConnection(
        formData.deltaApiKey,
        formData.deltaApiSecret,
        formData.deltaBaseUrl || "https://api.india.delta.exchange"
      );

      if (result.connected) {
        toast.success("Connection test successful! Credentials are valid.");
        // Update credentials store after successful test
        setCredentials({
          deltaApiKey: formData.deltaApiKey.trim(),
          deltaApiSecret: formData.deltaApiSecret.trim(),
          deltaBaseUrl: formData.deltaBaseUrl.trim() || "https://api.india.delta.exchange",
          srpClientEmail: formData.srpClientEmail.trim(),
        });
      } else {
        toast.error(result.error || "Connection test failed");
      }
    } catch (error: any) {
      toast.error(error.message || "Connection test failed");
    } finally {
      setIsTestingConnection(false);
    }
  };

  const handleClearCredentials = () => {
    if (window.confirm("Are you sure you want to delete your API credentials? This action cannot be undone.")) {
      clearCredentials();
      setFormData({
        deltaApiKey: "",
        deltaApiSecret: "",
        deltaBaseUrl: "https://api.india.delta.exchange",
        srpClientEmail: srpClientEmail || "",
      });
      toast.success("Credentials deleted successfully");
    }
  };

  const getConnectionStatusBadge = () => {
    if (isTesting || isTestingConnection) {
      return (
        <Badge variant="outline" className="bg-yellow-50 text-yellow-700 border-yellow-300">
          <Loader2 className="w-3 h-3 mr-1 animate-spin" />
          Testing...
        </Badge>
      );
    }
    if (isConnected) {
      return (
        <Badge variant="outline" className="bg-green-50 text-green-700 border-green-300">
          <CheckCircle2 className="w-3 h-3 mr-1" />
          Connected
        </Badge>
      );
    }
    return (
      <Badge variant="outline" className="bg-red-50 text-red-700 border-red-300">
        <XCircle className="w-3 h-3 mr-1" />
        Not Connected
      </Badge>
    );
  };

  if (!mounted) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-1">Settings</h1>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-1">Settings</h1>
        <p className="text-gray-600">
          Configure your Delta Exchange API credentials and connection settings
        </p>
      </div>

      <Card className="border-2 border-amber-200 bg-gradient-to-br from-amber-50 to-orange-50">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2 text-amber-900">
                <Key className="w-5 h-5" />
                Delta Exchange Configuration
              </CardTitle>
              <CardDescription className="text-amber-700">
                Configure your Delta Exchange API credentials. These are stored locally in your browser only and never sent to the server for storage.
              </CardDescription>
            </div>
            {mounted && hasCredentials() && getConnectionStatusBadge()}
          </div>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="srpClientEmail" className="text-sm font-semibold">
                SRP Client Email *
              </Label>
              <Input
                id="srpClientEmail"
                type="email"
                value={formData.srpClientEmail}
                onChange={(e) => setFormData({ ...formData, srpClientEmail: e.target.value })}
                placeholder="your.email@example.com"
                required
                disabled={isSaving}
                className="h-11"
              />
              <p className="text-xs text-gray-500">
                Your email must be registered in the SRP algo trade API whitelist
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="deltaApiKey" className="text-sm font-semibold">
                Delta API Key *
              </Label>
              <div className="relative">
                <Input
                  id="deltaApiKey"
                  type={showApiKey ? "text" : "password"}
                  value={formData.deltaApiKey}
                  onChange={(e) => setFormData({ ...formData, deltaApiKey: e.target.value })}
                  placeholder="Enter your Delta Exchange API Key"
                  className="pr-10 h-11"
                  required
                  disabled={isSaving}
                />
                <button
                  type="button"
                  onClick={() => setShowApiKey(!showApiKey)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                >
                  {showApiKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="deltaApiSecret" className="text-sm font-semibold">
                Delta API Secret *
              </Label>
              <div className="relative">
                <Input
                  id="deltaApiSecret"
                  type={showApiSecret ? "text" : "password"}
                  value={formData.deltaApiSecret}
                  onChange={(e) => setFormData({ ...formData, deltaApiSecret: e.target.value })}
                  placeholder="Enter your Delta Exchange API Secret"
                  className="pr-10 h-11"
                  required
                  disabled={isSaving}
                />
                <button
                  type="button"
                  onClick={() => setShowApiSecret(!showApiSecret)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                >
                  {showApiSecret ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="deltaBaseUrl" className="text-sm font-semibold">
                Base URL (Optional)
              </Label>
              <Input
                id="deltaBaseUrl"
                type="text"
                value={formData.deltaBaseUrl}
                onChange={(e) => setFormData({ ...formData, deltaBaseUrl: e.target.value })}
                placeholder="https://api.india.delta.exchange"
                disabled={isSaving}
                className="h-11"
              />
            </div>

            <div className="flex flex-col sm:flex-row gap-2">
              <Button
                type="submit"
                className="flex-1 bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-700 hover:to-orange-700"
                disabled={isSaving || isTestingConnection}
              >
                <Save className="w-4 h-4 mr-2" />
                {isSaving ? "Saving..." : "Save Credentials"}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={handleTestConnection}
                disabled={isSaving || isTestingConnection || !formData.deltaApiKey || !formData.deltaApiSecret}
                className="flex-1 sm:flex-shrink-0"
              >
                {isTestingConnection ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Testing...
                  </>
                ) : (
                  <>
                    <TestTube className="w-4 h-4 mr-2" />
                    Test Connection
                  </>
                )}
              </Button>
              {mounted && hasCredentials() && (
                <Button
                  type="button"
                  variant="destructive"
                  onClick={handleClearCredentials}
                  disabled={isSaving || isTestingConnection}
                  className="flex-1 sm:flex-shrink-0"
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Delete
                </Button>
              )}
            </div>

            {lastConnectionTest && (
              <p className="text-xs text-center text-gray-500">
                Last connection test: {lastConnectionTest.toLocaleString()}
              </p>
            )}

            <p className="text-xs text-center text-amber-600 pt-2">
              <Lock className="w-3 h-3 inline mr-1" />
              Credentials are stored locally in your browser only. They are never saved on the server.
            </p>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}


