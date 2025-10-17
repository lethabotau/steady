import { useState } from 'react';
import { Navigation } from './components/navigation'

export default function App(){
	
	//default starting screen set to placeholder default 
	const [currentScreen, setCurrentScreen] = useState('default')
	
	const renderScreen = () => {
	//using a switch statement to switch between screens
		switch (currentScreen){
		//placeholder case
			case 'a':
				return <screenA />; 
		}	
	}

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
