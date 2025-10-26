import { Card } from "./ui/card";
import { ArrowLeft, Clock, Cloud, Calendar, MapPin, BarChart3, Users } from "lucide-react";

interface InsightsScreenProps {
  onBack: () => void;
}

export function InsightsScreen({ onBack }: InsightsScreenProps) {
  const timingInsights = [
    {
      icon: Clock,
      title: "You earn most between 6–9 PM on Fridays",
      subtitle: "Friday evening rush delivers 23% higher rates than weekday averages.",
      strength: "Strong"
    },
    {
      icon: Clock,
      title: "Morning shifts (7–10 AM) show steady demand",
      subtitle: "Consistent $28-32/hour during weekday breakfast hours.",
      strength: "Moderate"
    }
  ];

  const externalInsights = [
    {
      icon: Cloud,
      title: "Rain increases your earnings by 18% on average",
      subtitle: "Particularly effective during weekends and evening hours.",
      strength: "Strong"
    },
    {
      icon: Calendar,
      title: "Public holidays boost demand by ~10%",
      subtitle: "Especially effective near CBD and Inner West areas.",
      strength: "Moderate"
    },
    {
      icon: MapPin,
      title: "Surry Hills and Newtown are your best areas",
      subtitle: "Higher tips and shorter wait times between rides.",
      strength: "Strong"
    }
  ];

  const behavioralInsights = [
    {
      icon: BarChart3,
      title: "Driving four days a week produces steadiest results",
      subtitle: "Better work-life balance with only 8% earnings variance.",
      strength: "Strong"
    },
    {
      icon: Users,
      title: "You perform 15% better during Uber Eats dinner rush",
      subtitle: "Consider focusing more on food delivery 6-9 PM.",
      strength: "Moderate"
    }
  ];

  const InsightCard = ({ insights, title }: { insights: any[], title: string }) => (
    <div className="space-y-4">
      <h3 className="text-lg font-medium text-foreground">{title}</h3>
      {insights.map((insight, index) => {
        const Icon = insight.icon;
        return (
          <Card key={index} className="p-4 bg-card border-border">
            <div className="flex gap-3">
              <div className="flex-shrink-0">
                <div className="w-10 h-10 bg-muted rounded-lg flex items-center justify-center">
                  <Icon className="w-5 h-5 text-primary" />
                </div>
              </div>
              
              <div className="flex-1 space-y-3">
                <div className="space-y-1">
                  <h4 className="font-medium text-foreground leading-snug">
                    {insight.title}
                  </h4>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    {insight.subtitle}
                  </p>
                </div>
                
                <div className="flex items-center gap-2">
                  <div className={`h-1.5 rounded-full ${
                    insight.strength === 'Strong' 
                      ? 'w-16 bg-primary' 
                      : 'w-10 bg-secondary'
                  }`} />
                  <span className="text-xs text-muted-foreground font-medium">
                    {insight.strength}
                  </span>
                </div>
              </div>
            </div>
          </Card>
        );
      })}
    </div>
  );

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
            <h1 className="text-xl font-semibold text-foreground">Insights</h1>
            <p className="text-sm text-muted-foreground">Data-driven advice for better earnings</p>
          </div>
        </div>
      </div>

      <div className="px-6 space-y-8">
        {/* Summary Card */}
        <Card className="p-6 bg-gradient-to-br from-primary/5 to-secondary/5 border-border">
          <div className="space-y-4">
            <h3 className="text-lg font-medium">Your Earnings Profile</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <p className="text-2xl font-semibold text-foreground">$865</p>
                <p className="text-sm text-muted-foreground">Weekly average</p>
              </div>
              <div className="space-y-1">
                <p className="text-2xl font-semibold text-primary">9%</p>
                <p className="text-sm text-muted-foreground">Earnings volatility</p>
              </div>
            </div>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Youre consistently earning more than 72% of Sydney drivers, with excellent stability during weather events.
            </p>
          </div>
        </Card>

        {/* Timing Insights */}
        <InsightCard insights={timingInsights} title="Timing Patterns" />

        {/* External Factors */}
        <InsightCard insights={externalInsights} title="External Factors" />

        {/* Behavioral Patterns */}
        <InsightCard insights={behavioralInsights} title="Behavioral Patterns" />

        {/* Action Recommendations */}
        <Card className="p-6 bg-card border-border">
          <div className="space-y-4">
            <h3 className="text-lg font-medium">Recommended Actions</h3>
            <div className="space-y-3">
              <div className="flex gap-3">
                <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0" />
                <p className="text-sm text-muted-foreground leading-relaxed">
                  Focus on Friday 6-9 PM shifts for maximum earnings potential
                </p>
              </div>
              <div className="flex gap-3">
                <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0" />
                <p className="text-sm text-muted-foreground leading-relaxed">
                  Add short shifts during rainy weekend periods
                </p>
              </div>
              <div className="flex gap-3">
                <div className="w-2 h-2 bg-secondary rounded-full mt-2 flex-shrink-0" />
                <p className="text-sm text-muted-foreground leading-relaxed">
                  Consider more Uber Eats during dinner hours
                </p>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
