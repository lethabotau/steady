import { Card } from "./ui/card";
import { Progress } from "./ui/progress";
import { TrendingUp, TrendingDown, Cloud, Clock, MapPin, BarChart3 } from "lucide-react";

export function DashboardScreen() {
  const forecasts = [
    {
      icon: Cloud,
      title: "Rainy weekends boosted your income by 14%",
      subtitle: "Consider adding short shifts when storms hit Sydney.",
      strength: "Strong"
    },
    {
      icon: Clock,
      title: "Earnings are highest between 5 PM – 8 PM",
      subtitle: "Staying active during this window improves stability.",
      strength: "Strong"
    },
    {
      icon: BarChart3,
      title: "Your weekly hours are balanced",
      subtitle: "Maintaining around 25–28 hours gives steadier pay.",
      strength: "Moderate"
    }
  ];

  return (
    <div className="pb-24 bg-background min-h-screen">
      {/* Header */}
      <div className="px-6 pt-12 pb-6">
        <div className="space-y-1">
          <h1 className="text-2xl font-semibold text-foreground">Your Weekly Outlook</h1>
          <p className="text-muted-foreground">Monday, October 6, 2025</p>
        </div>
      </div>

      <div className="px-6 space-y-6">
        {/* Forecast Card */}
        <Card className="p-6 bg-card border-border">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <h3 className="text-lg font-medium">This Weeks Forecast</h3>
                <p className="text-sm text-muted-foreground">Based on your patterns</p>
              </div>
              <TrendingUp className="w-5 h-5 text-primary" />
            </div>
            
            <div className="space-y-2">
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-semibold text-foreground">$930</span>
                <span className="text-muted-foreground">± $60</span>
              </div>
              <div className="flex items-center gap-1 text-sm text-primary">
                <TrendingUp className="w-4 h-4" />
                <span>Likely to rise slightly next week</span>
              </div>
            </div>
          </div>
        </Card>

        {/* Steadiness Gauge */}
        <Card className="p-6 bg-card border-border">
          <div className="space-y-4">
            <h3 className="text-lg font-medium">Income Steadiness</h3>
            
            <div className="space-y-3">
              <div className="relative w-32 h-32 mx-auto">
                <svg className="w-32 h-32 transform -rotate-90" viewBox="0 0 100 100">
                  <circle
                    cx="50"
                    cy="50"
                    r="40"
                    stroke="#E1E6E2"
                    strokeWidth="8"
                    fill="none"
                  />
                  <circle
                    cx="50"
                    cy="50"
                    r="40"
                    stroke="#6B8E6E"
                    strokeWidth="8"
                    fill="none"
                    strokeDasharray={`${72 * 2.51} ${(100 - 72) * 2.51}`}
                    strokeLinecap="round"
                    className="transition-all duration-1000"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center">
                    <div className="text-2xl font-semibold text-foreground">72%</div>
                    <div className="text-xs text-muted-foreground">Steady</div>
                  </div>
                </div>
              </div>
              
              <p className="text-sm text-muted-foreground text-center">
                More consistent than 72% of Sydney drivers
              </p>
            </div>
          </div>
        </Card>

        {/* Goal Progress */}
        <Card className="p-6 bg-card border-border">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium">Weekly Goal</h3>
              <span className="text-sm text-muted-foreground">$780 of $900</span>
            </div>
            
            <div className="space-y-2">
              <Progress value={86.7} className="h-2" />
              <p className="text-sm text-muted-foreground">
                You're ahead of schedule! 87% complete with 2 days left.
              </p>
            </div>
          </div>
        </Card>

        {/* Smart Insights Feed */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium">Smart Insights</h3>
          
          {forecasts.map((insight, index) => {
            const Icon = insight.icon;
            return (
              <Card key={index} className="p-4 bg-card border-border">
                <div className="flex gap-3">
                  <div className="flex-shrink-0">
                    <div className="w-10 h-10 bg-muted rounded-lg flex items-center justify-center">
                      <Icon className="w-5 h-5 text-primary" />
                    </div>
                  </div>
                  
                  <div className="flex-1 space-y-2">
                    <div className="space-y-1">
                      <h4 className="font-medium text-foreground leading-snug">
                        {insight.title}
                      </h4>
                      <p className="text-sm text-muted-foreground leading-relaxed">
                        {insight.subtitle}
                      </p>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <div className={`h-1 rounded-full ${
                        insight.strength === 'Strong' ? 'w-12 bg-primary' : 'w-8 bg-secondary'
                      }`} />
                      <span className="text-xs text-muted-foreground">{insight.strength}</span>
                    </div>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      </div>
    </div>
  );
}
