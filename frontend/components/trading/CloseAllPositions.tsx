"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useCredentialsStore } from "@/store/credentials";
import { closeAllPositions } from "@/lib/api/delta-direct";
import { toast } from "sonner";
import { X, AlertTriangle, Loader2 } from "lucide-react";
import { useDeltaConnection } from "@/hooks/useDeltaConnection";

export default function CloseAllPositions() {
  const { credentials, hasCredentials } = useCredentialsStore();
  const { isConnected } = useDeltaConnection();
  const [isOpen, setIsOpen] = useState(false);
  const [isClosing, setIsClosing] = useState(false);

  const handleCloseAll = async () => {
    if (!hasCredentials()) {
      toast.error("Please configure your Delta API credentials first");
      return;
    }

    const creds = credentials;
    if (!creds?.deltaApiKey || !creds?.deltaApiSecret) {
      toast.error("Delta API credentials are missing");
      return;
    }

    setIsClosing(true);
    try {
      const result = await closeAllPositions(
        creds.deltaApiKey,
        creds.deltaApiSecret,
        creds.deltaBaseUrl || 'https://api.india.delta.exchange',
        0 // user_id
      );

      if (result.success) {
        toast.success("All positions closed successfully");
        setIsOpen(false);
        // Refresh positions after a short delay
        setTimeout(() => {
          window.location.reload();
        }, 1000);
      } else {
        throw new Error(result.error || "Failed to close all positions");
      }
    } catch (error: any) {
      console.error("Error closing all positions:", error);
      toast.error(error.message || "Failed to close all positions");
    } finally {
      setIsClosing(false);
    }
  };

  if (!hasCredentials() || !isConnected) {
    return null;
  }

  return (
    <>
      <Button
        variant="destructive"
        onClick={() => setIsOpen(true)}
        className="w-full sm:w-auto bg-red-600 hover:bg-red-700 text-white font-semibold shadow-lg hover:shadow-xl transition-all duration-200 border-2 border-red-700"
        disabled={!isConnected}
        size="lg"
      >
        <X className="w-5 h-5 mr-2" />
        Close All Positions
      </Button>

      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogContent className="sm:max-w-[500px] bg-white border-2 border-red-200 shadow-2xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-xl font-bold text-red-700">
              <AlertTriangle className="w-6 h-6 text-red-600" />
              Close All Positions
            </DialogTitle>
            <DialogDescription className="text-base text-gray-700 mt-2">
              <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
                <p className="font-semibold text-red-800 mb-2">⚠️ Warning: This action cannot be undone!</p>
                <p className="text-red-700">
                  Are you sure you want to close <strong>ALL</strong> open positions? 
                  All portfolio and isolated positions will be closed immediately.
                </p>
              </div>
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="flex-col sm:flex-row gap-3 mt-4">
            <Button
              variant="outline"
              onClick={() => setIsOpen(false)}
              disabled={isClosing}
              className="w-full sm:w-auto border-2 border-gray-300 hover:bg-gray-50 font-medium"
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleCloseAll}
              disabled={isClosing}
              className="w-full sm:w-auto bg-red-600 hover:bg-red-700 text-white font-semibold shadow-lg border-2 border-red-700"
            >
              {isClosing ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Closing All Positions...
                </>
              ) : (
                <>
                  <X className="w-4 h-4 mr-2" />
                  Yes, Close All Positions
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}


