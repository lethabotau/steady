import React from 'react';
import { TrendingUp, AlertCircle, Target, Zap, Cloud, Clock } from 'lucide-react';

interface DashboardScreenProps {
  weeklyGoal: number;
}

export function DashboardScreen({ weeklyGoal }: DashboardScreenProps) {
  const forecastAmount = 910;
  const forecastVariance = 65;
  const currentProgress = 745;
  const steadinessScore = 78; // 0-100

  return (
    <div className="pb-20 px-6 pt-8" style={{ backgroundColor: '#FAF8F5' }}>
      {/* Header */}
      <div className="mb-8">
        <h1 className="mb-1" style={{ color: '#222' }}>Weekly Outlook</h1>
        <p className="text-gray-600">Nov 11 - Nov 17, 2025</p>
      </div>

      {/* Forecast Card */}
      <div className="bg-white rounded-3xl shadow-lg p-6 mb-6" style={{ borderTop: '4px solid #1E4E40' }}>
        <div className="flex items-start justify-between mb-4">
          <div>
            <p className="text-sm text-gray-500 mb-1">Predicted Earnings</p>
            <div className="flex items-baseline gap-2">
              <span className="text-5xl" style={{ color: '#1E4E40' }}>${forecastAmount}</span>
              <span className="text-gray-400">± ${forecastVariance}</span>
            </div>
          </div>
          <div className="w-10 h-10 rounded-full flex items-center justify-center" style={{ backgroundColor: '#F0F5F3' }}>
            <TrendingUp size={20} style={{ color: '#1E4E40' }} />
          </div>
        </div>
        <div className="flex items-center gap-2 text-sm" style={{ color: '#6CA58E' }}>
          <TrendingUp size={16} />
          <span>12% above your 4-week average</span>
        </div>
      </div>

      {/* Steadiness Index */}
      <div className="bg-white rounded-3xl shadow-lg p-6 mb-6">
        <p className="text-sm text-gray-500 mb-4">Steadiness Index</p>
        <div className="flex items-center gap-6">
          <div className="relative w-28 h-28">
            <svg className="transform -rotate-90" width="112" height="112">
              <circle
                cx="56"
                cy="56"
                r="48"
                fill="none"
                stroke="#E5E5E5"
                strokeWidth="12"
              />
              <circle
                cx="56"
                cy="56"
                r="48"
                fill="none"
                stroke="#6CA58E"
                strokeWidth="12"
                strokeDasharray={`${(steadinessScore / 100) * 301.6} 301.6`}
                strokeLinecap="round"
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-3xl" style={{ color: '#1E4E40' }}>{steadinessScore}</span>
              <span className="text-xs text-gray-400">/ 100</span>
            </div>
          </div>
          <div className="flex-1">
            <p className="mb-2" style={{ color: '#1E4E40' }}>Stable</p>
            <p className="text-sm text-gray-600">Your earnings have been consistent over the past 4 weeks</p>
          </div>
        </div>
        <div className="mt-4 pt-4 border-t border-gray-100">
          <div className="flex justify-between items-center text-sm">
            <span className="text-gray-500">Average weekly volatility</span>
            <span style={{ color: '#1E4E40' }}>± 9%</span>
          </div>
        </div>
      </div>

      {/* Quick Insights */}
      <div className="mb-6">
        <p className="text-sm mb-4" style={{ color: '#222' }}>Quick Insights</p>
        <div className="space-y-3">
          <div className="bg-white rounded-2xl shadow-md p-4 flex items-start gap-3">
            <div className="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0" style={{ backgroundColor: '#FFF5EB' }}>
              <Clock size={20} style={{ color: '#E09447' }} />
            </div>
            <div>
              <p className="mb-1" style={{ color: '#222' }}>Friday evenings earn +18% more</p>
              <p className="text-sm text-gray-600">Peak hours: 6 PM - 9 PM</p>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-md p-4 flex items-start gap-3">
            <div className="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0" style={{ backgroundColor: '#E8F4F0' }}>
              <Cloud size={20} style={{ color: '#6CA58E' }} />
            </div>
            <div>
              <p className="mb-1" style={{ color: '#222' }}>Rainy weeks boost earnings by 12%</p>
              <p className="text-sm text-gray-600">Rain expected Thu-Fri this week</p>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-md p-4 flex items-start gap-3">
            <div className="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0" style={{ backgroundColor: '#FFF5EB' }}>
              <Zap size={20} style={{ color: '#E09447' }} />
            </div>
            <div>
              <p className="mb-1" style={{ color: '#222' }}>Airport runs average $34/trip</p>
              <p className="text-sm text-gray-600">23% higher than downtown</p>
            </div>
          </div>
        </div>
      </div>

      {/* Goal Progress */}
      <div className="bg-white rounded-3xl shadow-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Target size={20} style={{ color: '#1E4E40' }} />
            <span style={{ color: '#222' }}>Weekly Goal</span>
          </div>
          <span className="text-sm" style={{ color: '#6CA58E' }}>{Math.round((currentProgress / weeklyGoal) * 100)}%</span>
        </div>
        <div className="mb-3">
          <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
            <div
              className="h-full rounded-full transition-all"
              style={{
                width: `${Math.min((currentProgress / weeklyGoal) * 100, 100)}%`,
                backgroundColor: '#6CA58E'
              }}
            />
          </div>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-gray-500">${currentProgress} earned</span>
          <span className="text-gray-500">${weeklyGoal} goal</span>
        </div>
        <div className="mt-4 pt-4 border-t border-gray-100">
          <div className="flex items-center gap-2 text-sm" style={{ color: '#E09447' }}>
            <AlertCircle size={16} />
            <span>Drive ${weeklyGoal - currentProgress} more to hit your goal</span>
          </div>
        </div>
      </div>
    </div>
  );
}
