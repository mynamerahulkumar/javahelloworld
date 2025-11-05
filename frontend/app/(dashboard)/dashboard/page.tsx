"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { OrderForm } from "@/components/trading/OrderForm";
import { PriceDisplay } from "@/components/trading/PriceDisplay";
import { PriceChart } from "@/components/charts/PriceChart";
import { OrderHistory } from "@/components/trading/OrderHistory";
import { TrendingUp, Zap, Target } from "lucide-react";
import { getTicker, getPriceFetchInterval } from "@/lib/api/trading";

interface PriceData {
  price: number;
  change24h?: number;
  changePercent24h?: number;
  previousPrice?: number;
}

export default function DashboardPage() {
  const [selectedSymbol, setSelectedSymbol] = useState("BTC");
  const [btcPrice, setBtcPrice] = useState<PriceData>({ price: 0 });
  const [ethPrice, setEthPrice] = useState<PriceData>({ price: 0 });
  const [fetchInterval, setFetchInterval] = useState(5000); // Default 5 seconds
  const [isLoading, setIsLoading] = useState(true);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const previousPricesRef = useRef<{ btc: number | null; eth: number | null }>({ btc: null, eth: null });

  // Fetch price fetch interval from backend
  useEffect(() => {
    const loadInterval = async () => {
      try {
        const response = await getPriceFetchInterval();
        setFetchInterval(response.interval_seconds * 1000); // Convert to milliseconds
      } catch (error) {
        console.error("Failed to load price fetch interval, using default 5 seconds:", error);
        // Keep default 5 seconds if fetch fails
      }
    };
    loadInterval();
  }, []);

  // Fetch ticker prices
  const fetchPrices = useCallback(async () => {
    try {
      const [btcResponse, ethResponse] = await Promise.all([
        getTicker("BTCUSD"),
        getTicker("ETHUSD"),
      ]);

      // Update BTC price
      if (btcResponse.success && btcResponse.mark_price) {
        const currentBtcPrice = btcResponse.mark_price;
        const previousBtcPrice = previousPricesRef.current.btc;
        
        setBtcPrice({
          price: currentBtcPrice,
          previousPrice: previousBtcPrice || currentBtcPrice,
          change24h: btcResponse.close && btcResponse.close !== currentBtcPrice 
            ? currentBtcPrice - btcResponse.close 
            : previousBtcPrice 
              ? currentBtcPrice - previousBtcPrice 
              : undefined,
          changePercent24h: btcResponse.close && btcResponse.close !== currentBtcPrice
            ? ((currentBtcPrice - btcResponse.close) / btcResponse.close) * 100
            : previousBtcPrice && previousBtcPrice !== currentBtcPrice
              ? ((currentBtcPrice - previousBtcPrice) / previousBtcPrice) * 100
              : undefined,
        });
        
        previousPricesRef.current.btc = currentBtcPrice;
      }

      // Update ETH price
      if (ethResponse.success && ethResponse.mark_price) {
        const currentEthPrice = ethResponse.mark_price;
        const previousEthPrice = previousPricesRef.current.eth;
        
        setEthPrice({
          price: currentEthPrice,
          previousPrice: previousEthPrice || currentEthPrice,
          change24h: ethResponse.close && ethResponse.close !== currentEthPrice
            ? currentEthPrice - ethResponse.close
            : previousEthPrice
              ? currentEthPrice - previousEthPrice
              : undefined,
          changePercent24h: ethResponse.close && ethResponse.close !== currentEthPrice
            ? ((currentEthPrice - ethResponse.close) / ethResponse.close) * 100
            : previousEthPrice && previousEthPrice !== currentEthPrice
              ? ((currentEthPrice - previousEthPrice) / previousEthPrice) * 100
              : undefined,
        });
        
        previousPricesRef.current.eth = currentEthPrice;
      }

      setIsLoading(false);
    } catch (error) {
      console.error("Error fetching prices:", error);
      setIsLoading(false);
    }
  }, []);

  // Set up interval to fetch prices
  useEffect(() => {
    // Fetch immediately on mount
    fetchPrices();

    // Set up interval
    intervalRef.current = setInterval(() => {
      fetchPrices();
    }, fetchInterval);

    // Cleanup interval on unmount or when interval changes
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [fetchInterval, fetchPrices]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-1">Trading Dashboard</h1>
          <p className="text-gray-600">
            Professional algorithmic trading platform with advanced order management
          </p>
        </div>
      </div>

      {/* Price Display */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <PriceDisplay 
          symbol="BTC" 
          price={btcPrice.price} 
          change24h={btcPrice.change24h} 
          changePercent24h={btcPrice.changePercent24h}
        />
        <PriceDisplay 
          symbol="ETH" 
          price={ethPrice.price} 
          change24h={ethPrice.change24h} 
          changePercent24h={ethPrice.changePercent24h}
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Order Forms - Takes 2 columns */}
        <div className="lg:col-span-2 space-y-6">
          <Tabs defaultValue="limit-wait" className="w-full">
            <TabsList className="grid w-full grid-cols-3 h-14 p-1.5 bg-gradient-to-r from-gray-50 via-gray-100 to-gray-50 rounded-xl shadow-inner border border-gray-200/50 backdrop-blur-sm">
              <TabsTrigger 
                value="limit-wait" 
                className="group flex items-center justify-center gap-2.5 px-4 py-3 text-sm font-semibold rounded-lg transition-all duration-300 ease-in-out data-[state=active]:bg-gradient-to-br data-[state=active]:from-blue-500 data-[state=active]:to-blue-600 data-[state=active]:text-white data-[state=active]:shadow-lg data-[state=active]:shadow-blue-500/50 data-[state=active]:scale-[1.02] data-[state=inactive]:text-gray-600 data-[state=inactive]:hover:text-gray-900 data-[state=inactive]:hover:bg-gray-50/80 data-[state=active]:border data-[state=active]:border-blue-400/30 relative overflow-hidden"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-blue-400/0 via-blue-400/0 to-blue-400/0 group-data-[state=active]:from-blue-400/20 group-data-[state=active]:via-blue-400/10 group-data-[state=active]:to-blue-400/20 transition-all duration-300" />
                <Target className="w-5 h-5 relative z-10 transition-transform duration-300 group-data-[state=active]:scale-110" />
                <span className="hidden sm:inline relative z-10">Limit (Wait)</span>
                <span className="sm:hidden relative z-10">Wait</span>
              </TabsTrigger>
              <TabsTrigger 
                value="market" 
                className="group flex items-center justify-center gap-2.5 px-4 py-3 text-sm font-semibold rounded-lg transition-all duration-300 ease-in-out data-[state=active]:bg-gradient-to-br data-[state=active]:from-amber-500 data-[state=active]:to-orange-500 data-[state=active]:text-white data-[state=active]:shadow-lg data-[state=active]:shadow-amber-500/50 data-[state=active]:scale-[1.02] data-[state=inactive]:text-gray-600 data-[state=inactive]:hover:text-gray-900 data-[state=inactive]:hover:bg-gray-50/80 data-[state=active]:border data-[state=active]:border-amber-400/30 relative overflow-hidden"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-amber-400/0 via-amber-400/0 to-amber-400/0 group-data-[state=active]:from-amber-400/20 group-data-[state=active]:via-amber-400/10 group-data-[state=active]:to-amber-400/20 transition-all duration-300" />
                <Zap className="w-5 h-5 relative z-10 transition-transform duration-300 group-data-[state=active]:scale-110" />
                <span className="relative z-10">Market</span>
              </TabsTrigger>
              <TabsTrigger 
                value="limit" 
                className="group flex items-center justify-center gap-2.5 px-4 py-3 text-sm font-semibold rounded-lg transition-all duration-300 ease-in-out data-[state=active]:bg-gradient-to-br data-[state=active]:from-emerald-500 data-[state=active]:to-teal-600 data-[state=active]:text-white data-[state=active]:shadow-lg data-[state=active]:shadow-emerald-500/50 data-[state=active]:scale-[1.02] data-[state=inactive]:text-gray-600 data-[state=inactive]:hover:text-gray-900 data-[state=inactive]:hover:bg-gray-50/80 data-[state=active]:border data-[state=active]:border-emerald-400/30 relative overflow-hidden"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-emerald-400/0 via-emerald-400/0 to-emerald-400/0 group-data-[state=active]:from-emerald-400/20 group-data-[state=active]:via-emerald-400/10 group-data-[state=active]:to-emerald-400/20 transition-all duration-300" />
                <TrendingUp className="w-5 h-5 relative z-10 transition-transform duration-300 group-data-[state=active]:scale-110" />
                <span className="relative z-10">Limit</span>
              </TabsTrigger>
            </TabsList>
            
            <TabsContent value="limit-wait" className="mt-6">
              <OrderForm orderType="limit-wait" />
            </TabsContent>
            
            <TabsContent value="market" className="mt-6">
              <Card>
                <CardHeader>
                  <CardTitle>Market Order</CardTitle>
                  <CardDescription>Coming soon - Market order execution</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-500">
                    Market order functionality will be available soon. This feature will allow you to execute orders immediately at the current market price.
                  </p>
                </CardContent>
              </Card>
            </TabsContent>
            
            <TabsContent value="limit" className="mt-6">
              <Card>
                <CardHeader>
                  <CardTitle>Limit Order</CardTitle>
                  <CardDescription>Coming soon - Regular limit order execution</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-500">
                    Regular limit order functionality will be available soon. This feature will allow you to place limit orders at specific prices.
                  </p>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>

          {/* Price Chart */}
          <Card>
            <CardHeader>
              <CardTitle>Price Chart</CardTitle>
              <CardDescription>Real-time price visualization for {selectedSymbol}</CardDescription>
            </CardHeader>
            <CardContent>
              <PriceChart />
            </CardContent>
          </Card>
        </div>

        {/* Sidebar - Order History */}
        <div className="lg:col-span-1">
          <OrderHistory />
        </div>
      </div>
    </div>
  );
}
