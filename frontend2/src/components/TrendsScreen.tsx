import React, { useState } from 'react';
import { ComposedChart, Line, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Cloud, Calendar, TrendingUp, Droplets } from 'lucide-react';

const mockData = [
  { week: 'Oct 7', earnings: 880, rainfall: 0.2, events: 0, demand: 45 },
  { week: 'Oct 14', earnings: 935, rainfall: 0, events: 1, demand: 52 },
  { week: 'Oct 21', earnings: 870, rainfall: 0.1, events: 0, demand: 48 },
  { week: 'Oct 28', earnings: 905, rainfall: 1.8, events: 0, demand: 50 },
  { week: 'Nov 4', earnings: 890, rainfall: 0.5, events: 0, demand: 49 },
  { week: 'Nov 11', earnings: 910, rainfall: 2.1, events: 1, demand: 56 },
];

export function TrendsScreen() {
  const [layers, setLayers] = useState({
    earnings: true,
    rainfall: true,
    events: true,
    demand: true
  });

  const toggleLayer = (layer: keyof typeof layers) => {
    setLayers(prev => ({ ...prev, [layer]: !prev[layer] }));
  };

  return (
    <div className="pb-20 px-6 pt-8" style={{ backgroundColor: '#FAF8F5' }}>
      {/* Header */}
      <div className="mb-6">
        <h1 className="mb-1" style={{ color: '#222' }}>Trends & Context</h1>
        <p className="text-gray-600">How external factors affect your earnings</p>
      </div>

      {/* Layer Toggles */}
      <div className="bg-white rounded-2xl shadow-md p-4 mb-6">
        <p className="text-sm text-gray-500 mb-3">Active Layers</p>
        <div className="grid grid-cols-2 gap-2">
          <button
            onClick={() => toggleLayer('earnings')}
            className="px-3 py-2 rounded-xl border-2 flex items-center gap-2 text-sm transition-all"
            style={{
              borderColor: layers.earnings ? '#1E4E40' : '#E5E5E5',
              backgroundColor: layers.earnings ? '#F0F5F3' : 'transparent',
              color: layers.earnings ? '#1E4E40' : '#666'
            }}
          >
            <TrendingUp size={16} />
            Earnings
          </button>
          <button
            onClick={() => toggleLayer('rainfall')}
            className="px-3 py-2 rounded-xl border-2 flex items-center gap-2 text-sm transition-all"
            style={{
              borderColor: layers.rainfall ? '#6CA58E' : '#E5E5E5',
              backgroundColor: layers.rainfall ? '#E8F4F0' : 'transparent',
              color: layers.rainfall ? '#6CA58E' : '#666'
            }}
          >
            <Cloud size={16} />
            Weather
          </button>
          <button
            onClick={() => toggleLayer('events')}
            className="px-3 py-2 rounded-xl border-2 flex items-center gap-2 text-sm transition-all"
            style={{
              borderColor: layers.events ? '#E09447' : '#E5E5E5',
              backgroundColor: layers.events ? '#FFF5EB' : 'transparent',
              color: layers.events ? '#E09447' : '#666'
            }}
          >
            <Calendar size={16} />
            Events
          </button>
          <button
            onClick={() => toggleLayer('demand')}
            className="px-3 py-2 rounded-xl border-2 flex items-center gap-2 text-sm transition-all"
            style={{
              borderColor: layers.demand ? '#D77B54' : '#E5E5E5',
              backgroundColor: layers.demand ? '#FFF0ED' : 'transparent',
              color: layers.demand ? '#D77B54' : '#666'
            }}
          >
            <TrendingUp size={16} />
            Demand
          </button>
        </div>
      </div>

      {/* Chart */}
      <div className="bg-white rounded-3xl shadow-lg p-6 mb-6">
        <div className="h-80 -mx-2">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={mockData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E5E5" vertical={false} />
              <XAxis
                dataKey="week"
                stroke="#999"
                fontSize={12}
                tickLine={false}
              />
              <YAxis
                yAxisId="left"
                stroke="#999"
                fontSize={12}
                tickLine={false}
                tickFormatter={(value) => `$${value}`}
              />
              <YAxis
                yAxisId="right"
                orientation="right"
                stroke="#999"
                fontSize={12}
                tickLine={false}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#FFF',
                  border: 'none',
                  borderRadius: '12px',
                  boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                }}
              />
              <Legend
                wrapperStyle={{ fontSize: '12px', paddingTop: '20px' }}
              />
              {layers.rainfall && (
                <Bar
                  yAxisId="right"
                  dataKey="rainfall"
                  fill="#6CA58E"
                  opacity={0.3}
                  name="Rainfall (in)"
                  radius={[8, 8, 0, 0]}
                />
              )}
              {layers.earnings && (
                <Line
                  yAxisId="left"
                  type="monotone"
                  dataKey="earnings"
                  stroke="#1E4E40"
                  strokeWidth={3}
                  dot={{ fill: '#1E4E40', r: 4 }}
                  name="Earnings ($)"
                />
              )}
              {layers.demand && (
                <Line
                  yAxisId="right"
                  type="monotone"
                  dataKey="demand"
                  stroke="#D77B54"
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  dot={false}
                  name="Demand Index"
                />
              )}
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Correlation Insights */}
      <div className="space-y-3">
        <div className="bg-white rounded-2xl shadow-md p-5">
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 rounded-full flex items-center justify-center" style={{ backgroundColor: '#E8F4F0' }}>
              <Droplets size={20} style={{ color: '#6CA58E' }} />
            </div>
            <div className="flex-1">
              <div className="flex items-center justify-between mb-1">
                <p style={{ color: '#222' }}>Weather Impact</p>
                <span className="text-sm" style={{ color: '#6CA58E' }}>+12% correlation</span>
              </div>
              <p className="text-sm text-gray-600">
                Rainy weeks consistently show higher earnings. Rain expected Thu-Fri this week.
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-md p-5">
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 rounded-full flex items-center justify-center" style={{ backgroundColor: '#FFF5EB' }}>
              <Calendar size={20} style={{ color: '#E09447' }} />
            </div>
            <div className="flex-1">
              <div className="flex items-center justify-between mb-1">
                <p style={{ color: '#222' }}>Upcoming Events</p>
                <span className="text-sm" style={{ color: '#E09447' }}>This weekend</span>
              </div>
              <p className="text-sm text-gray-600">
                Stadium concert Saturday night. Downtown surge zones active 8-11 PM.
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-md p-5">
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 rounded-full flex items-center justify-center" style={{ backgroundColor: '#FFF0ED' }}>
              <TrendingUp size={20} style={{ color: '#D77B54' }} />
            </div>
            <div className="flex-1">
              <div className="flex items-center justify-between mb-1">
                <p style={{ color: '#222' }}>Demand Trends</p>
                <span className="text-sm" style={{ color: '#D77B54' }}>↑ Rising</span>
              </div>
              <p className="text-sm text-gray-600">
                Search demand up 8% this week. Holiday travel season beginning.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
