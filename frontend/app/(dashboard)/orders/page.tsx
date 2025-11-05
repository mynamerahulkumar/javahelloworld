"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { TrendingUp, TrendingDown, Clock, CheckCircle, XCircle, AlertCircle } from "lucide-react";

export default function OrdersPage() {
  // Placeholder data - will be replaced with real API data
  const activeOrders: any[] = [];
  const orderHistory: any[] = [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-1">Order Management</h1>
        <p className="text-gray-600">
          View and manage your trading orders
        </p>
      </div>

      <Tabs defaultValue="active" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="active" className="flex items-center gap-2">
            <Clock className="w-4 h-4" />
            Active Orders
          </TabsTrigger>
          <TabsTrigger value="history" className="flex items-center gap-2">
            <CheckCircle className="w-4 h-4" />
            Order History
          </TabsTrigger>
        </TabsList>

        <TabsContent value="active" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Active Orders</CardTitle>
              <CardDescription>Your currently active and pending orders</CardDescription>
            </CardHeader>
            <CardContent>
              {activeOrders.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <Clock className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p className="text-lg font-medium">No active orders</p>
                  <p className="text-sm mt-2">Your active orders will appear here</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {activeOrders.map((order) => (
                    <div key={order.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors">
                      <div className="flex items-center gap-4">
                        {order.side === "buy" ? (
                          <TrendingUp className="w-6 h-6 text-green-500" />
                        ) : (
                          <TrendingDown className="w-6 h-6 text-red-500" />
                        )}
                        <div>
                          <div className="font-semibold text-lg">{order.symbol}</div>
                          <div className="text-sm text-gray-500">{order.type} • {order.side.toUpperCase()}</div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-semibold text-lg">${order.price?.toLocaleString()}</div>
                        <div className="text-sm text-gray-500">Size: {order.size}</div>
                      </div>
                      <Badge variant={order.status === "filled" ? "default" : "secondary"}>
                        {order.status}
                      </Badge>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="history" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Order History</CardTitle>
              <CardDescription>Your completed and cancelled orders</CardDescription>
            </CardHeader>
            <CardContent>
              {orderHistory.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <CheckCircle className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p className="text-lg font-medium">No order history</p>
                  <p className="text-sm mt-2">Your order history will appear here</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {orderHistory.map((order) => (
                    <div key={order.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors">
                      <div className="flex items-center gap-4">
                        {order.side === "buy" ? (
                          <TrendingUp className="w-6 h-6 text-green-500" />
                        ) : (
                          <TrendingDown className="w-6 h-6 text-red-500" />
                        )}
                        <div>
                          <div className="font-semibold text-lg">{order.symbol}</div>
                          <div className="text-sm text-gray-500">
                            {order.type} • {order.side.toUpperCase()} • {new Date(order.created_at).toLocaleString()}
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-semibold text-lg">${order.price?.toLocaleString()}</div>
                        <div className="text-sm text-gray-500">Size: {order.size}</div>
                      </div>
                      <Badge 
                        variant={order.status === "filled" ? "default" : order.status === "cancelled" ? "destructive" : "secondary"}
                      >
                        {order.status}
                      </Badge>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
