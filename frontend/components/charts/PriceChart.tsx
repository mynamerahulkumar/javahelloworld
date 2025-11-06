"use client";

import { useEffect, useState, useRef } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from "recharts";

interface PriceChartProps {
  data?: Array<{ time: string; price: number }>;
  symbol?: string;
  currentPrice?: number;
}

export function PriceChart({ data, symbol = "BTC", currentPrice }: PriceChartProps) {
  const [chartData, setChartData] = useState<Array<{ time: string; price: number }>>([]);
  const dataRef = useRef<Array<{ time: string; price: number }>>([]);
  const maxDataPoints = 50; // Keep last 50 data points

  // Update chart data when currentPrice changes
  useEffect(() => {
    if (currentPrice && currentPrice > 0) {
      const now = new Date();
      const timeStr = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
      
      // Add new price point only if price has changed (avoid duplicates)
      const lastPrice = dataRef.current.length > 0 ? dataRef.current[dataRef.current.length - 1].price : null;
      if (lastPrice !== currentPrice) {
        const newDataPoint = { time: timeStr, price: currentPrice };
        dataRef.current = [...dataRef.current, newDataPoint];
        
        // Keep only last maxDataPoints
        if (dataRef.current.length > maxDataPoints) {
          dataRef.current = dataRef.current.slice(-maxDataPoints);
        }
        
        setChartData([...dataRef.current]);
      }
    } else if (data && data.length > 0 && chartData.length === 0) {
      // Use provided data if available and no real-time data yet
      setChartData(data);
      dataRef.current = data;
    }
  }, [currentPrice, data]);

  // Use provided data if no real-time updates
  const displayData = chartData.length > 0 ? chartData : (data || []);

  // Show loading state if no data
  if (displayData.length === 0) {
    return (
      <div className="w-full h-96 bg-white rounded-lg p-4 border border-gray-200 flex items-center justify-center" style={{ minHeight: '384px' }}>
        <div className="text-center text-gray-500">
          <p className="text-lg font-medium">Loading price data...</p>
          <p className="text-sm mt-2">Waiting for real-time {symbol} prices</p>
        </div>
      </div>
    );
  }

  const isPositive = displayData.length > 1 ? displayData[displayData.length - 1].price >= displayData[0].price : false;
  const gradientColor = isPositive ? "#10b981" : "#ef4444";
  
  // Calculate min and max for Y-axis domain
  const prices = displayData.map(d => d.price);
  const minPrice = Math.min(...prices);
  const maxPrice = Math.max(...prices);
  const priceRange = maxPrice - minPrice;
  const padding = priceRange > 0 ? priceRange * 0.1 : Math.max(minPrice * 0.01, 100); // 10% padding or 1% of price, min 100

  return (
    <div className="w-full h-96 bg-white rounded-lg p-4 border border-gray-200" style={{ minHeight: '384px' }}>
      <ResponsiveContainer width="100%" height="100%" minHeight={384}>
        <AreaChart data={displayData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={gradientColor} stopOpacity={0.3}/>
              <stop offset="95%" stopColor={gradientColor} stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis 
            dataKey="time" 
            stroke="#6b7280"
            className="text-xs"
            tick={{ fill: '#6b7280' }}
          />
          <YAxis 
            stroke="#6b7280"
            className="text-xs"
            tick={{ fill: '#6b7280' }}
            domain={[minPrice - padding, maxPrice + padding]}
            tickFormatter={(value) => `$${value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
          />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: 'rgba(255, 255, 255, 0.95)', 
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              padding: '8px 12px'
            }}
            formatter={(value: any) => [`$${Number(value).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`, 'Price']}
          />
          <Area 
            type="monotone" 
            dataKey="price" 
            stroke={gradientColor} 
            strokeWidth={2}
            fillOpacity={1}
            fill="url(#colorPrice)" 
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
