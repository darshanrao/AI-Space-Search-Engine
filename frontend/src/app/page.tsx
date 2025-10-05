'use client';

import { useState, useRef, useEffect } from 'react';
import SearchBar from '@/components/SearchBar';
import ChatAnswer from '@/components/ChatAnswer';
import ContextChips from '@/components/ContextChips';
import SessionsSidebar from '@/components/SessionsSidebar';
import { postJSON } from '@/lib/api';
import { AnswerPayload } from '@/lib/types';

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

interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  answer?: AnswerPayload;
}

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [context, setContext] = useState<{ organism?: string; conditions: string[] }>({
    conditions: []
  });
  const [threadId, setThreadId] = useState<string | null>(null);
  const [isClient, setIsClient] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isMounted, setIsMounted] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);


  const renderAnswerWithCitations = (text: string, citations: (string | {url: string})[] = []) => {
    // Regular expression to match citation patterns like [1], [2], [1, 2], [1-3], etc.
    const citationRegex = /\[(\d+(?:[-,]\d+)*)\]/g;
    
    // Debug: Log citations array
    console.log('Citations array:', citations);
    console.log('Citations length:', citations.length);
    console.log('Citations structure:', citations.map((c, i) => ({ index: i, type: typeof c, value: c })));
    
    const parts = [];
    let lastIndex = 0;
    let match: RegExpExecArray | null;

    while ((match = citationRegex.exec(text)) !== null) {
      // Add text before the citation
      if (match.index > lastIndex) {
        parts.push(text.slice(lastIndex, match.index));
      }

      // Add the clickable citation
      const citationNumbers = match[1].split(',').map(num => num.trim());
      
      // Expand ranges like "1-3" to ["1", "2", "3"]
      const expandedNumbers = [];
      for (const num of citationNumbers) {
        if (num.includes('-')) {
          const [start, end] = num.split('-').map(n => parseInt(n.trim()));
          for (let i = start; i <= end; i++) {
            expandedNumbers.push(i.toString());
          }
        } else {
          expandedNumbers.push(num);
        }
      }
      
      // Handle multiple citations by creating individual clickable buttons
      if (expandedNumbers.length > 1) {
        // Multiple citations like [1, 2, 3] or [1-3] - create separate buttons
        expandedNumbers.forEach((num, index) => {
          const citationNumber = parseInt(num);
          const citationIndex = citationNumber - 1; // Convert to 0-based index
          
          // Safety check: ensure citation index is within bounds
          if (citationIndex >= 0 && citationIndex < citations.length) {
            const citationObj = citations[citationIndex];
            const url = typeof citationObj === 'string' ? citationObj : citationObj?.url;
            
            // Debug: Log citation mapping
            console.log(`Citation ${citationNumber} -> Index ${citationIndex} -> Citation Object:`, citationObj);
            console.log(`Citation ${citationNumber} -> URL:`, url);
            
            parts.push(
              <button
                key={`${match!.index}-${index}`}
                onClick={() => {
                  if (url) {
                    window.open(url, '_blank', 'noopener,noreferrer');
                  }
                }}
                className="inline-block mx-0.5 px-1 py-0.5 bg-blue-500/20 text-blue-400 hover:bg-blue-500/30 hover:text-blue-300 rounded text-xs font-medium transition-colors cursor-pointer"
                title={url ? `Open source ${citationNumber}` : `Source ${citationNumber} not available`}
                disabled={!url}
              >
                [{citationNumber}]
              </button>
            );
          } else {
            // Debug: Log out of bounds citation
            console.log(`Citation ${citationNumber} -> Index ${citationIndex} is out of bounds (citations.length: ${citations.length})`);
            
            // Still show the citation but make it non-clickable
            parts.push(
              <span
                key={`${match!.index}-${index}`}
                className="inline-block mx-0.5 px-1 py-0.5 bg-gray-500/20 text-gray-400 rounded text-xs font-medium"
                title={`Source ${citationNumber} not available`}
              >
                [{citationNumber}]
              </span>
            );
          }
        });
      } else {
        // Single citation like [1] or range like [1-3]
        const citationText = match[1];
        const firstNumber = parseInt(expandedNumbers[0]);
        const citationIndex = firstNumber - 1; // Convert to 0-based index
        
        // Safety check: ensure citation index is within bounds
        if (citationIndex >= 0 && citationIndex < citations.length) {
          const citationObj = citations[citationIndex];
          const url = typeof citationObj === 'string' ? citationObj : citationObj?.url;
          
          // Debug: Log citation mapping
          console.log(`Citation ${citationText} -> Index ${citationIndex} -> Citation Object:`, citationObj);
          console.log(`Citation ${citationText} -> URL:`, url);
          
          parts.push(
            <button
              key={match.index}
              onClick={() => {
                if (url) {
                  window.open(url, '_blank', 'noopener,noreferrer');
                }
              }}
              className="inline-block mx-1 px-1 py-0.5 bg-blue-500/20 text-blue-400 hover:bg-blue-500/30 hover:text-blue-300 rounded text-xs font-medium transition-colors cursor-pointer"
              title={url ? `Open source ${citationText}` : `Source ${citationText} not available`}
              disabled={!url}
            >
              [{citationText}]
            </button>
          );
        } else {
          // Debug: Log out of bounds citation
          console.log(`Citation ${citationText} -> Index ${citationIndex} is out of bounds (citations.length: ${citations.length})`);
          
          // Still show the citation but make it non-clickable
          parts.push(
            <span
              key={match.index}
              className="inline-block mx-1 px-1 py-0.5 bg-gray-500/20 text-gray-400 rounded text-xs font-medium"
              title={`Source ${citationText} not available`}
            >
              [{citationText}]
            </span>
          );
        }
      }

      lastIndex = match.index + match[0].length;
    }

    // Add remaining text
    if (lastIndex < text.length) {
      parts.push(text.slice(lastIndex));
    }

    return parts.length > 0 ? parts : text;
  };

  // Initialize client-side state
  useEffect(() => {
    setIsClient(true);
    setIsMounted(true);
    // Restore threadId from localStorage on page load
    if (typeof window !== 'undefined') {
      const savedThreadId = localStorage.getItem('space_bio_thread_id');
      if (savedThreadId) {
        setThreadId(savedThreadId);
      }
    }
  }, []);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  // Load messages when threadId changes (on page load or new thread)
  useEffect(() => {
    if (threadId && isMounted) {
      loadThreadMessages(threadId);
    }
  }, [threadId, isMounted]);

  // Function to load messages from a session
  const loadThreadMessages = async (sessionId: string) => {
    try {
      // Use fetch directly to handle 404 gracefully
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}/api/session/${sessionId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.status === 404) {
        // Session doesn't exist on backend (probably server was restarted)
        console.log(`Session ${sessionId} not found on backend, clearing from localStorage`);
        if (typeof window !== 'undefined') {
          localStorage.removeItem('space_bio_thread_id');
        }
        setThreadId(null);
        
        // Show a brief notification to the user
        setMessages([{
          id: 'session-not-found',
          type: 'assistant',
          content: 'The previous session was not found (it may have expired). Starting a new conversation.',
          timestamp: new Date()
        }]);
        return;
      }

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.messages) {
        const chatMessages: ChatMessage[] = data.messages.map((msg: {role: string, content: string, rag_response?: {answer_markdown: string, citations: unknown[], image_citations: unknown[], image_urls: string[], used_context_ids: string[], confident: boolean, confidence_score?: number}, timestamp: string}, index: number) => ({
          id: `${sessionId}-${index}`,
          type: msg.role === 'user' ? 'user' : 'assistant',
          content: msg.content,
          timestamp: new Date(msg.timestamp),
          answer: msg.role === 'assistant' && msg.rag_response ? {
            answer: msg.rag_response.answer_markdown,
            citations: msg.rag_response.citations,
            image_citations: msg.rag_response.image_citations,
            image_urls: msg.rag_response.image_urls,
            context_ids: msg.rag_response.used_context_ids,
            confident: msg.rag_response.confident,
            confidence_score: msg.rag_response.confidence_score
          } : undefined
        }));
        setMessages(chatMessages);
      }
    } catch (error) {
      console.error('Failed to load session messages:', error);
      if (typeof window !== 'undefined') {
        localStorage.removeItem('space_bio_thread_id');
      }
      setThreadId(null);
    }
  };

  // Handle search submission
  const handleSearch = async (query: string) => {
    setIsLoading(true);
    setError(null);

    // Add user message
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: query,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);

    try {
      // Single API call to new RAG chat endpoint
      const chatPayload = {
        message: query,
        session_id: threadId, // Use existing threadId if available
        context: {
          organism: "C. elegans", // Default context
          focus: "space biology"
        }
      };
      
      console.log('POST /api/chat payload:', chatPayload);
      
      const chatResponse = await postJSON<{
        session_id: string;
        message: string;
        rag_response: {
          answer_markdown: string;
          citations: Array<{
            id: string;
            url: string;
            why_relevant: string;
          }>;
          image_citations: Array<{
            id: string;
            url: string;
            why_relevant: string;
          }>;
          image_urls: string[];
          used_context_ids: string[];
          confident: boolean;
          confidence_score?: number;
        };
        context: unknown;
        timestamp: string;
      }>('/api/chat', chatPayload);
      
      console.log('Chat response:', chatResponse);

      // Update threadId if this is a new session
      if (!threadId) {
        setThreadId(chatResponse.session_id);
        if (typeof window !== 'undefined') {
          localStorage.setItem('space_bio_thread_id', chatResponse.session_id);
        }
        console.log('New session created:', chatResponse.session_id);
        
        // Add new session to sidebar
        if (window.sessionsSidebar) {
          const title = window.sessionsSidebar.generateTitle(query);
          window.sessionsSidebar.addSession(chatResponse.session_id, title, query);
        }
      } else {
        // Update existing session with new message
        if (window.sessionsSidebar) {
          const title = window.sessionsSidebar.generateTitle(query);
          window.sessionsSidebar.updateSession(threadId, title, query);
        }
      }

      // Add assistant message with RAG response
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: chatResponse.message,
        timestamp: new Date(),
        answer: {
          answer: chatResponse.message,
          citations: chatResponse.rag_response?.citations || [],
          image_citations: chatResponse.rag_response?.image_citations || [],
          image_urls: chatResponse.rag_response?.image_urls || [],
          context_ids: chatResponse.rag_response?.used_context_ids || [],
          confident: chatResponse.rag_response?.confident || false,
          confidence_score: chatResponse.rag_response?.confidence_score
        }
      };
      setMessages(prev => [...prev, assistantMessage]);

    } catch (err) {
      console.error('Search failed:', err);
      setError('Failed to search. Please try again.');
      
      // Add error message
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: 'Sorry, I encountered an error while searching. Please try again.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle context updates
  const handleContextUpdate = (newContext: { organism?: string; conditions: string[] }) => {
    setContext(newContext);
  };

  // Handle starting a new chat
  const handleNewChat = () => {
    // Clear current session
    if (typeof window !== 'undefined') {
      localStorage.removeItem('space_bio_thread_id');
    }
    setThreadId(null);
    setMessages([]);
    setContext({ organism: undefined, conditions: [] });
    setError(null);
    setIsLoading(false); // IMPORTANT: Clear loading state to prevent cross-context generation
  };

  // Handle session selection
  const handleSessionSelect = (sessionId: string) => {
    setThreadId(sessionId);
    if (typeof window !== 'undefined') {
      localStorage.setItem('space_bio_thread_id', sessionId);
    }
    setIsLoading(false); // Clear loading state when switching sessions
    setError(null); // Clear any errors when switching sessions
    // Messages will be loaded by the useEffect that watches threadId
  };



  return (
    <div style={{
      height: '100vh',
      color: 'var(--color-text-primary)',
      position: 'relative'
    }}>
      {/* Sessions Sidebar */}
      {isMounted && (
        <SessionsSidebar
          isOpen={isSidebarOpen}
          onClose={() => setIsSidebarOpen(false)}
          currentSessionId={threadId}
          onSessionSelect={handleSessionSelect}
          onNewSession={handleNewChat}
        />
      )}

      {/* Main Content Area */}
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        width: (isMounted && isSidebarOpen) ? 'calc(100vw - 320px)' : '100vw',
        height: '100vh',
        marginLeft: (isMounted && isSidebarOpen) ? '320px' : '0',
        padding: '0 16px',
        paddingLeft: 'max(16px, env(safe-area-inset-left))',
        paddingRight: 'max(16px, env(safe-area-inset-right))',
        transition: 'width 0.3s ease, margin-left 0.3s ease',
        minWidth: 0
      }}>
      {/* Chat Header */}
      <div style={{
        flexShrink: 0,
        padding: '16px 0',
        borderBottom: '1px solid rgba(30, 33, 51, 0.2)'
      }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              width: '100%'
            }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px'
              }}>
                {/* Sidebar Open Button - only show when sidebar is closed */}
                {isMounted && !isSidebarOpen && (
                  <button
                    onClick={() => setIsSidebarOpen(true)}
                    style={{
                      padding: '8px',
                      backgroundColor: 'rgba(30, 33, 51, 0.3)',
                      border: '1px solid rgba(30, 33, 51, 0.2)',
                      borderRadius: '8px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      cursor: 'pointer',
                      transition: 'all 0.2s ease',
                      flexShrink: 0
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(30, 33, 51, 0.5)'}
                    onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'rgba(30, 33, 51, 0.3)'}
                    title="Open sidebar"
                  >
                    <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                    </svg>
                  </button>
                )}
                
                <div>
                  <h1 style={{
                    fontSize: '18px',
                    fontWeight: '600',
                    margin: 0,
                    color: 'var(--color-text-primary)'
                  }}>AstroBio Explorer</h1>
                  <p style={{
                    fontSize: '12px',
                    margin: 0,
                    color: 'var(--color-text-secondary)'
                  }}>AI research companion</p>
                </div>
              </div>
              
            </div>
        
        {/* Thread ID Debug Info */}
        {isClient && threadId && (
          <div style={{
            marginTop: '8px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '12px'
          }}>
            <span style={{color: 'var(--color-text-secondary)'}}>Thread:</span>
            <code style={{
              backgroundColor: 'rgba(11, 13, 23, 0.5)',
              padding: '4px 6px',
              borderRadius: '4px',
              color: 'var(--color-primary)',
              fontSize: '12px'
            }}>{threadId}</code>
          </div>
        )}
      </div>

      {/* Chat Messages */}
      <div className="chat-messages" style={{
        flex: 1,
        overflowY: 'auto',
        padding: '16px 0',
        paddingLeft: 'max(0px, env(safe-area-inset-left))',
        paddingRight: 'max(0px, env(safe-area-inset-right))',
        display: 'flex',
        flexDirection: 'column',
        gap: '16px',
        maxWidth: '100%',
        width: '100%',
        scrollbarWidth: 'none', // Firefox
        msOverflowStyle: 'none' // IE/Edge
      }}>
        {messages.length === 0 && (
          <div style={{
            textAlign: 'center',
            padding: '32px 0',
            display: 'flex',
            flexDirection: 'column',
            gap: '16px',
            animation: 'fadeIn 0.5s ease-out'
          }}>
            <div style={{position: 'relative'}}>
              <div className="welcome-icon" style={{
                width: '64px',
                height: '64px',
                background: 'linear-gradient(135deg, rgba(62, 142, 222, 0.3), rgba(228, 79, 156, 0.3))',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto',
                animation: 'float 6s ease-in-out infinite'
              }}>
                <svg width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24" style={{
                  color: 'var(--color-primary)',
                  animation: 'twinkle 2s ease-in-out infinite alternate'
                }}>
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              {/* Floating particles around the icon */}
              <div style={{
                position: 'absolute',
                top: '-8px',
                left: '-8px',
                width: '8px',
                height: '8px',
                backgroundColor: 'rgba(62, 142, 222, 0.6)',
                borderRadius: '50%',
                animation: 'pulse 2s infinite',
                animationDelay: '0.5s'
              }}></div>
              <div style={{
                position: 'absolute',
                top: '-4px',
                right: '-12px',
                width: '6px',
                height: '6px',
                backgroundColor: 'rgba(228, 79, 156, 0.6)',
                borderRadius: '50%',
                animation: 'pulse 2s infinite',
                animationDelay: '1s'
              }}></div>
              <div style={{
                position: 'absolute',
                bottom: '-8px',
                right: '-4px',
                width: '4px',
                height: '4px',
                backgroundColor: 'rgba(62, 142, 222, 0.4)',
                borderRadius: '50%',
                animation: 'pulse 2s infinite',
                animationDelay: '1.5s'
              }}></div>
            </div>
            <div style={{display: 'flex', flexDirection: 'column', gap: '8px'}}>
              <h2 style={{
                fontSize: '20px',
                fontWeight: '600',
                margin: 0,
                color: 'var(--color-text-primary)'
              }}>Our AI copilot for Space Biology Research</h2>
              <p style={{
                fontSize: '14px',
                margin: '0 auto',
                color: 'var(--color-text-secondary)',
                maxWidth: '320px'
              }}>
                Search experiments, analyze findings and generate scientific insights from NASA&apos;s bioscience archives
              </p>
            </div>
          </div>
        )}

        {messages.map((message) => (
          <div key={message.id} style={{
            display: 'flex',
            justifyContent: message.type === 'user' ? 'flex-end' : 'flex-start',
            animation: 'slideUp 0.3s ease-out'
          }}>
            <div className="message-bubble" style={{
              position: 'relative',
              maxWidth: 'min(80%, 600px)',
              wordWrap: 'break-word'
            }}>
              <div style={{
                padding: '12px',
                borderRadius: '16px',
                backgroundColor: message.type === 'user' 
                  ? 'var(--color-primary)' 
                  : 'var(--color-surface)',
                color: message.type === 'user' 
                  ? 'white' 
                  : 'var(--color-text-primary)',
                border: message.type === 'user' 
                  ? 'none' 
                  : '1px solid rgba(30, 33, 51, 0.2)',
                position: 'relative'
              }}>
                {/* Chat bubble tail */}
                <div style={{
                  position: 'absolute',
                  width: 0,
                  height: 0,
                  borderStyle: 'solid',
                  ...(message.type === 'user' ? {
                    right: '-8px',
                    top: '12px',
                    borderWidth: '8px 0 8px 8px',
                    borderColor: 'transparent transparent transparent var(--color-primary)'
                  } : {
                    left: '-8px',
                    top: '12px',
                    borderWidth: '8px 8px 8px 0',
                    borderColor: 'transparent var(--color-surface) transparent transparent'
                  })
                }}></div>
                
                       <p style={{
                         fontSize: '14px',
                         lineHeight: '1.5',
                         margin: 0
                       }}>{renderAnswerWithCitations(message.content, message.answer?.citations || [])}</p>
                
                {/* Show answer details for assistant messages */}
                {message.type === 'assistant' && message.answer && (
                  <div style={{
                    marginTop: '12px',
                    paddingTop: '12px',
                    borderTop: '1px solid rgba(30, 33, 51, 0.2)'
                  }}>
                    <ChatAnswer answer={message.answer} />
                  </div>
                )}
                
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  marginTop: '8px'
                }}>
                  <span style={{
                    fontSize: '12px',
                    opacity: 0.6
                  }}>
                    {message.timestamp.toLocaleTimeString()}
                  </span>
                  {message.type === 'assistant' && (
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px'
                    }}>
                      <div style={{
                        width: '6px',
                        height: '6px',
                        backgroundColor: 'var(--color-primary)',
                        borderRadius: '50%',
                        animation: 'pulse 2s infinite'
                      }}></div>
                      <span style={{
                        fontSize: '12px',
                        opacity: 0.6
                      }}>AI</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}

        {/* Loading Message */}
        {isLoading && (
          <div style={{
            display: 'flex',
            justifyContent: 'flex-start',
            animation: 'slideUp 0.3s ease-out'
          }}>
            <div style={{
              position: 'relative',
              maxWidth: '80%',
              wordWrap: 'break-word'
            }}>
              <div style={{
                padding: '12px',
                borderRadius: '16px',
                backgroundColor: 'var(--color-surface)',
                color: 'var(--color-text-primary)',
                border: '1px solid rgba(30, 33, 51, 0.2)',
                position: 'relative'
              }}>
                {/* Chat bubble tail */}
                <div style={{
                  position: 'absolute',
                  left: '-8px',
                  top: '12px',
                  width: 0,
                  height: 0,
                  borderStyle: 'solid',
                  borderWidth: '8px 8px 8px 0',
                  borderColor: 'transparent var(--color-surface) transparent transparent'
                }}></div>
                
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  <div style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '4px'
                  }}>
                    <span style={{
                      width: '8px',
                      height: '8px',
                      borderRadius: '50%',
                      backgroundColor: 'var(--color-primary)',
                      animation: 'typing 1.4s infinite ease-in-out'
                    }}></span>
                    <span style={{
                      width: '8px',
                      height: '8px',
                      borderRadius: '50%',
                      backgroundColor: 'var(--color-primary)',
                      animation: 'typing 1.4s infinite ease-in-out',
                      animationDelay: '0.16s'
                    }}></span>
                    <span style={{
                      width: '8px',
                      height: '8px',
                      borderRadius: '50%',
                      backgroundColor: 'var(--color-primary)',
                      animation: 'typing 1.4s infinite ease-in-out',
                      animationDelay: '0.32s'
                    }}></span>
                  </div>
                  <span style={{
                    fontSize: '14px',
                    color: 'var(--color-text-secondary)'
                  }}>Generating response...</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div style={{
            display: 'flex',
            justifyContent: 'flex-start',
            animation: 'slideUp 0.3s ease-out'
          }}>
            <div style={{
              position: 'relative',
              maxWidth: '80%',
              wordWrap: 'break-word'
            }}>
              <div style={{
                padding: '12px',
                borderRadius: '16px',
                backgroundColor: 'rgba(239, 68, 68, 0.2)',
                color: '#f87171',
                border: '1px solid rgba(239, 68, 68, 0.3)',
                position: 'relative'
              }}>
                {/* Chat bubble tail */}
                <div style={{
                  position: 'absolute',
                  left: '-8px',
                  top: '12px',
                  width: 0,
                  height: 0,
                  borderStyle: 'solid',
                  borderWidth: '8px 8px 8px 0',
                  borderColor: 'transparent rgba(239, 68, 68, 0.2) transparent transparent'
                }}></div>
                
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  <svg width="12" height="12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                  </svg>
                  <span style={{fontSize: '14px'}}>{error}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Context Chips */}
      {(context.organism || context.conditions.length > 0) && (
        <div className="flex-shrink-0 px-6 pb-2">
          <ContextChips
            organism={context.organism}
            conditions={context.conditions}
            threadId={threadId || undefined}
            onUpdate={handleContextUpdate}
          />
        </div>
      )}

      {/* Search Input */}
      <div style={{
        flexShrink: 0,
        padding: '16px 0'
      }}>
        <SearchBar 
          onSubmit={handleSearch}
          isLoading={isLoading}
          placeholder="Ask about space biology experiments and research..."
        />
      </div>

      </div>
    </div>
  );
}
