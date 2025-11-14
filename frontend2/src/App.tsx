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
  const [weeklyGoal, setWeeklyGoal] = useState(1000);
  const [userData, setUserData] = useState<OnboardingData | null>(null);

  const handleLogin = () => {
    setCurrentScreen('onboarding');
  };

  const handleOnboardingComplete = (data: OnboardingData) => {
    setUserData(data);
    setWeeklyGoal(data.weeklyGoal);
    setCurrentScreen('dashboard');
  };

  const handleNavigate = (screen: string) => {
    setCurrentScreen(screen as AppScreen);
  };

  const handleUpdateGoal = (newGoal: number) => {
    setWeeklyGoal(newGoal);
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
        <ForecastDetailScreen />
      )}

      {currentScreen === 'insights' && (
        <InsightsScreen />
      )}

      {currentScreen === 'trends' && (
        <TrendsScreen />
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
