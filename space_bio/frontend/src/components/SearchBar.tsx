'use client';

import { useState } from 'react';

interface SearchBarProps {
  onSubmit: (query: string) => void;
  isLoading?: boolean;
  placeholder?: string;
}

/**
 * SearchBar component with controlled input and submit functionality
 * Handles search query input and submission
 */
export default function SearchBar({ 
  onSubmit, 
  isLoading = false, 
  placeholder = "Search space biology research..." 
}: SearchBarProps) {
  const [query, setQuery] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !isLoading) {
      onSubmit(query.trim());
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{
      width: '100%',
      maxWidth: '800px',
      margin: '0 auto'
    }}>
      <div style={{position: 'relative'}}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={isLoading}
          className="search-input"
          style={{
            width: '100%',
            padding: '12px 48px 12px 16px',
            backgroundColor: 'var(--color-surface)',
            border: '1px solid rgba(30, 33, 51, 0.2)',
            borderRadius: '12px',
            color: 'var(--color-text-primary)',
            fontSize: '14px',
            outline: 'none',
            opacity: isLoading ? 0.5 : 1,
            cursor: isLoading ? 'not-allowed' : 'text',
            transition: 'all 0.2s ease'
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
        <button
          type="submit"
          disabled={!query.trim() || isLoading}
          style={{
            position: 'absolute',
            right: '8px',
            top: '50%',
            transform: 'translateY(-50%)',
            padding: '8px 12px',
            backgroundColor: 'var(--color-primary)',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            fontSize: '14px',
            cursor: (!query.trim() || isLoading) ? 'not-allowed' : 'pointer',
            opacity: (!query.trim() || isLoading) ? 0.5 : 1,
            transition: 'all 0.2s ease'
          }}
          onMouseEnter={(e) => {
            if (!(!query.trim() || isLoading)) {
              e.currentTarget.style.backgroundColor = 'rgba(62, 142, 222, 0.9)';
            }
          }}
          onMouseLeave={(e) => {
            if (!(!query.trim() || isLoading)) {
              e.currentTarget.style.backgroundColor = 'var(--color-primary)';
            }
          }}
        >
          {isLoading ? (
            <>
              <div style={{
                width: '12px',
                height: '12px',
                border: '2px solid rgba(255, 255, 255, 0.3)',
                borderTop: '2px solid white',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite'
              }} />
              <span>Searching...</span>
            </>
          ) : (
            <>
              <svg width="12" height="12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
