'use client';

import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import { ChatMessage } from '@/services/chat-service';
import { authClient } from '@/lib/auth-client';

interface ChatContextType {
  messages: ChatMessage[];
  addMessage: (message: ChatMessage) => void;
  clearMessages: () => void;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
  conversationId: number | null;
  setConversationId: (id: number | null) => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const ChatProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<number | null>(null);

  const addMessage = (message: ChatMessage) => {
    setMessages(prev => [...prev, message]);
  };

  const clearMessages = () => {
    setMessages([]);
    setConversationId(null);
  };

  // Clear chat state when user signs out by checking session periodically
  useEffect(() => {
    const checkSessionAndClear = async () => {
      try {
        const session = await authClient.getSession();
        if (!session) {
          // User is not authenticated, clear messages
          clearMessages();
        }
      } catch (error) {
        // If there's an error getting session, clear messages
        clearMessages();
      }
    };

    // Check session on mount and periodically
    checkSessionAndClear();

    // Set up interval to check session (every 5 seconds)
    const intervalId = setInterval(checkSessionAndClear, 5000);

    // Cleanup interval on unmount
    return () => {
      clearInterval(intervalId);
    };
  }, []);

  return (
    <ChatContext.Provider
      value={{
        messages,
        addMessage,
        clearMessages,
        isLoading,
        setIsLoading,
        conversationId,
        setConversationId
      }}
    >
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = (): ChatContextType => {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};