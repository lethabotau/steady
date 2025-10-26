import { Button } from "./ui/button";
import { ImageWithFallback } from "./figma/ImageWithFallback";

interface LoginScreenProps {
  onLogin: () => void;
}

export function LoginScreen({ onLogin }: LoginScreenProps) {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-background px-6">
      <div className="w-full max-w-sm space-y-8">
        {/* Logo/Brand */}
        <div className="text-center space-y-4">
          <div className="w-16 h-16 bg-primary rounded-2xl flex items-center justify-center mx-auto">
            <span className="text-xl text-primary-foreground font-semibold">S</span>
          </div>
          <div className="space-y-2">
            <h1 className="text-2xl font-semibold text-foreground">Welcome to Steady</h1>
            <p className="text-muted-foreground">Your financial stability companion for driving in Sydney</p>
          </div>
        </div>

        {/* Login Card */}
        <div className="space-y-6">
          <div className="space-y-4">
            <h2 className="text-lg text-center">Sign in to continue with Uber</h2>
            
            <Button 
              onClick={onLogin}
              className="w-full bg-black text-white hover:bg-black/90 h-12 rounded-xl"
            >
              Continue with Uber
            </Button>
            
            <p className="text-sm text-muted-foreground text-center leading-relaxed">
              Securely connect your Sydney driver account to view insights and forecasts.
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center">
          <p className="text-xs text-muted-foreground leading-relaxed">
            Steady uses read-only access. Your Uber data stays private.
          </p>
        </div>
      </div>
    </div>
  );
}
