import { useState } from 'react';

export default function App(){

	const renderScreen = () => {
	//using a switch statement to switch between screens
		switch (x){
		//placeholder case
			case 'a':
				return <screenA />; 
		}	
	}

	return (
		<div className="min-h-screen bg-background">
			{renderScreen()}
			<Navigation />
		</div>	
	);
}
