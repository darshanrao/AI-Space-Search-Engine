'use client';

import { useState } from 'react';

interface SearchBarProps {
  onSubmit: (query: string) => void;
  onScholarSearch?: (query: string) => void;
  isLoading?: boolean;
  isScholarLoading?: boolean;
  isScholarDisabled?: boolean;
  placeholder?: string;
}

/**
 * SearchBar component with controlled input and submit functionality
 * Handles search query input and submission
 */
export default function SearchBar({ 
  onSubmit, 
  onScholarSearch,
  isLoading = false, 
  isScholarLoading = false,
  isScholarDisabled = false,
  placeholder = "Ask about space biology experiments and research..." 
}: SearchBarProps) {
  const [query, setQuery] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !isLoading) {
      onSubmit(query.trim());
      setQuery(''); // Clear the input after submission
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleScholarSearch = () => {
    if (!isScholarLoading && !isScholarDisabled && onScholarSearch) {
      onScholarSearch(query.trim() || ''); // Allow empty query for context-based search
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{
      width: '100%',
      maxWidth: '100%',
      margin: '0 auto'
    }}>
      <div style={{
        display: 'flex',
        gap: '12px',
        alignItems: 'stretch'
      }}>
        <div style={{flex: 1, display: 'flex', alignItems: 'stretch'}}>
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={isLoading}
            className="search-input"
            rows={1}
            style={{
              width: '100%',
              height: '44px',
              maxHeight: '120px',
              padding: '12px 16px',
              backgroundColor: 'var(--color-surface)',
              border: '1px solid rgba(30, 33, 51, 0.2)',
              borderRadius: '12px',
              color: 'var(--color-text-primary)',
              fontSize: '14px',
              outline: 'none',
              opacity: isLoading ? 0.5 : 1,
              cursor: isLoading ? 'not-allowed' : 'text',
              transition: 'all 0.2s ease',
              resize: 'none',
              overflow: 'hidden',
              fontFamily: 'inherit',
              lineHeight: '1.2',
              boxSizing: 'border-box',
              display: 'flex',
              alignItems: 'center'
            }}
            onInput={(e) => {
              // Auto-resize textarea
              const target = e.target as HTMLTextAreaElement;
              target.style.height = 'auto';
              target.style.height = Math.min(target.scrollHeight, 120) + 'px';
            }}
            onFocus={(e) => {
              e.target.style.borderColor = 'var(--color-primary)';
              e.target.style.boxShadow = '0 0 0 2px rgba(62, 142, 222, 0.2)';
            }}
            onBlur={(e) => {
              e.target.style.borderColor = 'rgba(30, 33, 51, 0.2)';
              e.target.style.boxShadow = 'none';
            }}
          />
        </div>
        {/* Google Scholar Button */}
        {onScholarSearch && (
          <button
            type="button"
            onClick={handleScholarSearch}
            disabled={isScholarLoading || isScholarDisabled}
            style={{
              padding: '0 20px',
              backgroundColor: 'var(--color-surface)',
              color: 'var(--color-text-primary)',
              border: '1px solid rgba(30, 33, 51, 0.2)',
              borderRadius: '12px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px',
              fontSize: '14px',
              fontWeight: '500',
              cursor: (isScholarLoading || isScholarDisabled) ? 'not-allowed' : 'pointer',
              opacity: (isScholarLoading || isScholarDisabled) ? 0.5 : 1,
              transition: 'all 0.2s ease',
              height: '44px',
              whiteSpace: 'nowrap',
              boxSizing: 'border-box',
              flexShrink: 0
            }}
            onMouseEnter={(e) => {
              if (!isScholarLoading && !isScholarDisabled) {
                e.currentTarget.style.backgroundColor = 'rgba(62, 142, 222, 0.1)';
                e.currentTarget.style.borderColor = 'var(--color-primary)';
                e.currentTarget.style.transform = 'translateY(-1px)';
              }
            }}
            onMouseLeave={(e) => {
              if (!isScholarLoading && !isScholarDisabled) {
                e.currentTarget.style.backgroundColor = 'var(--color-surface)';
                e.currentTarget.style.borderColor = 'rgba(30, 33, 51, 0.2)';
                e.currentTarget.style.transform = 'translateY(0)';
              }
            }}
            title="Search Google Scholar for relevant academic papers based on conversation context"
          >
            {isScholarLoading ? (
              <>
                <div style={{
                  width: '14px',
                  height: '14px',
                  border: '2px solid rgba(62, 142, 222, 0.3)',
                  borderTop: '2px solid var(--color-primary)',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite'
                }} />
                <span>Scholar...</span>
              </>
            ) : (
              <>
                <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
                <span>Scholar</span>
              </>
            )}
          </button>
        )}
        
        {/* Main Search Button */}
        <button
          type="submit"
          disabled={!query.trim() || isLoading}
          style={{
            padding: '0 20px',
            backgroundColor: 'var(--color-primary)',
            color: 'white',
            border: 'none',
            borderRadius: '12px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '6px',
            fontSize: '14px',
            fontWeight: '500',
            cursor: (!query.trim() || isLoading) ? 'not-allowed' : 'pointer',
            opacity: (!query.trim() || isLoading) ? 0.5 : 1,
            transition: 'all 0.2s ease',
            height: '44px',
            whiteSpace: 'nowrap',
            boxSizing: 'border-box',
            flexShrink: 0
          }}
          onMouseEnter={(e) => {
            if (!(!query.trim() || isLoading)) {
              e.currentTarget.style.backgroundColor = 'rgba(62, 142, 222, 0.9)';
              e.currentTarget.style.transform = 'translateY(-1px)';
            }
          }}
          onMouseLeave={(e) => {
            if (!(!query.trim() || isLoading)) {
              e.currentTarget.style.backgroundColor = 'var(--color-primary)';
              e.currentTarget.style.transform = 'translateY(0)';
            }
          }}
        >
          {isLoading ? (
            <>
              <div style={{
                width: '14px',
                height: '14px',
                border: '2px solid rgba(255, 255, 255, 0.3)',
                borderTop: '2px solid white',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite'
              }} />
              <span>Searching...</span>
            </>
          ) : (
            <>
              <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <span>Search</span>
            </>
          )}
        </button>
      </div>
    </form>
  );
}
