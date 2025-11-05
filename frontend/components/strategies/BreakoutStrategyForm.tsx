"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { BreakoutStrategyConfig } from "@/lib/types";
import { startBreakoutStrategy } from "@/lib/api/strategies";
import { toast } from "sonner";
import { useAuthStore } from "@/store/auth";
import { Loader2, Play, Settings, Shield, Clock, TrendingUp } from "lucide-react";

export function BreakoutStrategyForm() {
  const { srpClientId, srpClientEmail } = useAuthStore();
  const [isLoading, setIsLoading] = useState(false);
  
  const [config, setConfig] = useState<BreakoutStrategyConfig>({
    trading: {
      symbol: "BTCUSD",
      product_id: 27,
      order_size: 1,
      max_position_size: 3,
      check_existing_orders: true,
    },
    schedule: {
      timeframe: "4h",
      timezone: "Asia/Kolkata",
      wait_for_next_candle: false,
      startup_delay_minutes: 0,
    },
    risk_management: {
      stop_loss_points: 10000,
      take_profit_points: 40000,
      breakeven_trigger_points: 10000,
    },
    monitoring: {
      order_check_interval: 10,
      position_check_interval: 5,
    },
    api: {
      base_url: undefined,
      api_key: undefined,
      api_secret: undefined,
    },
  });

  const [credentials, setCredentials] = useState({
    apiKey: "",
    apiSecret: "",
    baseUrl: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!srpClientId || !srpClientEmail) {
      toast.error("Please login first");
      return;
    }

    if (!credentials.apiKey || !credentials.apiSecret) {
      toast.error("Please provide Delta Exchange API credentials");
      return;
    }

    setIsLoading(true);

    try {
      const finalConfig: BreakoutStrategyConfig = {
        ...config,
        api: {
          base_url: credentials.baseUrl || undefined,
          api_key: credentials.apiKey,
          api_secret: credentials.apiSecret,
        },
      };

      const response = await startBreakoutStrategy(finalConfig, {
        srpClientId,
        srpClientEmail,
        deltaApiKey: credentials.apiKey,
        deltaApiSecret: credentials.apiSecret,
        deltaBaseUrl: credentials.baseUrl || undefined,
      });

      if (response.success) {
        toast.success(response.message);
        // Reset form
        setCredentials({ apiKey: "", apiSecret: "", baseUrl: "" });
        // Optionally redirect to strategies list or refresh
        setTimeout(() => {
          window.location.href = "/strategies";
        }, 1500);
      } else {
        toast.error(response.error || "Failed to start strategy");
      }
    } catch (error: any) {
      toast.error(error.detail || "Failed to start strategy");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TrendingUp className="w-5 h-5" />
          Breakout Strategy Configuration
        </CardTitle>
        <CardDescription>
          Configure and start a new breakout trading strategy instance
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Trading Configuration */}
          <div className="space-y-4">
            <div className="flex items-center gap-2 mb-4">
              <Settings className="w-4 h-4 text-blue-600" />
              <h3 className="text-lg font-semibold">Trading Configuration</h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="symbol">Symbol *</Label>
                <Input
                  id="symbol"
                  value={config.trading.symbol}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      trading: { ...config.trading, symbol: e.target.value },
                    })
                  }
                  placeholder="BTCUSD"
                  required
                />
              </div>
              <div>
                <Label htmlFor="product_id">Product ID *</Label>
                <Input
                  id="product_id"
                  type="number"
                  value={config.trading.product_id}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      trading: {
                        ...config.trading,
                        product_id: parseInt(e.target.value) || 0,
                      },
                    })
                  }
                  required
                />
              </div>
              <div>
                <Label htmlFor="order_size">Order Size *</Label>
                <Input
                  id="order_size"
                  type="number"
                  value={config.trading.order_size}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      trading: {
                        ...config.trading,
                        order_size: parseInt(e.target.value) || 0,
                      },
                    })
                  }
                  required
                />
              </div>
              <div>
                <Label htmlFor="max_position_size">Max Position Size</Label>
                <Input
                  id="max_position_size"
                  type="number"
                  value={config.trading.max_position_size || ""}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      trading: {
                        ...config.trading,
                        max_position_size: e.target.value
                          ? parseInt(e.target.value)
                          : undefined,
                      },
                    })
                  }
                  placeholder="Auto (order_size * 3)"
                />
              </div>
            </div>
          </div>

          <Separator />

          {/* Schedule Configuration */}
          <div className="space-y-4">
            <div className="flex items-center gap-2 mb-4">
              <Clock className="w-4 h-4 text-blue-600" />
              <h3 className="text-lg font-semibold">Schedule Configuration</h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="timeframe">Timeframe *</Label>
                <Select
                  value={config.schedule.timeframe}
                  onValueChange={(value: any) =>
                    setConfig({
                      ...config,
                      schedule: { ...config.schedule, timeframe: value },
                    })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1m">1 Minute</SelectItem>
                    <SelectItem value="3m">3 Minutes</SelectItem>
                    <SelectItem value="5m">5 Minutes</SelectItem>
                    <SelectItem value="15m">15 Minutes</SelectItem>
                    <SelectItem value="30m">30 Minutes</SelectItem>
                    <SelectItem value="1h">1 Hour</SelectItem>
                    <SelectItem value="2h">2 Hours</SelectItem>
                    <SelectItem value="4h">4 Hours</SelectItem>
                    <SelectItem value="6h">6 Hours</SelectItem>
                    <SelectItem value="1d">1 Day</SelectItem>
                    <SelectItem value="1w">1 Week</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="timezone">Timezone *</Label>
                <Input
                  id="timezone"
                  value={config.schedule.timezone}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      schedule: { ...config.schedule, timezone: e.target.value },
                    })
                  }
                  placeholder="Asia/Kolkata"
                  required
                />
              </div>
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="wait_for_next_candle"
                  checked={config.schedule.wait_for_next_candle}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      schedule: {
                        ...config.schedule,
                        wait_for_next_candle: e.target.checked,
                      },
                    })
                  }
                  className="rounded"
                />
                <Label htmlFor="wait_for_next_candle">
                  Wait for next candle before placing orders
                </Label>
              </div>
              <div>
                <Label htmlFor="startup_delay_minutes">Startup Delay (minutes)</Label>
                <Input
                  id="startup_delay_minutes"
                  type="number"
                  value={config.schedule.startup_delay_minutes || 0}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      schedule: {
                        ...config.schedule,
                        startup_delay_minutes: parseInt(e.target.value) || 0,
                      },
                    })
                  }
                />
              </div>
            </div>
          </div>

          <Separator />

          {/* Risk Management */}
          <div className="space-y-4">
            <div className="flex items-center gap-2 mb-4">
              <Shield className="w-4 h-4 text-blue-600" />
              <h3 className="text-lg font-semibold">Risk Management</h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <Label htmlFor="stop_loss_points">Stop Loss (points) *</Label>
                <Input
                  id="stop_loss_points"
                  type="number"
                  step="0.01"
                  value={config.risk_management.stop_loss_points}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      risk_management: {
                        ...config.risk_management,
                        stop_loss_points: parseFloat(e.target.value) || 0,
                      },
                    })
                  }
                  required
                />
              </div>
              <div>
                <Label htmlFor="take_profit_points">Take Profit (points) *</Label>
                <Input
                  id="take_profit_points"
                  type="number"
                  step="0.01"
                  value={config.risk_management.take_profit_points}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      risk_management: {
                        ...config.risk_management,
                        take_profit_points: parseFloat(e.target.value) || 0,
                      },
                    })
                  }
                  required
                />
              </div>
              <div>
                <Label htmlFor="breakeven_trigger_points">
                  Breakeven Trigger (points) *
                </Label>
                <Input
                  id="breakeven_trigger_points"
                  type="number"
                  step="0.01"
                  value={config.risk_management.breakeven_trigger_points}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      risk_management: {
                        ...config.risk_management,
                        breakeven_trigger_points: parseFloat(e.target.value) || 0,
                      },
                    })
                  }
                  required
                />
              </div>
            </div>
          </div>

          <Separator />

          {/* Monitoring Configuration */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Monitoring Configuration</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="order_check_interval">
                  Order Check Interval (seconds)
                </Label>
                <Input
                  id="order_check_interval"
                  type="number"
                  value={config.monitoring?.order_check_interval || 10}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      monitoring: {
                        ...config.monitoring,
                        order_check_interval: parseInt(e.target.value) || 10,
                      },
                    })
                  }
                />
              </div>
              <div>
                <Label htmlFor="position_check_interval">
                  Position Check Interval (seconds)
                </Label>
                <Input
                  id="position_check_interval"
                  type="number"
                  value={config.monitoring?.position_check_interval || 5}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      monitoring: {
                        ...config.monitoring,
                        position_check_interval: parseInt(e.target.value) || 5,
                      },
                    })
                  }
                />
              </div>
            </div>
          </div>

          <Separator />

          {/* API Credentials */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Delta Exchange API Credentials</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <Label htmlFor="api_key">API Key *</Label>
                <Input
                  id="api_key"
                  type="password"
                  value={credentials.apiKey}
                  onChange={(e) =>
                    setCredentials({ ...credentials, apiKey: e.target.value })
                  }
                  placeholder="Delta Exchange API Key"
                  required
                />
              </div>
              <div>
                <Label htmlFor="api_secret">API Secret *</Label>
                <Input
                  id="api_secret"
                  type="password"
                  value={credentials.apiSecret}
                  onChange={(e) =>
                    setCredentials({ ...credentials, apiSecret: e.target.value })
                  }
                  placeholder="Delta Exchange API Secret"
                  required
                />
              </div>
              <div>
                <Label htmlFor="base_url">Base URL (optional)</Label>
                <Input
                  id="base_url"
                  value={credentials.baseUrl}
                  onChange={(e) =>
                    setCredentials({ ...credentials, baseUrl: e.target.value })
                  }
                  placeholder="https://api.india.delta.exchange"
                />
              </div>
            </div>
          </div>

          <Button type="submit" disabled={isLoading} className="w-full">
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Starting Strategy...
              </>
            ) : (
              <>
                <Play className="mr-2 h-4 w-4" />
                Start Breakout Strategy
              </>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}

