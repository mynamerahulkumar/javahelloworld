"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { PlaceLimitOrderWaitRequest } from "@/lib/types";
import { placeLimitOrderWait } from "@/lib/api/trading";
import { toast } from "sonner";
import { useAuthStore } from "@/store/auth";
import { useDeltaConnection } from "@/hooks/useDeltaConnection";
import { TrendingUp, TrendingDown, DollarSign, Target, Shield, Clock, Lock, Mail, User, Key, Loader2, AlertCircle } from "lucide-react";

interface OrderFormProps {
  orderType: "limit-wait" | "market" | "limit";
}

export function OrderForm({ orderType }: OrderFormProps) {
  const [isLoading, setIsLoading] = useState(false);
  const { srpClientId, srpClientEmail } = useAuthStore();
  const { isConnected, connectionStatus } = useDeltaConnection();
  const [formData, setFormData] = useState<PlaceLimitOrderWaitRequest>({
    symbol: "BTC",
    entry_price: 0,
    size: 1,
    side: "buy",
    stop_loss_price: undefined,
    take_profit_price: undefined,
    client_order_id: undefined,
    wait_time_seconds: 60,
  });
  
  // Delta API credentials state - never persisted (client-side only)
  const [credentials, setCredentials] = useState({
    apiKey: "",
    apiSecret: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Check connection status first
    if (!isConnected) {
      toast.error("Delta Exchange connection is not established. Please configure your API credentials in Settings and test the connection.");
      return;
    }

    if (formData.entry_price <= 0 || formData.size <= 0) {
      toast.error("Please enter valid entry price and size");
      return;
    }

    // Validate that we have client info from Supabase user
    if (!srpClientId || !srpClientEmail) {
      toast.error("User information not available. Please log in again.");
      return;
    }

    if (!credentials.apiKey || !credentials.apiSecret) {
      toast.error("Please provide Delta API credentials");
      return;
    }

    setIsLoading(true);
    try {
      console.log("Placing order with data:", { ...formData, credentials: { ...credentials, apiKey: "***", apiSecret: "***" } });
      
      const result = await placeLimitOrderWait(formData, {
        srpClientId: srpClientId,
        srpClientEmail: srpClientEmail,
        deltaApiKey: credentials.apiKey,
        deltaApiSecret: credentials.apiSecret,
      });
      
      console.log("Order placed successfully:", result);
      toast.success(result.message || "Order placed successfully");
      
      // Reset form data
      setFormData({
        symbol: "BTC",
        entry_price: 0,
        size: 1,
        side: "buy",
        stop_loss_price: undefined,
        take_profit_price: undefined,
        client_order_id: undefined,
        wait_time_seconds: 60,
      });
      
      // Clear Delta API credentials immediately after use for privacy
      // Note: srpClientId and srpClientEmail are kept in store (from Supabase user metadata)
      setCredentials({
        apiKey: "",
        apiSecret: "",
      });
    } catch (error: any) {
      console.error("Order placement error:", error);
      const errorMessage = error.detail || error.message || "Failed to place order. Please check your credentials and try again.";
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const sideColor = formData.side === "buy" ? "text-green-500" : "text-red-500";
  const sideBgColor = formData.side === "buy" ? "bg-green-500/10 border-green-500/20" : "bg-red-500/10 border-red-500/20";

  return (
    <Card className="border-2">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-2xl font-bold">Place Order</CardTitle>
            <CardDescription>Execute trading orders with stop loss and take profit</CardDescription>
          </div>
          <Badge variant="outline" className={`text-lg px-4 py-2 ${sideColor} ${sideBgColor}`}>
            {formData.side === "buy" ? (
              <><TrendingUp className="w-4 h-4 mr-2" /> BUY</>
            ) : (
              <><TrendingDown className="w-4 h-4 mr-2" /> SELL</>
            )}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Connection Status Warning */}
          {!isConnected && (
            <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm font-semibold text-yellow-800">
                  Delta Exchange connection required
                </p>
                <p className="text-xs text-yellow-700 mt-1">
                  Please configure your Delta API credentials in Settings and test the connection before placing orders.
                </p>
              </div>
            </div>
          )}

          {/* Delta API Credentials Section */}
          <div className="space-y-4 p-4 bg-slate-50 rounded-lg border border-slate-200">
            <div className="flex items-center gap-2 mb-2">
              <Lock className="w-4 h-4 text-slate-600" />
              <Label className="text-sm font-semibold text-slate-700">
                Delta Exchange API Credentials (Required)
              </Label>
            </div>
            <p className="text-xs text-slate-500 mb-4">
              Your user information is automatically used for order validation. 
              API credentials are never stored and cleared after order placement for privacy.
            </p>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="apiKey" className="text-sm font-semibold flex items-center gap-2">
                  <Key className="w-4 h-4" />
                  API Key *
                </Label>
                <Input
                  id="apiKey"
                  type="password"
                  value={credentials.apiKey}
                  onChange={(e) => setCredentials({ ...credentials, apiKey: e.target.value })}
                  required
                  placeholder="Enter API Key"
                  className="h-11"
                  disabled={isLoading}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="apiSecret" className="text-sm font-semibold flex items-center gap-2">
                  <Key className="w-4 h-4" />
                  Security API Key *
                </Label>
                <Input
                  id="apiSecret"
                  type="password"
                  value={credentials.apiSecret}
                  onChange={(e) => setCredentials({ ...credentials, apiSecret: e.target.value })}
                  required
                  placeholder="Enter Security API Key"
                  className="h-11"
                  disabled={isLoading}
                />
              </div>
            </div>
          </div>

          <Separator className="my-4" />

          {/* Symbol and Side */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="symbol" className="text-sm font-semibold flex items-center gap-2">
                <DollarSign className="w-4 h-4" />
                Trading Symbol
              </Label>
              <Select
                value={formData.symbol}
                onValueChange={(value) => setFormData({ ...formData, symbol: value })}
              >
                <SelectTrigger className="h-12">
                  <SelectValue placeholder="Select symbol" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="BTC">BTC - Bitcoin</SelectItem>
                  <SelectItem value="ETH">ETH - Ethereum</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="side" className="text-sm font-semibold">Order Side</Label>
              <Select
                value={formData.side}
                onValueChange={(value: "buy" | "sell") => setFormData({ ...formData, side: value })}
              >
                <SelectTrigger className="h-12">
                  <SelectValue placeholder="Select side" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="buy">
                    <span className="text-green-500">Buy (Long)</span>
                  </SelectItem>
                  <SelectItem value="sell">
                    <span className="text-red-500">Sell (Short)</span>
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Entry Price and Size */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="entry_price" className="text-sm font-semibold">
                Entry Price *
              </Label>
              <Input
                id="entry_price"
                type="number"
                step="0.01"
                value={formData.entry_price || ""}
                onChange={(e) => setFormData({ ...formData, entry_price: parseFloat(e.target.value) || 0 })}
                required
                placeholder="0.00"
                className="h-12 text-lg"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="size" className="text-sm font-semibold">
                Order Size *
              </Label>
              <Input
                id="size"
                type="number"
                value={formData.size || ""}
                onChange={(e) => setFormData({ ...formData, size: parseInt(e.target.value) || 1 })}
                required
                placeholder="1"
                className="h-12 text-lg"
              />
            </div>
          </div>

          {/* Stop Loss and Take Profit */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="stop_loss_price" className="text-sm font-semibold flex items-center gap-2">
                <Shield className="w-4 h-4" />
                Stop Loss (Optional)
              </Label>
              <Input
                id="stop_loss_price"
                type="number"
                step="0.01"
                value={formData.stop_loss_price || ""}
                onChange={(e) => setFormData({ ...formData, stop_loss_price: parseFloat(e.target.value) || undefined })}
                placeholder="0.00"
                className="h-12 text-lg"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="take_profit_price" className="text-sm font-semibold flex items-center gap-2">
                <Target className="w-4 h-4" />
                Take Profit (Optional)
              </Label>
              <Input
                id="take_profit_price"
                type="number"
                step="0.01"
                value={formData.take_profit_price || ""}
                onChange={(e) => setFormData({ ...formData, take_profit_price: parseFloat(e.target.value) || undefined })}
                placeholder="0.00"
                className="h-12 text-lg"
              />
            </div>
          </div>

          {/* Additional Options */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="client_order_id" className="text-sm font-semibold">
                Client Order ID (Optional)
              </Label>
              <Input
                id="client_order_id"
                value={formData.client_order_id || ""}
                onChange={(e) => setFormData({ ...formData, client_order_id: e.target.value || undefined })}
                placeholder="Enter order ID"
                className="h-12"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="wait_time_seconds" className="text-sm font-semibold flex items-center gap-2">
                <Clock className="w-4 h-4" />
                Wait Time (seconds, min: 30)
              </Label>
              <Input
                id="wait_time_seconds"
                type="number"
                min={30}
                value={formData.wait_time_seconds || 60}
                onChange={(e) => setFormData({ ...formData, wait_time_seconds: parseInt(e.target.value) || 60 })}
                placeholder="60"
                className="h-12"
              />
            </div>
          </div>

          {/* Submit Button */}
          <Button 
            type="submit" 
            className="w-full h-14 text-lg font-semibold bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-lg disabled:opacity-70 disabled:cursor-not-allowed" 
            disabled={isLoading || !isConnected}
            size="lg"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                Processing Order...
              </>
            ) : formData.side === "buy" ? (
              <>
                <TrendingUp className="w-5 h-5 mr-2" />
                Place Buy Order
              </>
            ) : (
              <>
                <TrendingDown className="w-5 h-5 mr-2" />
                Place Sell Order
              </>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}

