'use client';

import { useState } from 'react';
import { putJSON } from '@/lib/api';

interface ContextChipsProps {
  organism?: string;
  conditions: string[];
  threadId?: string;
  onUpdate: (context: { organism?: string; conditions: string[] }) => void;
}

/**
 * ContextChips component renders pinned context as removable chips
 * Handles organism and conditions with remove functionality
 */
export default function ContextChips({ 
  organism, 
  conditions, 
  threadId, 
  onUpdate 
}: ContextChipsProps) {
  const [isRemoving, setIsRemoving] = useState<string | null>(null);

  // Remove a condition from context
  const removeCondition = async (conditionToRemove: string) => {
    if (!threadId) return;
    
    setIsRemoving(conditionToRemove);
    
    try {
      const updatedConditions = conditions.filter(c => c !== conditionToRemove);
      
      // Update context via API
      await putJSON(`/api/thread/${threadId}/context`, {
        organism,
        conditions: updatedConditions
      });
      
      // Update local state
      onUpdate({
        organism,
        conditions: updatedConditions
      });
    } catch (error) {
      console.error('Failed to remove condition:', error);
    } finally {
      setIsRemoving(null);
    }
  };

  // Remove organism from context
  const removeOrganism = async () => {
    if (!threadId) return;
    
    setIsRemoving('organism');
    
    try {
      // Update context via API
      await putJSON(`/api/thread/${threadId}/context`, {
        organism: undefined,
        conditions
      });
      
      // Update local state
      onUpdate({
        organism: undefined,
        conditions
      });
    } catch (error) {
      console.error('Failed to remove organism:', error);
    } finally {
      setIsRemoving(null);
    }
  };

  // Don't render if no context
  if (!organism && conditions.length === 0) {
    return null;
  }

  return (
    <div className="mb-6">
      <h3 className="text-sm font-medium text-text-secondary mb-3">Active Context</h3>
      <div className="flex flex-wrap gap-2">
        {/* Organism Chip */}
        {organism && (
          <div className="flex items-center space-x-1 px-2 py-1 bg-primary/20 text-primary rounded-full text-xs">
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
            </svg>
            <span>{organism}</span>
            <button
              onClick={removeOrganism}
              disabled={isRemoving === 'organism'}
              className="ml-1 hover:bg-primary/30 rounded-full p-0.5 transition-colors disabled:opacity-50"
            >
              {isRemoving === 'organism' ? (
                <div className="w-2 h-2 border border-primary/50 border-t-primary rounded-full animate-spin" />
              ) : (
                <svg className="w-2 h-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              )}
            </button>
          </div>
        )}

        {/* Condition Chips */}
        {conditions.map((condition, index) => (
          <div key={index} className="flex items-center space-x-1 px-2 py-1 bg-secondary/20 text-secondary rounded-full text-xs">
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{condition}</span>
            <button
              onClick={() => removeCondition(condition)}
              disabled={isRemoving === condition}
              className="ml-1 hover:bg-secondary/30 rounded-full p-0.5 transition-colors disabled:opacity-50"
            >
              {isRemoving === condition ? (
                <div className="w-2 h-2 border border-secondary/50 border-t-secondary rounded-full animate-spin" />
              ) : (
                <svg className="w-2 h-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              )}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
