import { Card } from "./ui/card";
import { ArrowLeft, Cloud, Calendar, TrendingUp } from "lucide-react";
import { ComposedChart, Line, Bar, XAxis, YAxis, ResponsiveContainer, Legend } from "recharts";

interface TrendsScreenProps {
  onBack: () => void;
}

export function TrendsScreen({ onBack }: TrendsScreenProps) {
  const trendsData = [
    { week: 'Aug 14', earnings: 840, rainfall: 2, googleTrends: 65, events: 0 },
    { week: 'Aug 21', earnings: 780, rainfall: 0, googleTrends: 58, events: 0 },
    { week: 'Aug 28', earnings: 920, rainfall: 25, googleTrends: 72, events: 0 },
    { week: 'Sep 4', earnings: 810, rainfall: 5, googleTrends: 61, events: 0 },
    { week: 'Sep 11', earnings: 950, rainfall: 30, googleTrends: 78, events: 0 },
    { week: 'Sep 18', earnings: 770, rainfall: 0, googleTrends: 55, events: 0 },
    { week: 'Sep 25', earnings: 890, rainfall: 12, googleTrends: 68, events: 0 },
    { week: 'Oct 2', earnings: 940, rainfall: 8, googleTrends: 82, events: 1 },
    { week: 'Oct 9', earnings: 820, rainfall: 3, googleTrends: 63, events: 0 },
    { week: 'Oct 16', earnings: 860, rainfall: 0, googleTrends: 59, events: 0 },
    { week: 'Oct 23', earnings: 880, rainfall: 15, googleTrends: 71, events: 0 },
    { week: 'Oct 30', earnings: 930, rainfall: 18, googleTrends: 75, events: 0 },
  ];

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
            <h1 className="text-xl font-semibold text-foreground">Trends & Context</h1>
            <p className="text-sm text-muted-foreground">External factors affecting your earnings</p>
          </div>
        </div>
      </div>

      <div className="px-6 space-y-6">
        {/* Combined Trends Chart */}
        <Card className="p-6 bg-card border-border">
          <div className="space-y-4">
            <div className="space-y-2">
              <h3 className="text-lg font-medium">Earnings vs External Factors</h3>
              <p className="text-sm text-muted-foreground">
                How weather, events, and demand trends impact your income
              </p>
            </div>
            
            <div className="h-80 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={trendsData}>
                  <XAxis 
                    dataKey="week" 
                    axisLine={false}
                    tickLine={false}
                    tick={{ fontSize: 12, fill: '#6B7280' }}
                  />
                  <YAxis 
                    yAxisId="earnings"
                    orientation="left"
                    axisLine={false}
                    tickLine={false}
                    tick={{ fontSize: 12, fill: '#6B7280' }}
                    domain={['dataMin - 50', 'dataMax + 50']}
                  />
                  <YAxis 
                    yAxisId="factors"
                    orientation="right"
                    axisLine={false}
                    tickLine={false}
                    tick={{ fontSize: 12, fill: '#6B7280' }}
                    domain={[0, 100]}
                  />
                  
                  {/* Rainfall bars */}
                  <Bar 
                    yAxisId="factors"
                    dataKey="rainfall" 
                    fill="#8DA4DB" 
                    opacity={0.6}
                    radius={[2, 2, 0, 0]}
                  />
                  
                  {/* Google Trends line */}
                  <Line 
                    yAxisId="factors"
                    type="monotone" 
                    dataKey="googleTrends" 
                    stroke="#E7A95F" 
                    strokeWidth={2}
                    dot={{ fill: '#E7A95F', strokeWidth: 0, r: 3 }}
                    activeDot={{ r: 4, fill: '#E7A95F' }}
                  />
                  
                  {/* Earnings line */}
                  <Line 
                    yAxisId="earnings"
                    type="monotone" 
                    dataKey="earnings" 
                    stroke="#6B8E6E" 
                    strokeWidth={3}
                    dot={{ fill: '#6B8E6E', strokeWidth: 0, r: 4 }}
                    activeDot={{ r: 5, fill: '#6B8E6E' }}
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </div>

            {/* Legend */}
            <div className="grid grid-cols-1 gap-3 text-sm">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-primary rounded-full" />
                <span className="text-muted-foreground">Your weekly earnings ($)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-blue-400 rounded" />
                <span className="text-muted-foreground">Rainfall (mm)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-secondary rounded-full" />
                <span className="text-muted-foreground">Uber demand trend (Google search volume)</span>
              </div>
            </div>
          </div>
        </Card>

        {/* Correlation Insights */}
        <div className="grid grid-cols-1 gap-4">
          <Card className="p-4 bg-card border-border">
            <div className="flex gap-3">
              <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center">
                <Cloud className="w-5 h-5 text-blue-500" />
              </div>
              <div className="flex-1 space-y-1">
                <h4 className="font-medium text-foreground">Weather Impact</h4>
                <p className="text-sm text-muted-foreground">
                  +18% earnings during rainy weeks. Strong correlation with weekend rainfall.
                </p>
                <div className="flex items-center gap-2">
                  <div className="h-1.5 w-12 bg-blue-500 rounded-full" />
                  <span className="text-xs text-muted-foreground">Strong</span>
                </div>
              </div>
            </div>
          </Card>

          <Card className="p-4 bg-card border-border">
            <div className="flex gap-3">
              <div className="w-10 h-10 bg-orange-50 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-secondary" />
              </div>
              <div className="flex-1 space-y-1">
                <h4 className="font-medium text-foreground">Demand Patterns</h4>
                <p className="text-sm text-muted-foreground">
                  Google search trends for "Uber Eats Sydney" predict your weekly earnings.
                </p>
                <div className="flex items-center gap-2">
                  <div className="h-1.5 w-8 bg-secondary rounded-full" />
                  <span className="text-xs text-muted-foreground">Moderate</span>
                </div>
              </div>
            </div>
          </Card>

          <Card className="p-4 bg-card border-border">
            <div className="flex gap-3">
              <div className="w-10 h-10 bg-green-50 rounded-lg flex items-center justify-center">
                <Calendar className="w-5 h-5 text-primary" />
              </div>
              <div className="flex-1 space-y-1">
                <h4 className="font-medium text-foreground">Special Events</h4>
                <p className="text-sm text-muted-foreground">
                  Public holidays and major Sydney events boost earnings by 8-12%.
                </p>
                <div className="flex items-center gap-2">
                  <div className="h-1.5 w-8 bg-primary rounded-full" />
                  <span className="text-xs text-muted-foreground">Moderate</span>
                </div>
              </div>
            </div>
          </Card>
        </div>

        {/* Key Insights Summary */}
        <Card className="p-6 bg-gradient-to-br from-primary/5 to-secondary/5 border-border">
          <div className="space-y-4">
            <h3 className="text-lg font-medium">Key Takeaways</h3>
            <div className="space-y-3">
              <div className="flex gap-3">
                <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0" />
                <p className="text-sm text-muted-foreground leading-relaxed">
                  <span className="font-medium">Rain = Revenue:</span> Your earnings increase significantly during wet weather, especially on weekends.
                </p>
              </div>
              <div className="flex gap-3">
                <div className="w-2 h-2 bg-secondary rounded-full mt-2 flex-shrink-0" />
                <p className="text-sm text-muted-foreground leading-relaxed">
                  <span className="font-medium">Demand follows search trends:</span> Higher Google search volume for Uber Eats correlates with your better weeks.
                </p>
              </div>
              <div className="flex gap-3">
                <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0" />
                <p className="text-sm text-muted-foreground leading-relaxed">
                  <span className="font-medium">Events matter:</span> Long weekends and public holidays provide consistent earning opportunities.
                </p>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
