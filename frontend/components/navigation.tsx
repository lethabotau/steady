import { Home, TrendingUp, BarChart3, User, Lightbulb } from "lucide-react";

interface NavigationProps {
  currentScreen: string;
  onScreenChange: (screen: string) => void;
}

export function Navigation({ currentScreen, onScreenChange }: NavigationProps) {
  const navItems = [
    { id: 'dashboard', icon: Home, label: 'Home' },
    { id: 'forecast', icon: TrendingUp, label: 'Forecast' },
    { id: 'insights', icon: Lightbulb, label: 'Insights' },
    { id: 'trends', icon: BarChart3, label: 'Trends' },
    { id: 'profile', icon: User, label: 'Profile' },
  ];

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-card border-t border-border px-4 pb-6 pt-2">
      <div className="flex justify-around max-w-md mx-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentScreen === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onScreenChange(item.id)}
              className={`flex flex-col items-center gap-1 py-2 px-3 rounded-lg transition-colors ${
                isActive 
                  ? 'text-primary bg-muted' 
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              <Icon className={`w-5 h-5 ${isActive ? 'stroke-2' : 'stroke-1.5'}`} />
              <span className="text-xs">{item.label}</span>
            </button>
          );
        })}
      </div>
    </nav>
  );
}
