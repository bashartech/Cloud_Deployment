'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { MessageCircle, X, Bot } from 'lucide-react';
import { ChatProvider } from './ChatProvider';
import ChatWindow from './ChatWindow';
import { authClient } from '@/lib/auth-client';

const FloatingChatbot: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [checkingAuth, setCheckingAuth] = useState(true);

  // Check authentication status on mount
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const session = await authClient.getSession();
        setIsAuthenticated(!!session);
      } catch (error) {
        console.error('Error checking auth status:', error);
        setIsAuthenticated(false);
      } finally {
        setCheckingAuth(false);
      }
    };

    checkAuth();
  }, []);

  // Handle sign out by listening to auth state changes
  useEffect(() => {
    if (!isAuthenticated && !checkingAuth) {
      // Clear any open chat windows when user signs out
      setIsOpen(false);
    }
  }, [isAuthenticated, checkingAuth]);

  // Toggle chat window
  const toggleChat = () => {
    if (!isAuthenticated && !checkingAuth) {
      // Redirect to login if not authenticated
      window.location.href = '/login';
      return;
    }
    setIsOpen(!isOpen);
  };

  // Remove the click outside to close functionality
  // Chat will only close via the close button

  if (checkingAuth) {
    return null; // Don't render anything while checking auth
  }

  if (!isAuthenticated) {
    return null; // Don't show the chatbot button to non-authenticated users
  }

  return (
    <>
      {/* Floating chat button */}
      {!isOpen && (
        <div className="fixed bottom-6 right-6 z-50 animate-fade-in">
          <Button
            onClick={toggleChat}
            className="rounded-full w-14 h-14 p-4 shadow-xl bg-gradient-to-br from-neutral-700 to-black  hover:from-neutral-700 hover:to-gray-900 text-white font-semibold rounded-full transition-all duration-300 hover:scale-105 hover:shadow-lg hover:shadow-blue-500/20 backdrop-blur-xl border border-white/20"
            aria-label="Open chatbot"
          >
            <div className="relative">
              <MessageCircle className="h-7 w-7 text-blue-300" />
              <div className="absolute top-0 right-0 w-2 h-2 bg-green-500 rounded-full border border-white"></div>
            </div>
          </Button>
        </div>
      )}

      {/* Chat window */}
      {isOpen && (
        <div
          id="floating-chat-container"
          className="fixed bottom-24 right-6 z-50 w-full max-w-xs sm:max-w-sm md:max-w-md lg:max-w-lg xl:max-w-xl h-[50vh] sm:h-[60vh] md:h-[65vh] lg:h-[600px] bg-transparent"
        >
          <Card className="h-full flex flex-col border border-neutral-800/50 rounded-xl overflow-hidden shadow-2xl bg-gradient-to-br from-neutral-900 to-neutral-950 text-white backdrop-blur-xl">
            <div className="flex items-center justify-between p-4 bg-gradient-to-r from-neutral-800/50 to-neutral-900/50 border-b border-neutral-700/50">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-blue-500/20 rounded-lg backdrop-blur-sm border border-blue-500/30">
                  <Bot className="h-5 w-5 text-blue-400" />
                </div>
                <div>
                  <h3 className="font-semibold text-white text-sm sm:text-base">AI Task Assistant</h3>
                  <p className="text-xs text-gray-400 hidden sm:block">Always here to help</p>
                </div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={toggleChat}
                className="h-9 w-9 p-0 rounded-full hover:bg-neutral-700/50 text-gray-300 hover:text-white transition-colors border border-neutral-700/50"
                aria-label="Close chat"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
            <CardContent className="flex-grow p-0 flex flex-col bg-neutral-900/50">
              <ChatProvider>
                <ChatWindow />
              </ChatProvider>
            </CardContent>
          </Card>
        </div>
      )}
    </>
  );
};

export default FloatingChatbot;