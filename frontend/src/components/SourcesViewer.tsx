'use client';

import { useState, useEffect } from 'react';

interface PaperData {
  id: string;
  url: string;
  title?: string;
  why_relevant?: string;
}

interface SourcesViewerProps {
  paperIds: string[];
}

/**
 * SourcesViewer component displays papers in a sidebar with tabbed interface
 * Shows paper content using a web viewer approach
 */
export default function SourcesViewer({ paperIds }: SourcesViewerProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<string | null>(null);
  const [openTabs, setOpenTabs] = useState<PaperData[]>([]);
  const [loading, setLoading] = useState(false);

  // Listen for paper open events
  useEffect(() => {
    const handleOpenPaper = (event: CustomEvent) => {
      const { citation } = event.detail;
      openPaperInNewTab(citation);
    };

    window.addEventListener('openPaperInSidebar', handleOpenPaper as EventListener);
    return () => {
      window.removeEventListener('openPaperInSidebar', handleOpenPaper as EventListener);
    };
  }, []);

  const openPaperInNewTab = (citation: any) => {
    const paperData: PaperData = {
      id: citation.id,
      url: citation.url,
      title: `Research Paper ${citation.id}`,
      why_relevant: citation.why_relevant
    };

    // Check if tab is already open
    const existingTab = openTabs.find(tab => tab.id === citation.id);
    if (!existingTab) {
      setOpenTabs(prev => [...prev, paperData]);
    }
    
    // Set as active tab and open drawer
    setActiveTab(citation.id);
    setIsOpen(true);
  };

  const closeTab = (paperId: string) => {
    setOpenTabs(prev => prev.filter(tab => tab.id !== paperId));
    if (activeTab === paperId) {
      const remainingTabs = openTabs.filter(tab => tab.id !== paperId);
      setActiveTab(remainingTabs.length > 0 ? remainingTabs[0].id : null);
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
      {/* Toggle Button - Only show if there are open tabs */}
      {openTabs.length > 0 && (
        <button
          onClick={toggleDrawer}
          className="fixed top-20 right-4 z-40 flex items-center gap-2 px-3 py-2 
                     bg-surface text-text-primary rounded-lg shadow-lg hover:bg-surface/80 
                     transition-all duration-200 hover:shadow-xl border border-surface/20"
          style={{
            fontSize: '12px',
            fontWeight: '500'
          }}
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
          <span className="text-xs">
            Papers
          </span>
        </button>
      )}

      {/* Drawer Overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-50"
          onClick={toggleDrawer}
        />
      )}

      {/* Drawer Panel */}
      <div className={`fixed right-0 top-0 h-full w-full sm:w-96 lg:w-[500px] xl:w-[600px] 
                        bg-surface border-l border-surface/20 z-50
                        transform transition-transform duration-300 ease-in-out
                        ${isOpen ? 'translate-x-0' : 'translate-x-full'}`}>
        
        {/* Drawer Header */}
        <div className="flex items-center justify-between p-4 border-b border-surface/20 bg-surface/80 backdrop-blur-sm">
          <h2 className="text-lg font-semibold text-text-primary">Paper Viewer</h2>
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
          <div className="flex border-b border-surface/20 overflow-x-auto bg-surface/50">
            {openTabs.map((tab) => (
              <div
                key={tab.id}
                className={`flex items-center px-4 py-2 border-b-2 cursor-pointer transition-colors min-w-0
                           ${activeTab === tab.id 
                             ? 'border-primary text-primary bg-primary/10' 
                             : 'border-transparent text-text-secondary hover:text-text-primary hover:bg-surface/50'}`}
                onClick={() => setActiveTab(tab.id)}
              >
                <span className="text-sm font-medium truncate max-w-32">
                  {tab.id}
                </span>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    closeTab(tab.id);
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
        <div className="flex-1 overflow-hidden flex flex-col">
          {activeTab ? (
            // Display content of the active tab
            openTabs.find(tab => tab.id === activeTab) ? (
              <div className="flex-1 flex flex-col">
                {/* Paper Header */}
                <div className="p-4 border-b border-surface/20 bg-surface/30">
                  <h3 className="font-medium text-text-primary mb-2 line-clamp-2">
                    {openTabs.find(tab => tab.id === activeTab)?.title}
                  </h3>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-text-secondary">ID: {activeTab}</span>
                    <a
                      href={openTabs.find(tab => tab.id === activeTab)?.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center px-3 py-1 bg-primary/20 text-primary rounded-lg
                                 hover:bg-primary/30 transition-colors text-sm"
                    >
                      <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                      </svg>
                      Open Original
                    </a>
                  </div>
                </div>

                {/* Paper Content Viewer */}
                <div className="flex-1 relative">
                  <PaperViewer 
                    url={openTabs.find(tab => tab.id === activeTab)?.url || ''}
                    paperId={activeTab}
                  />
                </div>
              </div>
            ) : null
          ) : (
            <div className="flex-1 flex items-center justify-center p-8">
              <div className="text-center">
                <div className="w-16 h-16 bg-primary/20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-text-primary mb-2">No Paper Selected</h3>
                <p className="text-text-secondary text-sm">
                  Click on a source link in the chat to view the paper here.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}

// Paper Viewer Component
function PaperViewer({ url, paperId }: { url: string; paperId: string }) {
  const [viewerType, setViewerType] = useState<'iframe' | 'pdf' | 'reader' | 'proxy' | 'external'>('iframe');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [paperContent, setPaperContent] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    
    // Check if URL is from a known academic site that blocks iframes
    const isAcademicSite = url.includes('pmc.ncbi.nlm.nih.gov') || 
                          url.includes('pubmed.ncbi.nlm.nih.gov') ||
                          url.includes('nature.com') ||
                          url.includes('science.org') ||
                          url.includes('cell.com') ||
                          url.includes('elsevier.com') ||
                          url.includes('springer.com') ||
                          url.includes('wiley.com');
    
    if (isAcademicSite) {
      console.log('Academic site detected, trying alternative viewers');
      console.log('URL:', url);
      console.log('Paper ID:', paperId);
      tryAlternativeViewers();
    } else {
      setViewerType('iframe');
      // Set a shorter timeout for non-academic sites
      const timeout = setTimeout(() => {
        if (loading) {
          console.log('Iframe loading timeout, likely blocked');
          handleIframeError();
        }
      }, 3000); // 3 second timeout
      
      return () => clearTimeout(timeout);
    }
  }, [url, loading]);

  const tryAlternativeViewers = async () => {
    console.log('Trying alternative viewers for:', url);
    
    try {
      // Try multiple CORS proxies
      const proxies = [
        `https://api.allorigins.win/get?url=${encodeURIComponent(url)}`,
        `https://cors-anywhere.herokuapp.com/${url}`,
        `https://api.codetabs.com/v1/proxy?quest=${encodeURIComponent(url)}`
      ];
      
      for (const proxyUrl of proxies) {
        try {
          console.log('Trying proxy:', proxyUrl);
          const response = await fetch(proxyUrl, {
            method: 'GET',
            headers: {
              'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            }
          });
          
          if (response.ok) {
            const data = await response.json();
            if (data.contents) {
              console.log('Successfully fetched content via proxy');
              setPaperContent(data.contents);
              setViewerType('reader');
              setLoading(false);
              return;
            }
          }
        } catch (proxyError) {
          console.log('Proxy failed:', proxyError);
          continue;
        }
      }
    } catch (error) {
      console.log('All proxies failed:', error);
    }

    // Try direct iframe with different approaches
    console.log('Trying direct iframe approach');
    setViewerType('iframe');
    setLoading(false);
  };

  const handleIframeError = () => {
    console.log('Iframe failed, trying proxy viewer');
    setViewerType('proxy');
    setLoading(false);
  };

  const handleProxyError = () => {
    console.log('Proxy failed, showing external link');
    setViewerType('external');
    setLoading(false);
  };

  return (
    <div className="h-full w-full">
      {viewerType === 'iframe' && (
        <div className="h-full w-full">
          <iframe
            src={url}
            className="w-full h-full border-0"
            title={`Paper: ${paperId}`}
            sandbox="allow-same-origin allow-scripts allow-popups allow-forms allow-downloads allow-top-navigation"
            loading="lazy"
            onLoad={() => {
              setLoading(false);
              console.log('Iframe loaded successfully');
            }}
            onError={(e) => {
              console.log('Iframe error:', e);
              handleIframeError();
            }}
            style={{
              minHeight: '100%',
              width: '100%'
            }}
          />
          {/* Fallback message if iframe is blocked */}
          <div className="absolute top-4 right-4 z-10">
            <button
              onClick={() => {
                console.log('User clicked fallback button');
                setViewerType('external');
              }}
              className="px-3 py-1 bg-red-500/20 text-red-400 rounded text-xs hover:bg-red-500/30 transition-colors"
            >
              Iframe Blocked? Click Here
            </button>
          </div>
        </div>
      )}

      {viewerType === 'proxy' && (
        <div className="h-full w-full">
          <iframe
            src={`https://cors-anywhere.herokuapp.com/${url}`}
            className="w-full h-full border-0"
            title={`Proxy: ${paperId}`}
            onLoad={() => setLoading(false)}
            onError={() => {
              console.log('Proxy failed, falling back to external');
              setViewerType('external');
            }}
          />
        </div>
      )}

      {viewerType === 'pdf' && (
        <div className="h-full w-full">
          <iframe
            src={`https://mozilla.github.io/pdf.js/web/viewer.html?file=${encodeURIComponent(url)}`}
            className="w-full h-full border-0"
            title={`PDF: ${paperId}`}
            onLoad={() => setLoading(false)}
            onError={() => {
              console.log('PDF.js failed, falling back to external');
              setViewerType('external');
            }}
          />
        </div>
      )}

      {viewerType === 'reader' && paperContent && (
        <div className="h-full w-full overflow-y-auto p-6">
          <div className="max-w-4xl mx-auto">
            <div 
              className="prose prose-invert max-w-none"
              dangerouslySetInnerHTML={{ __html: paperContent }}
              style={{
                color: 'var(--color-text-primary)',
                lineHeight: '1.6'
              }}
            />
          </div>
        </div>
      )}

      {viewerType === 'reader' && !paperContent && (
        <div className="h-full w-full flex items-center justify-center bg-surface/50">
          <div className="text-center p-8">
            <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-text-primary mb-2">Reader Mode</h3>
            <p className="text-text-secondary text-sm mb-4">
              Loading paper content in reader mode...
            </p>
            <div className="w-8 h-8 border-2 border-primary/30 border-t-primary rounded-full animate-spin mx-auto" />
          </div>
        </div>
      )}

      {viewerType === 'external' && (
        <div className="h-full w-full flex items-center justify-center bg-surface/50">
          <div className="text-center p-8 max-w-md">
            <div className="w-16 h-16 bg-blue-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-text-primary mb-2">Academic Paper</h3>
            <p className="text-text-secondary text-sm mb-4">
              This paper is hosted on an academic platform that doesn't allow direct embedding. 
              Click below to open it in a new tab for the best reading experience.
            </p>
            <div className="space-y-3">
              <a
                href={url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center px-6 py-3 bg-primary text-white rounded-lg
                           hover:bg-primary/90 transition-colors text-sm font-medium w-full justify-center"
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
                Open Paper in New Tab
              </a>
              
              <div className="grid grid-cols-2 gap-2">
                <button
                  onClick={() => {
                    setViewerType('reader');
                    setLoading(true);
                    tryAlternativeViewers();
                  }}
                  className="px-3 py-2 bg-surface text-text-primary rounded-lg
                             hover:bg-surface/80 transition-colors text-xs border border-surface/20"
                >
                  Try Reader Mode
                </button>
                <button
                  onClick={() => {
                    setViewerType('iframe');
                    setLoading(false);
                  }}
                  className="px-3 py-2 bg-surface text-text-primary rounded-lg
                             hover:bg-surface/80 transition-colors text-xs border border-surface/20"
                >
                  Try Direct View
                </button>
              </div>
              
              <div className="grid grid-cols-2 gap-2">
                <a
                  href={`https://web.archive.org/web/${url}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-3 py-2 bg-surface text-text-primary rounded-lg
                             hover:bg-surface/80 transition-colors text-xs border border-surface/20 text-center"
                >
                  Web Archive
                </a>
                <a
                  href={`https://outline.com/${url}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-3 py-2 bg-surface text-text-primary rounded-lg
                             hover:bg-surface/80 transition-colors text-xs border border-surface/20 text-center"
                >
                  Outline Reader
                </a>
              </div>
              
              <div className="text-xs text-text-secondary">
                <p>Paper ID: {paperId}</p>
                <p className="mt-1 break-all">{url}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {loading && (
        <div className="absolute inset-0 flex items-center justify-center bg-surface/80 backdrop-blur-sm">
          <div className="text-center">
            <div className="w-8 h-8 border-2 border-primary/30 border-t-primary rounded-full animate-spin mx-auto mb-3" />
            <span className="text-text-secondary text-sm">Loading paper...</span>
          </div>
        </div>
      )}
    </div>
  );
}
