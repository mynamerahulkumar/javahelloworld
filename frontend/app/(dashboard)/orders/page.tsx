"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useCredentialsStore } from "@/store/credentials";
import { Position } from "@/lib/types";
import CredentialsSetup from "@/components/trading/CredentialsSetup";
import PositionsTable from "@/components/trading/PositionsTable";
import OrderHistoryTable from "@/components/trading/OrderHistoryTable";
import { RefreshCw } from "lucide-react";
import { toast } from "sonner";
import { getPositionsDirect } from "@/lib/api/delta-direct";

export default function OrdersPage() {
  const { hasCredentials, getCredentials } = useCredentialsStore();
  const [positions, setPositions] = useState<Position[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [pollingInterval] = useState(5000); // Default 5 seconds
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  // Fetch positions directly from Delta Exchange API
  const fetchPositions = useCallback(async () => {
    if (!hasCredentials()) {
      return;
    }

    const credentials = getCredentials();
    if (!credentials?.deltaApiKey || !credentials?.deltaApiSecret) {
      return;
    }

    setIsLoading(true);
    try {
      // Fetch positions directly from Delta Exchange API
      const data = await getPositionsDirect(
        credentials.deltaApiKey,
        credentials.deltaApiSecret,
        credentials.deltaBaseUrl || 'https://api.india.delta.exchange'
      );

      // Convert response to Position array
      // The API returns { success: true, result: [...] } where result is an array of positions
      let positionsList: Position[] = [];
      
      if (data.result && Array.isArray(data.result)) {
        // Filter out positions with size 0 (closed positions)
        positionsList = data.result
          .filter((pos: any) => {
            const size = parseFloat(pos.size?.toString() || '0');
            return size !== 0; // Only show open positions
          })
          .map((pos: any) => ({
            user_id: pos.user_id || 0,
            product_id: pos.product_id || 0,
            product_symbol: pos.product_symbol || '',
            size: parseFloat(pos.size?.toString() || '0'),
            entry_price: pos.entry_price?.toString() || '0',
            margin: pos.margin?.toString() || '0',
            liquidation_price: pos.liquidation_price?.toString() || null,
            bankruptcy_price: pos.bankruptcy_price?.toString() || null,
            adl_level: pos.adl_level || null,
            commission: pos.commission?.toString() || null,
            realized_pnl: pos.realized_pnl?.toString() || null,
            realized_funding: pos.realized_funding?.toString() || null,
          }));
      }

      setPositions(positionsList);
    } catch (error: any) {
      console.error("Error fetching positions:", error);
      toast.error(error.message || "Failed to fetch positions");
      setPositions([]);
    } finally {
      setIsLoading(false);
    }
  }, [hasCredentials, getCredentials]);

  // Set up polling
  useEffect(() => {
    if (!hasCredentials()) {
      return;
    }

    // Initial fetch
    fetchPositions();

    // Set up interval
    intervalRef.current = setInterval(() => {
      fetchPositions();
    }, pollingInterval);

    // Cleanup
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [fetchPositions, pollingInterval, hasCredentials]);

  if (!hasCredentials()) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-1">Current Positions</h1>
          <p className="text-gray-600">
            Enter your Delta Exchange API credentials to view your open positions
          </p>
        </div>
        <CredentialsSetup />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-1">Orders</h1>
        <p className="text-gray-600">
          View your open positions and order history from Delta Exchange
        </p>
      </div>

      <Tabs defaultValue="positions" className="w-full">
        <TabsList className="grid w-full grid-cols-2 mb-6">
          <TabsTrigger value="positions" className="text-sm sm:text-base">
            Open Positions
          </TabsTrigger>
          <TabsTrigger value="history" className="text-sm sm:text-base">
            Order History
          </TabsTrigger>
        </TabsList>

        <TabsContent value="positions" className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">Current Positions</h2>
              <p className="text-sm text-gray-600">
                View your open trading positions from Delta Exchange
              </p>
            </div>
            <div className="flex items-center gap-2">
              <div className="hidden sm:block text-sm text-gray-500">
                Auto-refresh: {pollingInterval / 1000}s
              </div>
              <button
                onClick={fetchPositions}
                disabled={isLoading}
                className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
                title="Refresh positions"
              >
                <RefreshCw className={`w-5 h-5 ${isLoading ? "animate-spin" : ""}`} />
              </button>
            </div>
          </div>

          {/* Positions Table */}
          <PositionsTable
            positions={positions}
            isLoading={isLoading}
          />
        </TabsContent>

        <TabsContent value="history" className="space-y-6">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Order History</h2>
            <p className="text-sm text-gray-600">
              View your complete order history from Delta Exchange
            </p>
          </div>

          {/* Order History Table */}
          <OrderHistoryTable />
        </TabsContent>
      </Tabs>

      {/* Credentials management (collapsible) */}
      <div className="mt-6">
        <details className="border rounded-lg p-4">
          <summary className="cursor-pointer font-semibold text-sm text-gray-700 hover:text-gray-900">
            Manage API Credentials
          </summary>
          <div className="mt-4">
            <CredentialsSetup />
          </div>
        </details>
      </div>
    </div>
  );
}
