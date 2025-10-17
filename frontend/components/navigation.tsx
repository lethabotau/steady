import { Home, TrendingUp, BarChart3, User, Lightbulb } from "lucide-react";

interface NavigationProps {
	currentScreen: string;
	onScreenChange: (screen: string) => void;
}

export function Navigation ({ currentScreen, onScreenChange }: NavigationProps) {
	const navItems = [
		{ id: 'dashboard' , icon: Home, label: 'Home'}, 
		{ id: 'forecast' , icon: TrendingUp, label: 'Forecast'},
		{ id: 'insights' , icon: Lightbulb, label: 'Insights'},
		{ id: 'trends', icon: BarChart3, label: 'Trends' },
		{ id: 'profile', icon: User, label: 'Profile' }, 	
	];

	return (
		
	); 
}
