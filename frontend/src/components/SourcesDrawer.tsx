'use client';

import { useState, useEffect } from 'react';
import { getJSON } from '@/lib/api';

interface PaperSnippet {
  section: string;
  snippet: string;
  score: number;
}

interface PaperData {
  paper_id: string;
  title: string;
  year: number;
  snippets: PaperSnippet[];
}

interface SourcesDrawerProps {
  paperIds: string[];
}

/**
 * SourcesDrawer component displays a toggleable drawer with paper sources and snippets
 * Fetches paper data and snippets from the API
 */
export default function SourcesDrawer({ paperIds }: SourcesDrawerProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [papers, setPapers] = useState<PaperData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch paper data and snippets when drawer opens
  useEffect(() => {
    if (isOpen && paperIds.length > 0 && papers.length === 0) {
      fetchPapers();
    }
  }, [isOpen, paperIds]);

  const fetchPapers = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const paperPromises = paperIds.map(async (paperId) => {
        try {
          const data = await getJSON<PaperData>(`/api/papers/${paperId}/snippets`);
          return data;
        } catch (err) {
          console.error(`Failed to fetch paper ${paperId}:`, err);
          return {
            paper_id: paperId,
            title: 'Failed to load',
            year: 0,
            snippets: []
          };
        }
      });

      const paperData = await Promise.all(paperPromises);
      setPapers(paperData);
    } catch (err) {
      setError('Failed to load paper sources');
      console.error('Error fetching papers:', err);
    } finally {
      setLoading(false);
    }
  };

  const toggleDrawer = () => {
    setIsOpen(!isOpen);
  };

  if (paperIds.length === 0) {
    return null;
  }

  return (
    <>
      {/* Toggle Button */}
      <button
        onClick={toggleDrawer}
        className="fixed bottom-4 right-4 bg-primary text-white px-3 py-2 rounded-full shadow-lg
                   hover:bg-primary/90 transition-colors duration-200
                   flex items-center space-x-1 z-40"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
        </svg>
        <span className="text-sm">Sources ({paperIds.length})</span>
      </button>

      {/* Drawer Overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-50"
          onClick={toggleDrawer}
        />
      )}

      {/* Drawer Panel */}
      <div className={`fixed right-0 top-0 h-full w-96 bg-surface border-l border-surface/20 z-50
                       transform transition-transform duration-300 ease-in-out
                       ${isOpen ? 'translate-x-0' : 'translate-x-full'}`}>
        
        {/* Drawer Header */}
        <div className="flex items-center justify-between p-4 border-b border-surface/20">
          <h2 className="text-lg font-semibold text-text-primary">Sources</h2>
          <button
            onClick={toggleDrawer}
            className="p-2 hover:bg-surface/50 rounded-lg transition-colors"
          >
            <svg className="w-5 h-5 text-text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Drawer Content */}
        <div className="flex-1 overflow-y-auto p-4">
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <div className="w-8 h-8 border-2 border-primary/30 border-t-primary rounded-full animate-spin" />
              <span className="ml-3 text-text-secondary">Loading sources...</span>
            </div>
          ) : error ? (
            <div className="text-center py-8">
              <p className="text-text-secondary mb-4">{error}</p>
              <button
                onClick={fetchPapers}
                className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
              >
                Retry
              </button>
            </div>
          ) : (
            <div className="space-y-6">
              {papers.map((paper) => (
                <div key={paper.paper_id} className="border border-surface/20 rounded-lg p-4">
                  {/* Paper Header */}
                  <div className="mb-4">
                    <h3 className="font-medium text-text-primary mb-2 line-clamp-2">
                      {paper.title}
                    </h3>
                    <div className="flex items-center space-x-4 text-sm text-text-secondary">
                      <span>ID: {paper.paper_id}</span>
                      {paper.year > 0 && <span>{paper.year}</span>}
                    </div>
                  </div>

                  {/* Snippets */}
                  {paper.snippets.length > 0 ? (
                    <div className="space-y-3">
                      <h4 className="text-sm font-medium text-text-secondary">Relevant Sections:</h4>
                      {paper.snippets.map((snippet, index) => (
                        <div key={index} className="bg-bg/50 rounded-lg p-3 border border-surface/10">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-xs font-medium text-primary bg-primary/20 px-2 py-1 rounded">
                              {snippet.section}
                            </span>
                            <span className="text-xs text-text-secondary">
                              {Math.round(snippet.score * 100)}% match
                            </span>
                          </div>
                          <p className="text-sm text-text-primary leading-relaxed">
                            {snippet.snippet}
                          </p>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-text-secondary italic">
                      No snippets available for this paper.
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
