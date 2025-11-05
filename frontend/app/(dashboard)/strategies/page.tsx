"use client";

import { useState, useEffect, useCallback } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { BreakoutStrategyForm } from "@/components/strategies/BreakoutStrategyForm";
import { StrategyStatus } from "@/components/strategies/StrategyStatus";
import { getAllStrategies } from "@/lib/api/strategies";
import { StrategyStatus as StrategyStatusType } from "@/lib/types";
import { useAuthStore } from "@/store/auth";
import { toast } from "sonner";
import { RefreshCw, Plus, List } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function StrategiesPage() {
  const { srpClientId, srpClientEmail } = useAuthStore();
  const [strategies, setStrategies] = useState<StrategyStatusType[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const fetchStrategies = useCallback(async () => {
    if (!srpClientId || !srpClientEmail) {
      return;
    }

    try {
      const response = await getAllStrategies({
        srpClientId,
        srpClientEmail,
      });
      setStrategies(response.strategies);
    } catch (error: any) {
      console.error("Error fetching strategies:", error);
      // Don't show toast on every poll, only on manual refresh
    }
  }, [srpClientId, srpClientEmail]);

  const handleStrategyStopped = useCallback(() => {
    fetchStrategies();
  }, [fetchStrategies]);

  const handleManualRefresh = async () => {
    setIsLoading(true);
    try {
      await fetchStrategies();
      toast.success("Strategies refreshed");
    } catch (error: any) {
      toast.error(error.detail || "Failed to refresh strategies");
    } finally {
      setIsLoading(false);
    }
  };

  // Initial fetch
  useEffect(() => {
    fetchStrategies();
  }, [fetchStrategies]);

  // Set up polling for running strategies
  useEffect(() => {
    const hasRunningStrategies = strategies.some((s) => s.status === "running");
    
    if (hasRunningStrategies) {
      // Poll every 5 seconds if there are running strategies
      const interval = setInterval(() => {
        fetchStrategies();
      }, 5000);

      return () => {
        clearInterval(interval);
      };
    }
    // Cleanup handled by return function above
  }, [strategies.length, fetchStrategies]); // Depend on length and fetchStrategies

  const runningStrategies = strategies.filter((s) => s.status === "running");
  const stoppedStrategies = strategies.filter((s) => s.status === "stopped");
  const errorStrategies = strategies.filter((s) => s.status === "error");

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 bg-clip-text text-transparent mb-2">
            Trading Strategies
          </h1>
          <p className="text-gray-600 text-lg">
            Manage and monitor your algorithmic trading strategies
          </p>
        </div>
        <Button
          variant="outline"
          onClick={handleManualRefresh}
          disabled={isLoading}
          className="border-2 hover:bg-blue-50 hover:border-blue-300 transition-all duration-200"
        >
          <RefreshCw
            className={`w-4 h-4 mr-2 ${isLoading ? "animate-spin" : ""}`}
          />
          Refresh
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card className="bg-gradient-to-br from-green-50 to-emerald-50 border-green-200 shadow-md">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-green-700 mb-1">Running</p>
                <p className="text-3xl font-bold text-green-600">{runningStrategies.length}</p>
              </div>
              <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center">
                <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse"></div>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-gray-50 to-slate-50 border-gray-200 shadow-md">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-700 mb-1">Stopped</p>
                <p className="text-3xl font-bold text-gray-600">{stoppedStrategies.length}</p>
              </div>
              <div className="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center">
                <div className="w-3 h-3 rounded-full bg-gray-400"></div>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-red-50 to-rose-50 border-red-200 shadow-md">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-red-700 mb-1">Errors</p>
                <p className="text-3xl font-bold text-red-600">{errorStrategies.length}</p>
              </div>
              <div className="w-12 h-12 rounded-full bg-red-100 flex items-center justify-center">
                <div className="w-3 h-3 rounded-full bg-red-500"></div>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200 shadow-md">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-blue-700 mb-1">Total</p>
                <p className="text-3xl font-bold text-blue-600">{strategies.length}</p>
              </div>
              <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
                <List className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <Tabs defaultValue="list" className="w-full">
        <TabsList className="grid w-full grid-cols-2 h-14 p-1.5 bg-gradient-to-r from-gray-50 via-gray-100 to-gray-50 rounded-xl shadow-inner border border-gray-200/50 backdrop-blur-sm">
          <TabsTrigger 
            value="list" 
            className="flex items-center gap-2 px-4 py-3 text-sm font-semibold rounded-lg transition-all duration-300 ease-in-out data-[state=active]:bg-gradient-to-br data-[state=active]:from-blue-500 data-[state=active]:to-indigo-600 data-[state=active]:text-white data-[state=active]:shadow-lg data-[state=active]:shadow-blue-500/50 data-[state=active]:scale-[1.02] data-[state=inactive]:text-gray-600 data-[state=inactive]:hover:text-gray-900 data-[state=inactive]:hover:bg-gray-50/80"
          >
            <List className="w-4 h-4" />
            Strategies ({strategies.length})
          </TabsTrigger>
          <TabsTrigger 
            value="new" 
            className="flex items-center gap-2 px-4 py-3 text-sm font-semibold rounded-lg transition-all duration-300 ease-in-out data-[state=active]:bg-gradient-to-br data-[state=active]:from-emerald-500 data-[state=active]:to-teal-600 data-[state=active]:text-white data-[state=active]:shadow-lg data-[state=active]:shadow-emerald-500/50 data-[state=active]:scale-[1.02] data-[state=inactive]:text-gray-600 data-[state=inactive]:hover:text-gray-900 data-[state=inactive]:hover:bg-gray-50/80"
          >
            <Plus className="w-4 h-4" />
            Start New Strategy
          </TabsTrigger>
        </TabsList>

        <TabsContent value="list" className="mt-6 space-y-8">
          {/* Running Strategies */}
          {runningStrategies.length > 0 && (
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="w-1 h-8 bg-gradient-to-b from-green-500 to-emerald-600 rounded-full"></div>
                <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse"></div>
                  Running Strategies
                  <span className="text-lg font-normal text-gray-500">({runningStrategies.length})</span>
                </h2>
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {runningStrategies.map((strategy) => (
                  <StrategyStatus
                    key={strategy.strategy_id}
                    strategy={strategy}
                    onStop={handleStrategyStopped}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Stopped Strategies */}
          {stoppedStrategies.length > 0 && (
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="w-1 h-8 bg-gradient-to-b from-gray-400 to-gray-500 rounded-full"></div>
                <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-gray-400"></div>
                  Stopped Strategies
                  <span className="text-lg font-normal text-gray-500">({stoppedStrategies.length})</span>
                </h2>
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {stoppedStrategies.map((strategy) => (
                  <StrategyStatus
                    key={strategy.strategy_id}
                    strategy={strategy}
                    onStop={handleStrategyStopped}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Error Strategies */}
          {errorStrategies.length > 0 && (
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="w-1 h-8 bg-gradient-to-b from-red-500 to-rose-600 rounded-full"></div>
                <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-red-500"></div>
                  Error Strategies
                  <span className="text-lg font-normal text-gray-500">({errorStrategies.length})</span>
                </h2>
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {errorStrategies.map((strategy) => (
                  <StrategyStatus
                    key={strategy.strategy_id}
                    strategy={strategy}
                    onStop={handleStrategyStopped}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Empty State */}
          {strategies.length === 0 && (
            <Card className="border-2 border-dashed border-gray-300 bg-gradient-to-br from-gray-50 to-blue-50/30">
              <CardContent className="py-16 text-center">
                <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-gradient-to-br from-blue-100 to-indigo-100 flex items-center justify-center">
                  <List className="w-10 h-10 text-blue-600" />
                </div>
                <h3 className="text-2xl font-bold text-gray-800 mb-2">No Strategies Yet</h3>
                <p className="text-gray-600 mb-6 max-w-md mx-auto">
                  Start your first algorithmic trading strategy to begin automated trading
                </p>
                <Button
                  onClick={() => {
                    const tabsList = document.querySelector('[role="tablist"]');
                    const newTab = tabsList?.querySelector('[value="new"]') as HTMLElement;
                    newTab?.click();
                  }}
                  className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-lg hover:shadow-xl transition-all duration-200"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Start New Strategy
                </Button>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="new" className="mt-6">
          <BreakoutStrategyForm />
        </TabsContent>
      </Tabs>
    </div>
  );
}

