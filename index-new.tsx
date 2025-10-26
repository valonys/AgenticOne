import React, { useState, useRef, useEffect, useCallback, memo } from 'react';
import { createRoot } from 'react-dom/client';
import { GoogleGenAI } from "@google/genai";
import { auth, type GoogleUser } from './auth-oauth2';
import LoginCard from './components/LoginCard';

import type { Message, Agent, AgentRole, RagSources, UploadedFileState } from './types';
import { AGENT_ROLES, UserAvatar, AssistantAvatar } from './constants';

const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

const MAX_FILES = 5;
const MAX_FILE_SIZE_MB = 10;
const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024;
const TOTAL_TOKEN_LIMIT = 10000;

const AppLogo: React.FC<{ className?: string }> = ({ className }) => (
    <img 
        src="https://github.com/valonys/DigiTwin/blob/29dd50da95bec35a5abdca4bdda1967f0e5efff6/ValonyLabs_Logo.png?raw=true" 
        alt="Valony Labs Logo"
        className={className}
    />
);

const LoginScreen: React.FC = memo(() => {
    const [error, setError] = useState<string | null>(null);

    const handleSignIn = (user: GoogleUser) => {
        // User successfully signed in
        console.log('User signed in:', user);
    };

    const handleError = (errorMessage: string) => {
        setError(errorMessage);
    };

    return (
        <div>
            {error && (
                <div className="fixed top-4 right-4 p-4 bg-red-900/20 border border-red-500/30 rounded-lg z-50">
                    <p className="text-red-200 text-sm">{error}</p>
                    <button 
                        onClick={() => setError(null)}
                        className="mt-2 text-red-300 hover:text-red-100 text-xs"
                    >
                        Dismiss
                    </button>
                </div>
            )}
            <LoginCard onSignIn={handleSignIn} onError={handleError} />
        </div>
    );
});

const App: React.FC = () => {
    const [user, setUser] = useState<GoogleUser | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        // Check if user is already authenticated
        const currentUser = auth.getCurrentUser();
        if (currentUser) {
            setUser(currentUser);
        }

        // Listen for auth state changes
        const unsubscribe = auth.onAuthStateChanged((user) => {
            setUser(user);
        });

        return () => unsubscribe();
    }, []);

    const handleSignOut = useCallback(async () => {
        try {
            await auth.signOut();
            setUser(null);
        } catch (error) {
            console.error("Sign out error:", error);
        }
    }, []);

    // Show login screen if not authenticated
    if (!user) {
        return <LoginScreen />;
    }

    // Main application content
    return (
        <div className="min-h-screen bg-gray-900 text-white">
            {/* Header */}
            <header className="bg-gray-800 border-b border-gray-700">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between items-center h-16">
                        <div className="flex items-center">
                            <AppLogo className="h-8 w-8 mr-3" />
                            <div>
                                <h1 className="text-xl font-bold">AgenticOne</h1>
                                <p className="text-sm text-gray-400">AI Beyond Compare</p>
                            </div>
                        </div>
                        <div className="flex items-center space-x-4">
                            <span className="text-sm text-gray-300">
                                Welcome, {user.name}
                            </span>
                            <button
                                onClick={handleSignOut}
                                className="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                            >
                                Sign Out
                            </button>
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="text-center">
                    <h2 className="text-3xl font-bold text-white mb-4">
                        Welcome to AgenticOne
                    </h2>
                    <p className="text-gray-400 text-lg mb-8">
                        Your AI-powered engineering analysis platform is ready
                    </p>
                    
                    {/* Agent Selection */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                        {Object.entries(AGENT_ROLES).map(([key, agent]) => (
                            <div key={key} className="bg-gray-800 rounded-lg p-6 border border-gray-700 hover:border-cyan-500 transition-colors">
                                <div className="text-center">
                                    <div className="w-12 h-12 bg-cyan-600 rounded-full flex items-center justify-center mx-auto mb-4">
                                        <span className="text-white font-bold text-lg">
                                            {agent.name.charAt(0)}
                                        </span>
                                    </div>
                                    <h3 className="text-lg font-semibold text-white mb-2">
                                        {agent.name}
                                    </h3>
                                    <p className="text-gray-400 text-sm mb-4">
                                        {agent.description}
                                    </p>
                                    <button className="w-full bg-cyan-600 hover:bg-cyan-700 text-white py-2 px-4 rounded-lg font-medium transition-colors">
                                        Start Chat
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Quick Actions */}
                    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                        <h3 className="text-xl font-semibold text-white mb-4">
                            Quick Actions
                        </h3>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <button className="bg-gray-700 hover:bg-gray-600 p-4 rounded-lg transition-colors">
                                <div className="text-center">
                                    <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-2">
                                        <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
                                        </svg>
                                    </div>
                                    <span className="text-sm font-medium">Upload Documents</span>
                                </div>
                            </button>
                            
                            <button className="bg-gray-700 hover:bg-gray-600 p-4 rounded-lg transition-colors">
                                <div className="text-center">
                                    <div className="w-8 h-8 bg-green-600 rounded-full flex items-center justify-center mx-auto mb-2">
                                        <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                        </svg>
                                    </div>
                                    <span className="text-sm font-medium">Generate Report</span>
                                </div>
                            </button>
                            
                            <button className="bg-gray-700 hover:bg-gray-600 p-4 rounded-lg transition-colors">
                                <div className="text-center">
                                    <div className="w-8 h-8 bg-purple-600 rounded-full flex items-center justify-center mx-auto mb-2">
                                        <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                        </svg>
                                    </div>
                                    <span className="text-sm font-medium">View Analytics</span>
                                </div>
                            </button>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
};

// Initialize the app
const container = document.getElementById('root');
if (container) {
    const root = createRoot(container);
    root.render(<App />);
} else {
    console.error('Root element not found');
}
