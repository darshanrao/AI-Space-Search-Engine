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
  const [isMounted, setIsMounted] = useState(false);

  // Set mounted state
  useEffect(() => {
    setIsMounted(true);
  }, []);

  // Load sessions from localStorage
  useEffect(() => {
    if (!isMounted) return;
    
    const loadSessions = () => {
      if (typeof window === 'undefined') return;
      
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
  }, [isMounted]);

  // Save sessions to localStorage
  const saveSessions = (newSessions: ChatSession[]) => {
    if (typeof window === 'undefined') return;
    
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

  if (!isMounted) {
    return null;
  }

  return (
    <>
      {/* Mobile backdrop when sidebar is open */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm z-40 md:hidden"
          onClick={onClose}
        />
      )}
      
       <div className="w-80 sessions-sidebar flex flex-col h-full transition-all duration-300" style={{
         position: 'absolute',
         left: isOpen ? '0' : '-320px',
         top: 0,
         zIndex: 30,
         background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 50%, rgba(255, 255, 255, 0.1) 100%)',
         borderRight: '1px solid rgba(255, 255, 255, 0.2)',
         backdropFilter: 'blur(20px)',
         boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)'
       }}>
         {/* Header */}
         <div style={{
           padding: '16px',
           borderBottom: '1px solid rgba(255, 255, 255, 0.2)',
           backgroundColor: 'rgba(255, 255, 255, 0.05)',
           backdropFilter: 'blur(20px)'
         }}>
          <div className="flex items-center justify-between">
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px'
            }}>
              {/* Space Bio Assistant Logo */}
              <div style={{
                width: '32px',
                height: '32px',
                background: 'linear-gradient(135deg, var(--color-primary), var(--color-secondary))',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                animation: 'pulse 2s infinite'
              }}>
                <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24" style={{color: 'white'}}>
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
               <h2 style={{
                 fontSize: '18px',
                 fontWeight: '600',
                 color: 'rgba(255, 255, 255, 0.95)',
                 margin: 0
               }}>Chat Sessions</h2>
            </div>
            <button
              onClick={onClose}
               style={{
                 color: 'rgba(255, 255, 255, 0.7)',
                 padding: '4px',
                 borderRadius: '4px',
                 border: 'none',
                 backgroundColor: 'transparent',
                 cursor: 'pointer',
                 transition: 'all 0.2s ease'
               }}
               onMouseEnter={(e) => {
                 e.currentTarget.style.color = 'rgba(255, 255, 255, 0.95)';
                 e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.1)';
               }}
               onMouseLeave={(e) => {
                 e.currentTarget.style.color = 'rgba(255, 255, 255, 0.7)';
                 e.currentTarget.style.backgroundColor = 'transparent';
               }}
              title="Close sidebar"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          {/* New Chat Button */}
          <button
            onClick={onNewSession}
            style={{
              width: '100%',
              marginTop: '16px',
              padding: '8px 16px',
              backgroundColor: 'var(--color-primary)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px',
              fontSize: '14px',
              fontWeight: '500',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(62, 142, 222, 0.9)'}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'var(--color-primary)'}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            New Chat
          </button>
        </div>

        {/* Sessions List */}
        <div style={{
          flex: 1,
          overflowY: 'auto',
          scrollbarWidth: 'none',
          msOverflowStyle: 'none'
        }}>
          {sessions.length === 0 ? (
             <div style={{
               padding: '32px 16px',
               textAlign: 'center',
               color: 'rgba(255, 255, 255, 0.7)'
             }}>
              <svg className="w-12 h-12 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" style={{color: 'rgba(255, 255, 255, 0.7)'}}>
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              <p style={{fontSize: '14px', margin: 0}}>No chat sessions yet</p>
              <p style={{fontSize: '12px', margin: '4px 0 0 0', opacity: 0.8}}>Start a new conversation to see it here</p>
            </div>
          ) : (
            <div style={{padding: '8px'}}>
              {sessions.map((session) => (
                <div
                  key={session.id}
                  style={{
                    position: 'relative',
                    padding: '12px',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    marginBottom: '8px',
                    backgroundColor: session.id === currentSessionId 
                      ? 'rgba(62, 142, 222, 0.2)' 
                      : 'transparent',
                    border: session.id === currentSessionId 
                      ? '1px solid rgba(62, 142, 222, 0.3)' 
                      : '1px solid transparent'
                  }}
                  onMouseEnter={(e) => {
                    if (session.id !== currentSessionId) {
                      e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.1)';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (session.id !== currentSessionId) {
                      e.currentTarget.style.backgroundColor = 'transparent';
                    }
                  }}
                  onClick={() => onSessionSelect(session.id)}
                >
                  <div style={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    justifyContent: 'space-between'
                  }}>
                    <div style={{
                      flex: 1,
                      minWidth: 0
                    }}>
                       <h3 style={{
                         fontSize: '14px',
                         fontWeight: '500',
                         color: 'rgba(255, 255, 255, 0.95)',
                         margin: 0,
                         overflow: 'hidden',
                         textOverflow: 'ellipsis',
                         whiteSpace: 'nowrap'
                       }}>
                        {session.title}
                      </h3>
                      {session.lastMessage && (
                        <p style={{
                          fontSize: '12px',
                          color: 'rgba(255, 255, 255, 0.7)',
                          margin: '4px 0 0 0',
                          display: '-webkit-box',
                          WebkitLineClamp: 2,
                          WebkitBoxOrient: 'vertical',
                          overflow: 'hidden'
                        }}>
                          {session.lastMessage}
                        </p>
                      )}
                      <p style={{
                        fontSize: '11px',
                        color: 'rgba(255, 255, 255, 0.6)',
                        margin: '4px 0 0 0'
                      }}>
                        {session.timestamp.toLocaleDateString()} at {session.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </p>
                    </div>
                    
                    {/* Delete Button */}
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteSession(session.id);
                      }}
                       style={{
                         opacity: 0,
                         marginLeft: '8px',
                         padding: '4px',
                         color: 'rgba(255, 255, 255, 0.7)',
                         backgroundColor: 'transparent',
                         border: 'none',
                         borderRadius: '4px',
                         cursor: 'pointer',
                         transition: 'all 0.2s ease'
                       }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.opacity = '1';
                        e.currentTarget.style.color = '#EF4444';
                        e.currentTarget.style.backgroundColor = 'rgba(239, 68, 68, 0.1)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.opacity = '0';
                        e.currentTarget.style.color = 'rgba(255, 255, 255, 0.7)';
                        e.currentTarget.style.backgroundColor = 'transparent';
                      }}
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
         <div style={{
           padding: '16px',
           borderTop: '1px solid rgba(255, 255, 255, 0.2)',
           backgroundColor: 'rgba(255, 255, 255, 0.05)',
           backdropFilter: 'blur(20px)'
         }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            fontSize: '12px',
            color: 'rgba(255, 255, 255, 0.7)'
          }}>
            <div style={{
              width: '16px',
              height: '16px',
              background: 'linear-gradient(135deg, var(--color-primary), var(--color-secondary))',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <svg width="8" height="8" fill="none" stroke="currentColor" viewBox="0 0 24 24" style={{color: 'white'}}>
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            AstroBio Explorer
          </div>
        </div>
      </div>
    </>
  );
}
