import React, { useState } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Calendar, Filter } from 'lucide-react';
interface ForecastDetailScreenProps {
  weeklyGoal: number;
}

const mockData = [
  { week: 'Aug 19', earnings: 820, lower: 760, upper: 880 },
  { week: 'Aug 26', earnings: 890, lower: 830, upper: 950 },
  { week: 'Sep 2', earnings: 740, lower: 680, upper: 800 },
  { week: 'Sep 9', earnings: 910, lower: 850, upper: 970 },
  { week: 'Sep 16', earnings: 865, lower: 805, upper: 925 },
  { week: 'Sep 23', earnings: 920, lower: 860, upper: 980 },
  { week: 'Sep 30', earnings: 795, lower: 735, upper: 855 },
  { week: 'Oct 7', earnings: 880, lower: 820, upper: 940 },
  { week: 'Oct 14', earnings: 935, lower: 875, upper: 995 },
  { week: 'Oct 21', earnings: 870, lower: 810, upper: 930 },
  { week: 'Oct 28', earnings: 905, lower: 845, upper: 965 },
  { week: 'Nov 4', earnings: 890, lower: 830, upper: 950 },
  { week: 'Nov 11', earnings: 910, lower: 845, upper: 975, forecast: true },
];

export function ForecastDetailScreen({ weeklyGoal }: ForecastDetailScreenProps) {
  const [activeFilter, setActiveFilter] = useState<string | null>(null);

  const baseForecast = Math.round(weeklyGoal * 0.95);
  const lowerBound = Math.round(weeklyGoal * 0.85);
  const upperBound = Math.round(weeklyGoal * 1.10); 

  const filters = ['Weekday', 'Zone', 'Shift Type'];

  return (
    <div className="pb-20 px-6 pt-8" style={{ backgroundColor: '#FAF8F5' }}>
      {/* Header */}
      <div className="mb-6">
        <h1 className="mb-1" style={{ color: '#222' }}>Earnings Forecast</h1>
        <p className="text-gray-600">12-week trend with prediction</p>
      </div>

      {/* Filter Chips */}
      <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
        {filters.map((filter) => (
          <button
            key={filter}
            onClick={() => setActiveFilter(activeFilter === filter ? null : filter)}
            className="px-4 py-2 rounded-xl border-2 whitespace-nowrap flex items-center gap-2 transition-all"
            style={{
              borderColor: activeFilter === filter ? '#1E4E40' : '#E5E5E5',
              backgroundColor: activeFilter === filter ? '#F0F5F3' : '#FFF',
              color: activeFilter === filter ? '#1E4E40' : '#666'
            }}
          >
            <Filter size={16} />
            {filter}
          </button>
        ))}
      </div>

      {/* Chart Card */}
      <div className="bg-white rounded-3xl shadow-lg p-6 mb-6">
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-500">Next Week Forecast</span>
            <div className="flex items-center gap-2">
              <Calendar size={16} style={{ color: '#6CA58E' }} />
              <span className="text-sm" style={{ color: '#6CA58E' }}>Nov 11 - 17</span>
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl" style={{ color: '#1E4E40' }}>${baseForecast}</span>
            <span className="text-gray-400">± ${upperBound - baseForecast}</span>
          </div>
          <p className="text-sm text-gray-500 mt-1">
            Likely range: ${lowerBound} – ${upperBound}
          </p>
        </div>

        <div className="h-64 -mx-2">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={mockData}>
              <defs>
                <linearGradient id="colorEarnings" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#1E4E40" stopOpacity={0.2}/>
                  <stop offset="95%" stopColor="#1E4E40" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorForecast" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6CA58E" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#6CA58E" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E5E5" vertical={false} />
              <XAxis
                dataKey="week"
                stroke="#999"
                fontSize={12}
                tickLine={false}
              />
              <YAxis
                stroke="#999"
                fontSize={12}
                tickLine={false}
                tickFormatter={(value) => `$${value}`}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#FFF',
                  border: 'none',
                  borderRadius: '12px',
                  boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                }}
                formatter={(value: number) => [`$${value}`, 'Earnings']}
              />
              <Area
                type="monotone"
                dataKey="lower"
                stroke="none"
                fill="none"
              />
              <Area
                type="monotone"
                dataKey="upper"
                stroke="#6CA58E"
                strokeWidth={0}
                fill="url(#colorForecast)"
                fillOpacity={0.3}
              />
              <Area
                type="monotone"
                dataKey="earnings"
                stroke="#1E4E40"
                strokeWidth={3}
                fill="url(#colorEarnings)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="flex items-center justify-center gap-6 mt-4 pt-4 border-t border-gray-100">
          <div className="flex items-center gap-2">
            <div className="w-4 h-0.5 rounded" style={{ backgroundColor: '#1E4E40' }} />
            <span className="text-sm text-gray-600">Actual</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-0.5 border-b-2 border-dashed" style={{ borderColor: '#6CA58E' }} />
            <span className="text-sm text-gray-600">Forecast</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-3 rounded" style={{ backgroundColor: '#6CA58E', opacity: 0.2 }} />
            <span className="text-sm text-gray-600">Range</span>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white rounded-2xl shadow-md p-4">
          <p className="text-sm text-gray-500 mb-1">12-Week Average</p>
          <p className="text-2xl" style={{ color: '#1E4E40' }}>$872</p>
        </div>
        <div className="bg-white rounded-2xl shadow-md p-4">
          <p className="text-sm text-gray-500 mb-1">Avg. Volatility</p>
          <p className="text-2xl" style={{ color: '#E09447' }}>± 9%</p>
        </div>
        <div className="bg-white rounded-2xl shadow-md p-4">
          <p className="text-sm text-gray-500 mb-1">Best Week</p>
          <p className="text-2xl" style={{ color: '#6CA58E' }}>$935</p>
        </div>
        <div className="bg-white rounded-2xl shadow-md p-4">
          <p className="text-sm text-gray-500 mb-1">Trend</p>
          <p className="text-2xl" style={{ color: '#6CA58E' }}>↑ 4%</p>
        </div>
      </div>
    </div>
  );
}
