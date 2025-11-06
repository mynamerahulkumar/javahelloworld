"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useCredentialsStore } from "@/store/credentials";
import { getOrderHistory } from "@/lib/api/delta-direct";
import { OrderHistoryItem, OrderHistoryMeta } from "@/lib/types";
import { RefreshCw, ChevronLeft, ChevronRight, Loader2 } from "lucide-react";
import { toast } from "sonner";

export default function OrderHistoryTable() {
  const { hasCredentials, getCredentials } = useCredentialsStore();
  const [orders, setOrders] = useState<OrderHistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [pagination, setPagination] = useState<OrderHistoryMeta | null>(null);
  const [currentPage, setCurrentPage] = useState<"after" | "before" | null>(null);
  const [pageToken, setPageToken] = useState<string | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const fetchOrderHistory = useCallback(async (after?: string, before?: string) => {
    if (!hasCredentials()) {
      return;
    }

    const credentials = getCredentials();
    if (!credentials?.deltaApiKey || !credentials?.deltaApiSecret) {
      return;
    }

    setIsLoading(true);
    try {
      const data = await getOrderHistory(
        credentials.deltaApiKey,
        credentials.deltaApiSecret,
        credentials.deltaBaseUrl || 'https://api.india.delta.exchange',
        after,
        before
      );

      if (data.result && Array.isArray(data.result)) {
        setOrders(data.result);
        setPagination(data.meta || null);
      } else {
        setOrders([]);
        setPagination(null);
      }
    } catch (error: any) {
      console.error("Error fetching order history:", error);
      toast.error(error.message || "Failed to fetch order history");
      setOrders([]);
      setPagination(null);
    } finally {
      setIsLoading(false);
    }
  }, [hasCredentials, getCredentials]);

  useEffect(() => {
    if (!hasCredentials()) {
      return;
    }

    // Initial fetch
    fetchOrderHistory();

    // Set up polling every 30 seconds
    intervalRef.current = setInterval(() => {
      fetchOrderHistory();
    }, 30000);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [hasCredentials, fetchOrderHistory]);

  const handleNextPage = () => {
    if (pagination?.after) {
      setCurrentPage("after");
      setPageToken(pagination.after);
      fetchOrderHistory(pagination.after, undefined);
    }
  };

  const handlePrevPage = () => {
    if (pagination?.before) {
      setCurrentPage("before");
      setPageToken(pagination.before);
      fetchOrderHistory(undefined, pagination.before);
    }
  };

  const getStateBadge = (state: string) => {
    const stateColors: Record<string, string> = {
      open: "bg-blue-50 text-blue-700 border-blue-200",
      filled: "bg-green-50 text-green-700 border-green-200",
      cancelled: "bg-gray-50 text-gray-700 border-gray-200",
      rejected: "bg-red-50 text-red-700 border-red-200",
    };

    return (
      <Badge
        variant="outline"
        className={stateColors[state.toLowerCase()] || "bg-gray-50 text-gray-700 border-gray-200"}
      >
        {state}
      </Badge>
    );
  };

  const formatDate = (timestamp: string) => {
    try {
      // Handle nanosecond timestamp (if it's a very large number)
      let date: Date;
      if (timestamp.length > 13) {
        // Nanosecond timestamp, convert to milliseconds
        const nanoseconds = BigInt(timestamp);
        const milliseconds = Number(nanoseconds / BigInt(1000000));
        date = new Date(milliseconds);
      } else {
        // Regular timestamp
        const num = parseInt(timestamp);
        date = new Date(num > 1000000000000 ? num : num * 1000);
      }
      return date.toLocaleString();
    } catch {
      return timestamp;
    }
  };

  if (!hasCredentials()) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Order History</CardTitle>
          <CardDescription>Configure your Delta API credentials to view order history</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Order History</CardTitle>
            <CardDescription>View your trading order history from Delta Exchange</CardDescription>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => fetchOrderHistory()}
            disabled={isLoading}
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading && orders.length === 0 ? (
          <div className="text-center py-8">
            <Loader2 className="w-8 h-8 mx-auto animate-spin text-gray-400" />
            <p className="mt-2 text-sm text-gray-500">Loading order history...</p>
          </div>
        ) : orders.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-sm text-gray-500">No orders found</p>
          </div>
        ) : (
          <>
            {/* Desktop Table View */}
            <div className="hidden md:block overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-3 font-semibold text-sm">ID</th>
                    <th className="text-left p-3 font-semibold text-sm">Symbol</th>
                    <th className="text-left p-3 font-semibold text-sm">Side</th>
                    <th className="text-right p-3 font-semibold text-sm">Size</th>
                    <th className="text-right p-3 font-semibold text-sm">Price</th>
                    <th className="text-left p-3 font-semibold text-sm">Type</th>
                    <th className="text-left p-3 font-semibold text-sm">State</th>
                    <th className="text-right p-3 font-semibold text-sm">Commission</th>
                    <th className="text-left p-3 font-semibold text-sm">Created</th>
                  </tr>
                </thead>
                <tbody>
                  {orders.map((order) => (
                    <tr key={order.id} className="border-b hover:bg-gray-50">
                      <td className="p-3 text-sm">{order.id}</td>
                      <td className="p-3 text-sm font-medium">{order.product_symbol}</td>
                      <td className="p-3 text-sm">
                        <Badge
                          variant="outline"
                          className={
                            order.side === "buy"
                              ? "bg-green-50 text-green-700 border-green-200"
                              : "bg-red-50 text-red-700 border-red-200"
                          }
                        >
                          {order.side.toUpperCase()}
                        </Badge>
                      </td>
                      <td className="p-3 text-sm text-right">{order.size}</td>
                      <td className="p-3 text-sm text-right">
                        {order.limit_price ? parseFloat(order.limit_price).toFixed(2) : "-"}
                      </td>
                      <td className="p-3 text-sm">{order.order_type}</td>
                      <td className="p-3 text-sm">{getStateBadge(order.state)}</td>
                      <td className="p-3 text-sm text-right">
                        {order.commission ? parseFloat(order.commission).toFixed(4) : "-"}
                      </td>
                      <td className="p-3 text-sm text-gray-500">{formatDate(order.created_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Mobile Card View */}
            <div className="md:hidden space-y-4">
              {orders.map((order) => (
                <div
                  key={order.id}
                  className="p-4 border rounded-lg space-y-2 bg-white hover:bg-gray-50"
                >
                  <div className="flex items-center justify-between">
                    <div className="font-semibold text-sm">{order.product_symbol}</div>
                    {getStateBadge(order.state)}
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <span className="text-gray-500">Side:</span>
                      <Badge
                        variant="outline"
                        className={`ml-2 ${
                          order.side === "buy"
                            ? "bg-green-50 text-green-700 border-green-200"
                            : "bg-red-50 text-red-700 border-red-200"
                        }`}
                      >
                        {order.side.toUpperCase()}
                      </Badge>
                    </div>
                    <div>
                      <span className="text-gray-500">Size:</span>
                      <span className="ml-2 font-medium">{order.size}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Price:</span>
                      <span className="ml-2 font-medium">
                        {order.limit_price ? parseFloat(order.limit_price).toFixed(2) : "-"}
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-500">Type:</span>
                      <span className="ml-2 font-medium">{order.order_type}</span>
                    </div>
                    {order.commission && (
                      <div>
                        <span className="text-gray-500">Commission:</span>
                        <span className="ml-2 font-medium">
                          {parseFloat(order.commission).toFixed(4)}
                        </span>
                      </div>
                    )}
                    <div className="col-span-2">
                      <span className="text-gray-500">Created:</span>
                      <span className="ml-2 text-xs">{formatDate(order.created_at)}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination */}
            {(pagination?.after || pagination?.before) && (
              <div className="flex items-center justify-between mt-4 pt-4 border-t">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handlePrevPage}
                  disabled={!pagination?.before || isLoading}
                >
                  <ChevronLeft className="w-4 h-4 mr-1" />
                  Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleNextPage}
                  disabled={!pagination?.after || isLoading}
                >
                  Next
                  <ChevronRight className="w-4 h-4 ml-1" />
                </Button>
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
}
