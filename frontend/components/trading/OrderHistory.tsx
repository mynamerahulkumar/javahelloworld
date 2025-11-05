"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, TrendingDown, Clock, CheckCircle, XCircle } from "lucide-react";

export function OrderHistory() {
  // Placeholder for order history
  const orders: any[] = []; // Will be populated from API later

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Clock className="w-5 h-5" />
          Order History
        </CardTitle>
        <CardDescription>Your recent trading orders</CardDescription>
      </CardHeader>
      <CardContent>
        {orders.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <Clock className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p className="text-lg font-medium">No orders yet</p>
            <p className="text-sm mt-2">Your order history will appear here</p>
          </div>
        ) : (
          <div className="space-y-3">
            {orders.map((order) => (
              <div key={order.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center gap-3">
                  {order.side === "buy" ? (
                    <TrendingUp className="w-5 h-5 text-green-500" />
                  ) : (
                    <TrendingDown className="w-5 h-5 text-red-500" />
                  )}
                  <div>
                    <div className="font-semibold">{order.symbol}</div>
                    <div className="text-sm text-gray-500">{order.type}</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-semibold">${order.price}</div>
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
  );
}

