import React, { useState } from 'react';
import { LoginScreen } from './components/LoginScreen';
import { OnboardingScreen, OnboardingData } from './components/OnboardingScreen';
import { DashboardScreen } from './components/DashboardScreen';
import { ForecastDetailScreen } from './components/ForecastDetailScreen';
import { InsightsScreen } from './components/InsightsScreen';
import { TrendsScreen } from './components/TrendsScreen';
import { ProfileScreen } from './components/ProfileScreen';
import { BottomNav } from './components/BottomNav';

type AppScreen = 'login' | 'onboarding' | 'dashboard' | 'forecast' | 'insights' | 'trends' | 'profile';

export default function App() {
  const [currentScreen, setCurrentScreen] = useState<AppScreen>('login');
  const [weeklyGoal, setWeeklyGoal] = useState(() => {
    if (typeof window === 'undefined') return 1000;
    const saved = window.localStorage.getItem('steady:weeklyGoal');
    const parsed = saved ? parseInt(saved, 10) : NaN;
    return Number.isFinite(parsed) && parsed > 0 ? parsed : 1000;
  });
  const [userData, setUserData] = useState<OnboardingData | null>(null);

  const handleLogin = () => {
    setCurrentScreen('onboarding');
  };

  const handleOnboardingComplete = (data: OnboardingData) => {
    setUserData(data);
    persistWeeklyGoal(data.weeklyGoal);
    setCurrentScreen('dashboard');
  };

  const handleNavigate = (screen: string) => {
    setCurrentScreen(screen as AppScreen);
  };

  const handleUpdateGoal = (newGoal: number) => {
    persistWeeklyGoal(newGoal);
  };

  const persistWeeklyGoal = (newGoal: number) => {
    setWeeklyGoal(newGoal);
    if (typeof window !== 'undefined') {
      window.localStorage.setItem('steady:weeklyGoal', String(newGoal));
    }
  };

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#FAF8F5' }}>
      {/* Login Screen */}
      {currentScreen === 'login' && (
        <LoginScreen onLogin={handleLogin} />
      )}

      {/* Onboarding Screen */}
      {currentScreen === 'onboarding' && (
        <OnboardingScreen onComplete={handleOnboardingComplete} />
      )}

      {/* Main App Screens */}
      {currentScreen === 'dashboard' && (
        <DashboardScreen weeklyGoal={weeklyGoal} />
      )}

      {currentScreen === 'forecast' && (
        <ForecastDetailScreen weeklyGoal={weeklyGoal} />
      )}

      {currentScreen === 'insights' && (
        <InsightsScreen weeklyGoal={weeklyGoal} />
      )}

      {currentScreen === 'trends' && (
        <TrendsScreen weeklyGoal={weeklyGoal} />
      )}

      {currentScreen === 'profile' && (
        <ProfileScreen weeklyGoal={weeklyGoal} onUpdateGoal={handleUpdateGoal} />
      )}

      {/* Bottom Navigation - Show only after onboarding */}
      {currentScreen !== 'login' && currentScreen !== 'onboarding' && (
        <BottomNav activeScreen={currentScreen} onNavigate={handleNavigate} />
      )}
    </div>
  );
}
