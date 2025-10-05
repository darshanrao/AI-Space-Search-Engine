'use client';

import { useState, useEffect } from 'react';

// Extend window interface for sessions sidebar
declare global {
  interface Window {
    sessionsSidebar?: {
      addSession: (id: string, title: string, lastMessage?: string) => void;
      updateSession: (id: string, title: string, lastMessage?: string) => void;
      deleteSession: (id: string) => void;
      generateTitle: (message: string) => string;
    };
  }
}

interface ChatSession {
  id: string;
  title: string;
  timestamp: Date;
  lastMessage?: string;
}

interface SessionsSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  currentSessionId: string | null;
  onSessionSelect: (sessionId: string) => void;
  onNewSession: () => void;
}

export default function SessionsSidebar({ 
  isOpen, 
  onClose, 
  currentSessionId, 
  onSessionSelect, 
  onNewSession 
}: SessionsSidebarProps) {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Load sessions from localStorage
  useEffect(() => {
    const loadSessions = () => {
      try {
        const savedSessions = localStorage.getItem('space_bio_sessions');
        if (savedSessions) {
          const parsedSessions = JSON.parse(savedSessions).map((session: any) => ({
            ...session,
            timestamp: new Date(session.timestamp)
          }));
          setSessions(parsedSessions.sort((a: ChatSession, b: ChatSession) => 
            b.timestamp.getTime() - a.timestamp.getTime()
          ));
        }
      } catch (error) {
        console.error('Error loading sessions:', error);
      }
    };

    loadSessions();
  }, []);

  // Save sessions to localStorage
  const saveSessions = (newSessions: ChatSession[]) => {
    try {
      localStorage.setItem('space_bio_sessions', JSON.stringify(newSessions));
    } catch (error) {
      console.error('Error saving sessions:', error);
    }
  };

  // Add a new session
  const addSession = (sessionId: string, title: string, lastMessage?: string) => {
    const newSession: ChatSession = {
      id: sessionId,
      title: title,
      timestamp: new Date(),
      lastMessage
    };

    const updatedSessions = [newSession, ...sessions.filter(s => s.id !== sessionId)];
    setSessions(updatedSessions);
    saveSessions(updatedSessions);
  };

  // Update session title and last message
  const updateSession = (sessionId: string, title: string, lastMessage?: string) => {
    const updatedSessions = sessions.map(session => 
      session.id === sessionId 
        ? { ...session, title, lastMessage, timestamp: new Date() }
        : session
    );
    setSessions(updatedSessions);
    saveSessions(updatedSessions);
  };

  // Delete a session
  const deleteSession = (sessionId: string) => {
    const updatedSessions = sessions.filter(s => s.id !== sessionId);
    setSessions(updatedSessions);
    saveSessions(updatedSessions);
    
    // If we're deleting the current session, start a new one
    if (sessionId === currentSessionId) {
      onNewSession();
    }
  };

  // Generate title from first message
  const generateTitle = (message: string): string => {
    const words = message.trim().split(' ');
    if (words.length <= 4) return message;
    return words.slice(0, 4).join(' ') + '...';
  };

  // Expose functions to parent component
  useEffect(() => {
    // Store functions in window for parent to access
    window.sessionsSidebar = {
      addSession,
      updateSession,
      deleteSession,
      generateTitle
    };
  }, [sessions]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-40 flex">
      {/* Sidebar */}
      <div className="w-80 bg-gray-900 border-r border-gray-700 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-700">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white">Chat Sessions</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-white transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          {/* New Chat Button */}
          <button
            onClick={onNewSession}
            className="w-full mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors flex items-center justify-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            New Chat
          </button>
        </div>

        {/* Sessions List */}
        <div className="flex-1 overflow-y-auto">
          {sessions.length === 0 ? (
            <div className="p-4 text-center text-gray-400">
              <svg className="w-12 h-12 mx-auto mb-3 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              <p className="text-sm">No chat sessions yet</p>
              <p className="text-xs mt-1">Start a new conversation to see it here</p>
            </div>
          ) : (
            <div className="p-2">
              {sessions.map((session) => (
                <div
                  key={session.id}
                  className={`group relative p-3 rounded-lg cursor-pointer transition-colors mb-2 ${
                    session.id === currentSessionId
                      ? 'bg-blue-600/20 border border-blue-500/30'
                      : 'hover:bg-gray-800/50'
                  }`}
                  onClick={() => onSessionSelect(session.id)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <h3 className="text-sm font-medium text-white truncate">
                        {session.title}
                      </h3>
                      {session.lastMessage && (
                        <p className="text-xs text-gray-400 mt-1 line-clamp-2">
                          {session.lastMessage}
                        </p>
                      )}
                      <p className="text-xs text-gray-500 mt-1">
                        {session.timestamp.toLocaleDateString()} at {session.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </p>
                    </div>
                    
                    {/* Delete Button */}
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteSession(session.id);
                      }}
                      className="opacity-0 group-hover:opacity-100 ml-2 p-1 text-gray-400 hover:text-red-400 transition-all"
                      title="Delete session"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-700">
          <div className="text-xs text-gray-500 text-center">
            Space Bio Assistant
          </div>
        </div>
      </div>
      
      {/* Backdrop */}
      <div 
        className="flex-1 bg-black bg-opacity-50 backdrop-blur-sm"
        onClick={onClose}
      />
    </div>
  );
}
