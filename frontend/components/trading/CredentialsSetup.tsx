"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { useCredentialsStore } from "@/store/credentials";
import { Eye, EyeOff, Save, Key, Lock, Trash2 } from "lucide-react";
import { toast } from "sonner";

export default function CredentialsSetup() {
  const { setCredentials, getCredentials, clearCredentials, hasCredentials } = useCredentialsStore();
  const [mounted, setMounted] = useState(false);
  const [showApiKey, setShowApiKey] = useState(false);
  const [showApiSecret, setShowApiSecret] = useState(false);
  const [formData, setFormData] = useState({
    deltaApiKey: "",
    deltaApiSecret: "",
    deltaBaseUrl: "https://api.india.delta.exchange",
  });
  const [isSaving, setIsSaving] = useState(false);

  // Load credentials only after mount to prevent hydration errors
  useEffect(() => {
    setMounted(true);
    const existingCredentials = getCredentials();
    if (existingCredentials) {
      setFormData({
        deltaApiKey: existingCredentials.deltaApiKey || "",
        deltaApiSecret: existingCredentials.deltaApiSecret || "",
        deltaBaseUrl: existingCredentials.deltaBaseUrl || "https://api.india.delta.exchange",
      });
    }
  }, [getCredentials]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.deltaApiKey || !formData.deltaApiSecret) {
      toast.error("Please provide API Key and API Secret");
      return;
    }

    setIsSaving(true);
    try {
      setCredentials({
        deltaApiKey: formData.deltaApiKey.trim(),
        deltaApiSecret: formData.deltaApiSecret.trim(),
        deltaBaseUrl: formData.deltaBaseUrl.trim() || "https://api.india.delta.exchange",
      });
      toast.success("Delta API credentials saved successfully (client-side only)");
    } catch (error) {
      toast.error("Failed to save credentials");
    } finally {
      setIsSaving(false);
    }
  };

  const handleClearCredentials = () => {
    if (window.confirm("Are you sure you want to delete your API credentials? This action cannot be undone.")) {
      clearCredentials();
      setFormData({
        deltaApiKey: "",
        deltaApiSecret: "",
        deltaBaseUrl: "https://api.india.delta.exchange",
      });
      toast.success("Credentials deleted successfully");
    }
  };

  return (
    <Card className="border-2 border-amber-200 bg-gradient-to-br from-amber-50 to-orange-50">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-amber-900">
          <Key className="w-5 h-5" />
          Delta Exchange API Credentials
        </CardTitle>
        <CardDescription className="text-amber-700">
          Configure your Delta Exchange API credentials. These are stored locally in your browser only and never sent to the server for storage.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="deltaApiKey" className="text-sm font-semibold">
              API Key *
            </Label>
            <div className="relative">
              <Input
                id="deltaApiKey"
                type={showApiKey ? "text" : "password"}
                value={formData.deltaApiKey}
                onChange={(e) => setFormData({ ...formData, deltaApiKey: e.target.value })}
                placeholder="Enter your Delta Exchange API Key"
                className="pr-10"
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
              API Secret *
            </Label>
            <div className="relative">
              <Input
                id="deltaApiSecret"
                type={showApiSecret ? "text" : "password"}
                value={formData.deltaApiSecret}
                onChange={(e) => setFormData({ ...formData, deltaApiSecret: e.target.value })}
                placeholder="Enter your Delta Exchange API Secret"
                className="pr-10"
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
            />
          </div>

          <div className="flex gap-2">
            <Button
              type="submit"
              className="flex-1 bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-700 hover:to-orange-700"
              disabled={isSaving}
            >
              <Save className="w-4 h-4 mr-2" />
              {isSaving ? "Saving..." : "Save Credentials"}
            </Button>
            {mounted && hasCredentials() && (
              <Button
                type="button"
                variant="destructive"
                onClick={handleClearCredentials}
                disabled={isSaving}
                className="flex-shrink-0"
              >
                <Trash2 className="w-4 h-4 mr-2" />
                Delete
              </Button>
            )}
          </div>

          <p className="text-xs text-center text-amber-600 pt-2">
            <Lock className="w-3 h-3 inline mr-1" />
            Credentials are stored locally in your browser only. They are never saved on the server.
          </p>
        </form>
      </CardContent>
    </Card>
  );
}

