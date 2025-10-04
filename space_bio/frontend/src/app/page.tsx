'use client';

import { useState, useRef, useEffect } from 'react';
import SearchBar from '@/components/SearchBar';
import ChatAnswer from '@/components/ChatAnswer';
import ContextChips from '@/components/ContextChips';
import SourcesDrawer from '@/components/SourcesDrawer';
import { postJSON, getJSON } from '@/lib/api';
import { SearchResponse, AnswerPayload, ThreadResponse } from '@/lib/types';

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
  const [threadId, setThreadId] = useState<string | null>(() => {
    // Restore threadId from localStorage on page load
    if (typeof window !== 'undefined') {
      return localStorage.getItem('space_bio_thread_id') || null;
    }
    return null;
  });
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  // Load messages when threadId changes (on page load or new thread)
  useEffect(() => {
    if (threadId) {
      loadThreadMessages(threadId);
    }
  }, [threadId]);

  // Function to load messages from a thread
  const loadThreadMessages = async (threadId: string) => {
    try {
      const response = await getJSON<ThreadResponse>(`/api/thread/${threadId}`);
      if (response.messages) {
        const chatMessages: ChatMessage[] = response.messages.map((msg: any) => ({
          id: msg.id || Date.now().toString(),
          type: msg.role === 'user' ? 'user' : 'assistant',
          content: msg.role === 'user' ? msg.text : msg.answer,
          timestamp: new Date(msg.created_at || Date.now()),
          answer: msg.role === 'assistant' ? msg.answer : undefined
        }));
        setMessages(chatMessages);
      }
    } catch (error) {
      console.error('Failed to load thread messages:', error);
      // If thread doesn't exist, clear the threadId
      localStorage.removeItem('space_bio_thread_id');
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
      let currentThreadId = threadId;

      // Step 1: Create thread if it doesn't exist
      if (!currentThreadId) {
        console.log('Creating new thread...');
        const threadPayload = { seed_context: {} };
        console.log('POST /api/thread payload:', threadPayload);
        
            const threadResponse = await postJSON<{ thread_id: string }>('/api/thread', threadPayload);
            currentThreadId = threadResponse.thread_id;
            setThreadId(currentThreadId);
            // Save threadId to localStorage for persistence
            localStorage.setItem('space_bio_thread_id', currentThreadId);
            console.log('Thread created:', currentThreadId);
      }

      // Step 2: POST to /api/search
      const searchPayload = {
        q: query,
        filters: {},
        limit: 10,
        offset: 0,
        thread_id: currentThreadId
      };
      console.log('POST /api/search payload:', searchPayload);
      
      const searchResponse = await postJSON<SearchResponse>('/api/search', searchPayload);
      console.log('Search response:', searchResponse);

      // Step 3: POST to /api/answer
      const answerPayload = {
        q: query,
        thread_id: currentThreadId,
        k: 8,
        max_tokens: 800
      };
      console.log('POST /api/answer payload:', answerPayload);
      
      const answerResponse = await postJSON<AnswerPayload>('/api/answer', answerPayload);
      console.log('Answer response:', answerResponse);

      // Add assistant message
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: answerResponse.answer,
        timestamp: new Date(),
        answer: answerResponse
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
    localStorage.removeItem('space_bio_thread_id');
    setThreadId(null);
    setMessages([]);
    setContext({ organism: undefined, conditions: [] });
    setError(null);
  };

  // Get unique paper IDs for sources drawer from all messages
  const allPaperIds = messages
    .filter(msg => msg.answer?.citations)
    .flatMap(msg => msg.answer!.citations.map(citation => citation.id));
  const uniquePaperIds = [...new Set(allPaperIds)];

  return (
    <div className="chat-container" style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100vh',
      maxWidth: '1200px',
      margin: '0 auto',
      backgroundColor: 'var(--color-bg)',
      color: 'var(--color-text-primary)'
    }}>
      {/* Chat Header */}
      <div className="chat-header" style={{
        flexShrink: 0,
        padding: '16px',
        borderBottom: '1px solid rgba(30, 33, 51, 0.2)',
        backgroundColor: 'rgba(30, 33, 51, 0.3)',
        backdropFilter: 'blur(10px)'
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
                <div>
                  <h1 style={{
                    fontSize: '18px',
                    fontWeight: '600',
                    margin: 0,
                    color: 'var(--color-text-primary)'
                  }}>Space Bio Assistant</h1>
                  <p style={{
                    fontSize: '12px',
                    margin: 0,
                    color: 'var(--color-text-secondary)'
                  }}>AI research companion</p>
                </div>
              </div>
              
              {/* New Chat Button */}
              <button
                onClick={handleNewChat}
                style={{
                  padding: '8px 12px',
                  backgroundColor: 'rgba(62, 142, 222, 0.2)',
                  color: 'var(--color-primary)',
                  border: '1px solid rgba(62, 142, 222, 0.3)',
                  borderRadius: '8px',
                  fontSize: '12px',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = 'rgba(62, 142, 222, 0.3)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'rgba(62, 142, 222, 0.2)';
                }}
              >
                <svg width="12" height="12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                New Chat
              </button>
            </div>
        
        {/* Thread ID Debug Info */}
        {threadId && (
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
        padding: '16px',
        display: 'flex',
        flexDirection: 'column',
        gap: '16px'
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
              }}>Welcome to Space Bio Assistant</h2>
              <p style={{
                fontSize: '14px',
                margin: 0,
                color: 'var(--color-text-secondary)',
                maxWidth: '320px',
                margin: '0 auto'
              }}>
                Ask me anything about space biology research. I can help you find papers, 
                analyze data, and explore scientific insights.
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
              maxWidth: '80%',
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
                }}>{message.content}</p>
                
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
                  }}>Searching space biology literature...</span>
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
      <div className="chat-input" style={{
        flexShrink: 0,
        padding: '16px',
        borderTop: '1px solid rgba(30, 33, 51, 0.2)',
        backgroundColor: 'rgba(30, 33, 51, 0.3)',
        backdropFilter: 'blur(10px)'
      }}>
        <SearchBar 
          onSubmit={handleSearch}
          isLoading={isLoading}
          placeholder="Ask about space biology research..."
        />
      </div>

      {/* Sources Drawer */}
      <SourcesDrawer paperIds={uniquePaperIds} />
    </div>
  );
}
