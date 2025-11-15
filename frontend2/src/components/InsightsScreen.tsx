import React from 'react';
import { Clock, TrendingUp, Cloud, Calendar, MapPin, Zap, Users, DollarSign } from 'lucide-react';

interface InsightsScreenProps {
  weeklyGoal: number;
}

export function InsightsScreen({ weeklyGoal }: InsightsScreenProps) {
  const extraFromPeak = Math.round(weeklyGoal * 0.18);
  const timingInsights = [
    {
      icon: Clock,
      title: 'Peak earning hours',
      stat: '6 PM - 9 PM',
      description: `You earn ~18% more during evening rush (~$${extraFromPeak} vs your weekly target).`,
      color: '#E09447'
    },
    {
      icon: Calendar,
      title: 'Best days to drive',
      stat: 'Friday & Saturday',
      description: 'Weekend earnings are 24% higher',
      color: '#6CA58E'
    },
    {
      icon: TrendingUp,
      title: 'Morning opportunity',
      stat: '7 AM - 9 AM',
      description: 'Airport runs increase by 35%',
      color: '#1E4E40'
    }
  ];

  const consistencyInsights = [
    {
      icon: Zap,
      title: 'Optimal work hours',
      stat: '20-25 hours/week',
      description: 'Your most stable income periods',
      color: '#E09447'
    },
    {
      icon: TrendingUp,
      title: 'Consistency score',
      stat: '78/100',
      description: 'You maintain steady earnings',
      color: '#6CA58E'
    },
    {
      icon: DollarSign,
      title: 'Hourly average',
      stat: '$42/hour',
      description: '12% above city average',
      color: '#1E4E40'
    }
  ];

  const externalInsights = [
    {
      icon: Cloud,
      title: 'Weather impact',
      stat: '+12% earnings',
      description: 'Rainy days boost demand',
      color: '#6CA58E'
    },
    {
      icon: Users,
      title: 'Event alerts',
      stat: 'Concert tonight',
      description: 'Downtown surge expected 9-11 PM',
      color: '#E09447'
    },
    {
      icon: MapPin,
      title: 'Zone performance',
      stat: 'Airport best',
      description: '$34 avg trip vs $28 downtown',
      color: '#1E4E40'
    }
  ];

  const renderInsightCard = (insight: any, index: number) => {
    const Icon = insight.icon;
    return (
      <div key={index} className="bg-white rounded-2xl shadow-md p-5">
        <div className="flex items-start gap-3 mb-3">
          <div
            className="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0"
            style={{ backgroundColor: `${insight.color}15` }}
          >
            <Icon size={20} style={{ color: insight.color }} />
          </div>
          <div className="flex-1">
            <p className="text-sm text-gray-500 mb-1">{insight.title}</p>
            <p className="mb-1" style={{ color: '#222' }}>{insight.stat}</p>
          </div>
        </div>
        <p className="text-sm text-gray-600">{insight.description}</p>
      </div>
    );
  };

  return (
    <div className="pb-20 px-6 pt-8" style={{ backgroundColor: '#FAF8F5' }}>
      {/* Header */}
      <div className="mb-8">
        <h1 className="mb-1" style={{ color: '#222' }}>Insights</h1>
        <p className="text-gray-600">Personalized tips to boost your earnings</p>
      </div>

      {/* Timing Insights */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-4">
          <Clock size={20} style={{ color: '#E09447' }} />
          <h2 className="text-sm" style={{ color: '#222' }}>Timing</h2>
        </div>
        <div className="space-y-3">
          {timingInsights.map(renderInsightCard)}
        </div>
      </div>

      {/* Consistency Insights */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-4">
          <Zap size={20} style={{ color: '#6CA58E' }} />
          <h2 className="text-sm" style={{ color: '#222' }}>Consistency</h2>
        </div>
        <div className="space-y-3">
          {consistencyInsights.map(renderInsightCard)}
        </div>
      </div>

      {/* External Factors */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-4">
          <Cloud size={20} style={{ color: '#1E4E40' }} />
          <h2 className="text-sm" style={{ color: '#222' }}>External Factors</h2>
        </div>
        <div className="space-y-3">
          {externalInsights.map(renderInsightCard)}
        </div>
      </div>

      {/* Action Card */}
      <div className="bg-gradient-to-br from-white to-gray-50 rounded-3xl shadow-lg p-6 border-2" style={{ borderColor: '#E09447' }}>
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 rounded-full flex items-center justify-center" style={{ backgroundColor: '#E09447' }}>
            <Zap size={24} style={{ color: '#FFF' }} />
          </div>
          <div className="flex-1">
            <p className="mb-2" style={{ color: '#222' }}>Try this week</p>
            <p className="text-sm text-gray-600 mb-4">
              Based on your patterns, driving Friday 6-9 PM could earn you an extra $85 this week.
            </p>
            <button
              className="px-5 py-2 rounded-xl text-sm text-white"
              style={{ backgroundColor: '#E09447' }}
            >
              Set Reminder
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
