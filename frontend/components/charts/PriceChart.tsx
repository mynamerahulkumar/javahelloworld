"use client";

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from "recharts";

interface PriceChartProps {
  data?: Array<{ time: string; price: number }>;
  symbol?: string;
}

export function PriceChart({ data, symbol = "BTC" }: PriceChartProps) {
  // Sample data if none provided
  const chartData = data || [
    { time: "09:00", price: 105000 },
    { time: "10:00", price: 106000 },
    { time: "11:00", price: 107000 },
    { time: "12:00", price: 106500 },
    { time: "13:00", price: 107500 },
    { time: "14:00", price: 108000 },
    { time: "15:00", price: 107800 },
    { time: "16:00", price: 108200 },
    { time: "17:00", price: 108500 },
    { time: "18:00", price: 108300 },
  ];

  const isPositive = chartData.length > 1 && chartData[chartData.length - 1].price >= chartData[0].price;
  const gradientColor = isPositive ? "#10b981" : "#ef4444";

  return (
    <div className="w-full h-96 bg-white rounded-lg p-4 border border-gray-200">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
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
            domain={['dataMin - 500', 'dataMax + 500']}
            tickFormatter={(value) => `$${value.toLocaleString()}`}
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
