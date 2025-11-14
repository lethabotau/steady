import React from 'react';
import { Home, TrendingUp, Lightbulb, BarChart3, User } from 'lucide-react';

interface BottomNavProps {
  activeScreen: string;
  onNavigate: (screen: string) => void;
}

export function BottomNav({ activeScreen, onNavigate }: BottomNavProps) {
  const navItems = [
    { id: 'dashboard', icon: Home, label: 'Home' },
    { id: 'forecast', icon: TrendingUp, label: 'Forecast' },
    { id: 'insights', icon: Lightbulb, label: 'Insights' },
    { id: 'trends', icon: BarChart3, label: 'Trends' },
    { id: 'profile', icon: User, label: 'Profile' },
  ];

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-4 py-2 safe-area-bottom">
      <div className="max-w-md mx-auto flex items-center justify-around">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeScreen === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className="flex flex-col items-center gap-1 py-2 px-3 rounded-xl transition-all"
              style={{
                color: isActive ? '#1E4E40' : '#999'
              }}
            >
              <Icon size={24} strokeWidth={isActive ? 2.5 : 2} />
              <span className="text-xs">{item.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
