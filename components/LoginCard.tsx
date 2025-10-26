import React, { useState } from 'react';
import { auth } from '../auth-oauth2';

interface LoginCardProps {
  onSignIn: (user: any) => void;
  onError: (error: string) => void;
}

const LoginCard: React.FC<LoginCardProps> = ({ onSignIn, onError }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [showGuestForm, setShowGuestForm] = useState(false);
  const [guestName, setGuestName] = useState('');

  const handleGoogleSignIn = async () => {
    setIsLoading(true);
    try {
      await auth.signIn();
      // The OAuth flow will handle the redirect
    } catch (error: any) {
      onError(`Google sign-in failed: ${error.message}. Please try guest mode instead.`);
      setIsLoading(false);
    }
  };

  const handleGuestSignIn = () => {
    if (!showGuestForm) {
      setShowGuestForm(true);
      return;
    }

    if (!guestName.trim()) {
      onError('Please enter your name');
      return;
    }

    try {
      auth.signInAsGuest(guestName.trim());
      onSignIn(auth.getCurrentUser());
    } catch (error: any) {
      onError(`Guest sign-in failed: ${error.message}`);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-900 font-sans">
      <div className="w-full max-w-md p-8 space-y-6 bg-gray-800 rounded-2xl shadow-2xl border border-gray-700">
        {/* Logo and Title */}
        <div className="text-center">
          <div className="logo-container mb-6">
            <img 
              src="https://github.com/valonys/DigiTwin/blob/29dd50da95bec35a5abdca4bdda1967f0e5efff6/ValonyLabs_Logo.png?raw=true" 
              width="70" 
              alt="ValonyLabs Logo"
              className="mx-auto"
            />
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">AgenticOne</h1>
          <p className="text-cyan-400 mt-4">Choose your sign-in method</p>
        </div>
        
        {/* Guest Login Form */}
        {!showGuestForm ? (
          <div className="space-y-4">
            <button
              onClick={handleGoogleSignIn}
              disabled={isLoading}
              className="w-full flex items-center justify-center px-6 py-3 bg-white text-gray-900 rounded-lg font-medium hover:bg-gray-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-gray-900 mr-3"></div>
              ) : (
                <svg className="w-5 h-5 mr-3" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
              )}
              Continue with Google
            </button>
            
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-600"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-gray-800 text-gray-400">or</span>
              </div>
            </div>
            
            <button
              onClick={() => setShowGuestForm(true)}
              className="w-full flex items-center justify-center px-6 py-3 bg-gray-700 text-white rounded-lg font-medium hover:bg-gray-600 transition-colors"
            >
              <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              Continue as Guest
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            <div>
              <label htmlFor="guestName" className="block text-sm font-medium text-gray-300 mb-2">
                Enter your name
              </label>
              <input
                id="guestName"
                type="text"
                value={guestName}
                onChange={(e) => setGuestName(e.target.value)}
                placeholder="Your name"
                className="w-full px-4 py-3 bg-gray-700 text-white rounded-lg border border-gray-600 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 focus:outline-none"
                autoFocus
              />
            </div>
            
            <div className="flex space-x-3">
              <button
                onClick={handleGuestSignIn}
                className="flex-1 bg-cyan-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-cyan-700 transition-colors"
              >
                Continue as Guest
              </button>
              <button
                onClick={() => setShowGuestForm(false)}
                className="flex-1 bg-gray-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-gray-700 transition-colors"
              >
                Back
              </button>
            </div>
          </div>
        )}
        
        {/* Footer */}
        <div className="text-center text-xs text-gray-500">
          <p>By continuing, you agree to our Terms of Service and Privacy Policy</p>
        </div>
      </div>
    </div>
  );
};

export default LoginCard;
