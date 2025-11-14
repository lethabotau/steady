import React from 'react';
import { Lock } from 'lucide-react';

interface LoginScreenProps {
  onLogin: () => void;
}

export function LoginScreen({ onLogin }: LoginScreenProps) {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-6" style={{ backgroundColor: '#FAF8F5' }}>
      <div className="w-full max-w-md">
        {/* Logo/Brand */}
        <div className="text-center mb-12">
          <h1 className="mb-2" style={{ color: '#1E4E40' }}>Steady</h1>
          <p className="text-gray-600">Financial stability for drivers</p>
        </div>

        {/* Main Card */}
        <div className="bg-white rounded-3xl shadow-lg p-8 mb-6">
          <h2 className="text-center mb-2" style={{ color: '#222' }}>Sign in to continue with Uber</h2>
          <p className="text-center text-gray-500 mb-8">
            Securely connect your driver account to view your earnings analytics
          </p>

          {/* Uber OAuth Button */}
          <button
            onClick={onLogin}
            className="w-full bg-black text-white py-4 rounded-xl flex items-center justify-center gap-3 hover:bg-gray-900 transition-colors mb-4"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <rect width="24" height="24" rx="4" fill="white"/>
              <path d="M7 9h3v6H7V9zm0-2h3v1H7V7zm4 0h6v8h-6V7z" fill="black"/>
            </svg>
            <span>Continue with Uber</span>
          </button>

          <div className="flex items-center gap-2 text-sm text-gray-500">
            <Lock size={14} />
            <span>Steady uses read-only access — your data stays private</span>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center text-sm text-gray-400">
          <p>By continuing, you agree to Steady's Terms of Service and Privacy Policy</p>
        </div>
      </div>
    </div>
  );
}
