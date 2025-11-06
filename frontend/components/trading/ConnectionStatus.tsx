"use client";

import { Badge } from "@/components/ui/badge";
import { useDeltaConnection } from "@/hooks/useDeltaConnection";
import { CheckCircle2, XCircle, Loader2, Clock } from "lucide-react";

export default function ConnectionStatus() {
  const { connectionStatus, isConnected, isTesting, lastConnectionTest } = useDeltaConnection();

  const getStatusBadge = () => {
    if (isTesting) {
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

  return (
    <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 p-3 bg-white rounded-lg border border-gray-200">
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium text-gray-700">Connection Status:</span>
        {getStatusBadge()}
      </div>
      {lastConnectionTest && (
        <div className="flex items-center gap-1 text-xs text-gray-500">
          <Clock className="w-3 h-3" />
          <span>Last test: {lastConnectionTest.toLocaleTimeString()}</span>
        </div>
      )}
    </div>
  );
}

