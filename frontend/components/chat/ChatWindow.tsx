'use client';

import React, { useState, useEffect, useRef } from 'react';
import {
  MainContainer,
  ChatContainer,
  MessageList,
  Message,
  MessageInput,
  TypingIndicator
} from '@chatscope/chat-ui-kit-react';
// CSS import causes type errors, so we'll import globally in layout.tsx
import { useChat } from '@/components/chat/ChatProvider';
import { chatService, ChatMessage } from '@/services/chat-service';
import { authClient } from '@/lib/auth-client';

const ChatWindow: React.FC = () => {
  const { messages, addMessage, isLoading, setIsLoading, conversationId, setConversationId } = useChat();
  const messageEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom when messages change with smooth behavior
  useEffect(() => {
    messageEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (message: string) => {
    if (!message.trim()) return;

    // Add user message to UI immediately
    const userMessage: ChatMessage = {
      role: 'user',
      content: message,
      timestamp: new Date().toISOString()
    };
    addMessage(userMessage);

    setIsLoading(true);

    try {
      // Send message to backend
      const response = await chatService.sendMessage(message, conversationId);
      console.log("CHAT RESPONSE -->>>", response);

      // Update conversation ID if it's the first message
      if (conversationId === null || conversationId === undefined) {
        setConversationId(response.conversation_id);
      }

      // Add assistant response to UI
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.response,
        timestamp: new Date().toISOString()
      };
      addMessage(assistantMessage);
    } catch (error) {
      console.error('Error sending message:', error);

      // Add error message to UI
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        timestamp: new Date().toISOString()
      };
      addMessage(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <MainContainer className="bg-transparent rounded-xl" style={{ height: '100%', border: 'none', borderRadius: '8px', backgroundColor: 'transparent' }}>
      <ChatContainer style={{ height: '100%', display: 'flex', flexDirection: 'column', backgroundColor: 'transparent' }}>
        <MessageList
          className="p-3 sm:p-4 flex-grow bg-neutral-900/30"
          style={{
            overflowY: 'auto',
            backgroundColor: 'transparent',
            maxHeight: 'calc(100vh - 150px)', // Ensure there's always space for input and header
            minHeight: '150px',
            flex: 1,
            scrollbarWidth: 'thin',
            scrollbarColor: '#374151 #111827'
          }}
        >
          {isLoading && <TypingIndicator content="AI is thinking..." className="text-gray-400" style={{ backgroundColor: 'transparent' }} />}
          {messages.map((msg, index) => (
            <Message
              key={index}
              model={{
                message: msg.content,
                sender: msg.role,
                direction: msg.role === 'user' ? 'outgoing' : 'incoming',
                position: 'normal'
              }}
              className={`
                mb-2 sm:mb-3 rounded-lg p-3 sm:p-4 max-w-[80%] sm:max-w-[85%] shadow-sm text-sm
                ${msg.role === 'user'
                  ? 'ml-auto text-white rounded-br-none'
                  : 'mr-auto bg-neutral-800/60 text-gray-100 rounded-bl-none border border-neutral-700/50'}
              `}
            />
          ))}
          <div ref={messageEndRef} />
        </MessageList>
        <MessageInput
          placeholder="Type your message here..."
          onSend={handleSend}
          attachButton={false}  // Remove attachment button for cleaner UI
          disabled={isLoading}
          className="border-t border-neutral-700/50 bg-neutral-900/50 text-white placeholder-gray-400 text-sm p-3"
          style={{
            marginTop: 'auto',
            backgroundColor: 'rgba(17, 24, 39, 0.6)',
            color: 'white',
            borderColor: '#374151',
            padding: '0.75rem'
          }}
        />
      </ChatContainer>
    </MainContainer>
  );
};

export default ChatWindow;