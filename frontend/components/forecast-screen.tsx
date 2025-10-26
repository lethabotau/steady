import { Card } from "./ui/card";
import { ArrowLeft, Calendar, Cloud, TrendingUp } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, ReferenceLine, Area, AreaChart } from "recharts";

interface ForecastScreenProps {
  onBack: () => void;
}

export function ForecastScreen({ onBack }: ForecastScreenProps) {
  const weeklyData = [
    { week: 'Aug 14', earnings: 840, predicted: false, holiday: false, weather: 'sunny' },
    { week: 'Aug 21', earnings: 780, predicted: false, holiday: false, weather: 'sunny' },
    { week: 'Aug 28', earnings: 920, predicted: false, holiday: false, weather: 'rainy' },
    { week: 'Sep 4', earnings: 810, predicted: false, holiday: false, weather: 'sunny' },
    { week: 'Sep 11', earnings: 950, predicted: false, holiday: false, weather: 'rainy' },
    { week: 'Sep 18', earnings: 770, predicted: false, holiday: false, weather: 'sunny' },
    { week: 'Sep 25', earnings: 890, predicted: false, holiday: false, weather: 'mixed' },
    { week: 'Oct 2', earnings: 940, predicted: false, holiday: true, weather: 'sunny' },
    { week: 'Oct 9', earnings: 820, predicted: false, holiday: false, weather: 'sunny' },
    { week: 'Oct 16', earnings: 860, predicted: false, holiday: false, weather: 'sunny' },
    { week: 'Oct 23', earnings: 880, predicted: false, holiday: false, weather: 'mixed' },
    { week: 'Oct 30', earnings: 930, predicted: true, holiday: false, weather: 'mixed' },
    { week: 'Nov 6', earnings: 890, predicted: true, holiday: false, weather: 'sunny' },
  ];

  const currentWeekIndex = 11; // Oct 30 is the current week we're forecasting

  return (
    <div className="pb-24 bg-background min-h-screen">
      {/* Header */}
      <div className="px-6 pt-12 pb-6">
        <div className="flex items-center gap-3 mb-4">
          <button 
            onClick={onBack}
            className="w-10 h-10 rounded-lg bg-muted flex items-center justify-center"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div className="space-y-1">
            <h1 className="text-xl font-semibold text-foreground">Forecast Detail</h1>
            <p className="text-sm text-muted-foreground">12-week earnings pattern</p>
          </div>
        </div>
      </div>

      <div className="px-6 space-y-6">
        {/* Chart Card */}
        <Card className="p-6 bg-card border-border">
          <div className="space-y-4">
            <div className="space-y-2">
              <h3 className="text-lg font-medium">Weekly Earnings Trend</h3>
              <p className="text-sm text-muted-foreground">
                Historical data with weather and event markers
              </p>
            </div>
            
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={weeklyData}>
                  <defs>
                    <linearGradient id="earningsGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#6B8E6E" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#6B8E6E" stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="forecastGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#8DAA91" stopOpacity={0.2}/>
                      <stop offset="95%" stopColor="#8DAA91" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <XAxis 
                    dataKey="week" 
                    axisLine={false}
                    tickLine={false}
                    tick={{ fontSize: 12, fill: '#6B7280' }}
                  />
                  <YAxis 
                    axisLine={false}
                    tickLine={false}
                    tick={{ fontSize: 12, fill: '#6B7280' }}
                    domain={['dataMin - 50', 'dataMax + 50']}
                  />
                  <ReferenceLine x="Oct 30" stroke="#E1E6E2" strokeDasharray="2 2" />
                  <Area
                    type="monotone"
                    dataKey="earnings"
                    stroke="#6B8E6E"
                    strokeWidth={2}
                    fill="url(#earningsGradient)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            {/* Legend and markers */}
            <div className="flex flex-wrap gap-4 text-xs">
              <div className="flex items-center gap-2">
                <Cloud className="w-4 h-4 text-blue-500" />
                <span className="text-muted-foreground">Rainy periods</span>
              </div>
              <div className="flex items-center gap-2">
                <Calendar className="w-4 h-4 text-secondary" />
                <span className="text-muted-foreground">Public holidays</span>
              </div>
              <div className="flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-primary" />
                <span className="text-muted-foreground">Forecast range</span>
              </div>
            </div>
          </div>
        </Card>

        {/* Volatility Card */}
        <Card className="p-6 bg-card border-border">
          <div className="space-y-4">
            <h3 className="text-lg font-medium">Income Stability</h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <p className="text-2xl font-semibold text-foreground">± 9%</p>
                <p className="text-sm text-muted-foreground">Average weekly volatility</p>
              </div>
              <div className="space-y-1">
                <p className="text-2xl font-semibold text-primary">$865</p>
                <p className="text-sm text-muted-foreground">12-week average</p>
              </div>
            </div>
            
            <div className="p-4 bg-muted rounded-lg">
              <h4 className="font-medium mb-2">Why this matters</h4>
              <p className="text-sm text-muted-foreground leading-relaxed">
                Your earnings are more stable than 68% of Sydney drivers. Weather patterns and public holidays are your biggest income drivers, with weekend rain consistently boosting demand.
              </p>
            </div>
          </div>
        </Card>

        {/* Next Week Forecast */}
        <Card className="p-6 bg-card border-border">
          <div className="space-y-4">
            <h3 className="text-lg font-medium">Next Week Outlook</h3>
            
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Predicted earnings</span>
                <span className="font-semibold text-foreground">$930 ± $60</span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Confidence level</span>
                <span className="text-sm text-primary">High (85%)</span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Key factors</span>
                <span className="text-sm text-muted-foreground">Mixed weather, normal demand</span>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
