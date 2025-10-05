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
  citation?: {
    id: string;
    url: string;
    why_relevant: string;
  };
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
  const [activeTab, setActiveTab] = useState<string | null>(null);
  const [openTabs, setOpenTabs] = useState<PaperData[]>([]);

  const openPaperInNewTab = (citation: any) => {
    // Create paper data from citation
    const paperData: PaperData = {
      paper_id: citation.id,
      title: `Research Paper ${citation.id}`,
      year: 2023,
      snippets: [
        {
          section: 'Abstract',
          snippet: citation.why_relevant || 'This paper discusses important findings in space biology research.',
          score: 0.85
        }
      ],
      citation: citation
    };

    // Check if tab is already open
    const existingTab = openTabs.find(tab => tab.paper_id === citation.id);
    if (!existingTab) {
      setOpenTabs(prev => [...prev, paperData]);
    }
    
    // Set as active tab and open drawer
    setActiveTab(citation.id);
    setIsOpen(true);
  };

  const closeTab = (paperId: string) => {
    setOpenTabs(prev => prev.filter(tab => tab.paper_id !== paperId));
    if (activeTab === paperId) {
      const remainingTabs = openTabs.filter(tab => tab.paper_id !== paperId);
      setActiveTab(remainingTabs.length > 0 ? remainingTabs[0].paper_id : null);
    }
  };

  // Fetch paper data and snippets when drawer opens
  useEffect(() => {
    if (isOpen && paperIds.length > 0 && papers.length === 0) {
      fetchPapers();
    }
  }, [isOpen, paperIds]);

  // Listen for paper open events
  useEffect(() => {
    const handleOpenPaper = (event: CustomEvent) => {
      console.log('Paper open event received:', event.detail);
      const { citation } = event.detail;
      openPaperInNewTab(citation);
    };

    window.addEventListener('openPaperInSidebar', handleOpenPaper as EventListener);
    return () => {
      window.removeEventListener('openPaperInSidebar', handleOpenPaper as EventListener);
    };
  }, []);

  const fetchPapers = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Since we don't have paper detail endpoints, create mock data from paper IDs
      const paperData = paperIds.map((paperId) => ({
        paper_id: paperId,
        title: `Research Paper ${paperId.split(':')[0] || paperId}`,
        year: 2023,
        snippets: [
          {
            section: 'Abstract',
            snippet: 'This paper discusses important findings in space biology research.',
            score: 0.85
          }
        ]
      }));

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
                   flex items-center space-x-1 z-40
                   text-sm sm:text-base"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
        </svg>
        <span className="text-sm">
          Sources {openTabs.length > 0 ? `(${openTabs.length})` : `(${paperIds.length})`}
        </span>
      </button>

      {/* Drawer Overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-50"
          onClick={toggleDrawer}
        />
      )}

      {/* Drawer Panel */}
      <div className={`fixed right-0 top-0 h-full w-full sm:w-96 bg-surface border-l border-surface/20 z-50
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

        {/* Tab Navigation */}
        {openTabs.length > 0 && (
          <div className="flex border-b border-surface/20 overflow-x-auto">
            {openTabs.map((tab) => (
              <div
                key={tab.paper_id}
                className={`flex items-center px-4 py-2 border-b-2 cursor-pointer transition-colors
                           ${activeTab === tab.paper_id 
                             ? 'border-primary text-primary bg-primary/10' 
                             : 'border-transparent text-text-secondary hover:text-text-primary hover:bg-surface/50'}`}
                onClick={() => setActiveTab(tab.paper_id)}
              >
                <span className="text-sm font-medium truncate max-w-32">
                  {tab.paper_id}
                </span>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    closeTab(tab.paper_id);
                  }}
                  className="ml-2 p-1 hover:bg-surface/50 rounded transition-colors"
                >
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Drawer Content */}
        <div className="flex-1 overflow-y-auto p-4">
          {activeTab && openTabs.length > 0 ? (
            // Show active tab content
            (() => {
              const activePaper = openTabs.find(tab => tab.paper_id === activeTab);
              if (!activePaper) return null;
              
              return (
                <div className="space-y-4">
                  {/* Paper Header */}
                  <div className="border-b border-surface/20 pb-4">
                    <h3 className="font-medium text-text-primary mb-2">
                      {activePaper.title}
                    </h3>
                    <div className="flex items-center space-x-4 text-sm text-text-secondary mb-3">
                      <span>ID: {activePaper.paper_id}</span>
                      {activePaper.year > 0 && <span>{activePaper.year}</span>}
                    </div>
                    
                  </div>

                  {/* Paper Content in iframe */}
                  {activePaper.citation && (
                    <div className="space-y-4">
                      <h4 className="text-sm font-medium text-text-secondary">Paper Content:</h4>
                      <div className="border border-surface/20 rounded-lg overflow-hidden">
                        <iframe
                          src={activePaper.citation.url}
                          className="w-full h-96 border-0"
                          title={`Paper: ${activePaper.paper_id}`}
                          sandbox="allow-same-origin allow-scripts allow-popups allow-forms"
                          loading="lazy"
                          onError={(e) => {
                            console.log('Iframe failed to load:', e);
                            // Fallback content if iframe fails
                            e.currentTarget.style.display = 'none';
                            const fallback = document.createElement('div');
                            fallback.className = 'p-4 text-center text-text-secondary';
                            fallback.innerHTML = `
                              <p>Unable to load paper content due to security restrictions.</p>
                              <a href="${activePaper.citation.url}" target="_blank" class="text-primary underline">Open in new tab</a>
                            `;
                            e.currentTarget.parentNode.appendChild(fallback);
                          }}
                        />
                      </div>
                    </div>
                  )}

                </div>
              );
            })()
          ) : (
            // Show default content when no tabs are open
            <div className="text-center py-8">
              <div className="w-16 h-16 bg-primary/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-text-primary mb-2">Sources</h3>
              <p className="text-text-secondary text-sm">
                Click on source links in the chat to view paper details here.
              </p>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
