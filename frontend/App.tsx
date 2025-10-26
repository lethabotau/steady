import { useState } from 'react';
import { LoginScreen } from './components/login-screen';
import { DashboardScreen } from './components/dashboard-screen';
import { ForecastScreen } from './components/forecast-screen';
import { InsightsScreen } from './components/insights-screen';
import { TrendsScreen } from './components/trends-screen';
import { ProfileScreen } from './components/profile-screen';
import { Navigation } from './components/navigation';

export default function App(){
	
	//default starting screen set to dashboard as a default 
	const [currentScreen, setCurrentScreen] = useState('dashboard');
	const [isLoggedIn, setIsLoggedIn] = useState(false);

	  const handleLogin = () => {
	    setIsLoggedIn(true);
	  };

	  const handleLogout = () => {
	    setIsLoggedIn(false);
	    setCurrentScreen('dashboard');
	  };

	  const handleScreenChange = (screen: string) => {
	    setCurrentScreen(screen);
	  };

	  const handleBackToDashboard = () => {
	    setCurrentScreen('dashboard');
	  };

	  if (!isLoggedIn) {
	    return <LoginScreen onLogin={handleLogin} />;
	  }
	
	const renderScreen = () => {
	//using a switch statement to switch between screens
		switch (currentScreen){
	      case 'dashboard':
	        return <DashboardScreen />;
	      case 'forecast':
	        return <ForecastScreen onBack={handleBackToDashboard} />;
	      case 'insights':
	        return <InsightsScreen onBack={handleBackToDashboard} />;
	      case 'trends':
	        return <TrendsScreen onBack={handleBackToDashboard} />;
	      case 'profile':
	        return <ProfileScreen onBack={handleBackToDashboard} onLogout={handleLogout} />;
	      default:
	        return <DashboardScreen />;
		}	
	};

	return (
		<div className="min-h-screen bg-background">
			{renderScreen()}
			<Navigation
				currentScreen={currentScreen}
				onScreenChange={handleScreenChange}
			/>
		</div>	
	);
}
