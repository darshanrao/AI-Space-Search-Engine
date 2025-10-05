'use client';

import { useState } from 'react';
import { AnswerPayload } from '@/lib/types';
import ImageSidebar from './ImageSidebar';

interface ChatAnswerProps {
  answer: AnswerPayload;
}

/**
 * ChatAnswer component displays answer details within chat bubbles
 * Shows blocks, citations, and evidence badges in a compact format
 */
export default function ChatAnswer({ answer }: ChatAnswerProps) {
  const [sidebarImage, setSidebarImage] = useState<{
    url: string;
    title?: string;
    source?: string;
  } | null>(null);

  const openImageSidebar = (url: string, title?: string, source?: string) => {
    setSidebarImage({ url, title, source });
  };

  const closeImageSidebar = () => {
    setSidebarImage(null);
  };


  // Render spans within text blocks
  const renderSpans = (text: string, spans?: Array<{start: number, end: number, type?: string}>) => {
    if (!spans || spans.length === 0) {
      return text;
    }

    const result = [];
    let lastIndex = 0;

    spans.forEach((span, index) => {
      // Add text before span
      if (span.start > lastIndex) {
        result.push(text.slice(lastIndex, span.start));
      }
      
      // Add highlighted span
      result.push(
        <mark key={index} className="bg-blue-500/30 text-blue-400 px-1 rounded">
          {text.slice(span.start, span.end)}
        </mark>
      );
      
      lastIndex = span.end;
    });

    // Add remaining text
    if (lastIndex < text.length) {
      result.push(text.slice(lastIndex));
    }

    return result;
  };

  // Render individual block based on type
  const renderBlock = (block: {type: string, text?: string, caption?: string, data?: string[][], figure_id?: string, table_id?: string, figure_url?: string, spans?: Array<{start: number, end: number, type?: string}>}, index: number) => {
    switch (block.type) {
      case 'paragraph':
        return (
          <div key={index} className="mb-3 last:mb-0">
            <p className="text-sm leading-relaxed">
              {renderSpans(block.text || '', block.spans)}
            </p>
          </div>
        );

      case 'figure':
        return (
          <div key={index} className="mb-3 p-2 bg-gray-800/30 rounded-lg border border-gray-800/20">
            <div className="flex items-center space-x-1 mb-2">
              <svg className="w-3 h-3 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <span className="text-xs font-medium text-blue-400">Figure {block.figure_id}</span>
            </div>
            {block.figure_url && (
              <img 
                src={block.figure_url} 
                alt={block.caption}
                className="w-full max-w-xs mx-auto rounded border border-gray-800/20"
              />
            )}
            <p className="text-xs text-gray-400 mt-2 italic">
              {renderSpans(block.caption || '', block.spans)}
            </p>
          </div>
        );

      case 'table':
        return (
          <div key={index} className="mb-3 p-2 bg-gray-800/30 rounded-lg border border-gray-800/20">
            <div className="flex items-center space-x-1 mb-2">
              <svg className="w-3 h-3 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M3 14h18m-9-4v8m-7 0V6a2 2 0 012-2h14a2 2 0 012 2v12a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
              </svg>
              <span className="text-xs font-medium text-blue-400">Table {block.table_id}</span>
            </div>
            {block.caption && (
              <p className="text-xs text-gray-400 mb-2 italic">
                {renderSpans(block.caption || '', block.spans)}
              </p>
            )}
            <div className="overflow-x-auto">
              <table className="w-full text-xs border-collapse border border-gray-800/20">
                <tbody>
                  {block.data?.slice(0, 3).map((row: string[], rowIndex: number) => (
                    <tr key={rowIndex}>
                      {row.map((cell: string, cellIndex: number) => (
                        <td 
                          key={cellIndex} 
                          className="border border-gray-800/20 px-2 py-1 text-blue-400"
                        >
                          {cell}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
                {block.data && block.data.length > 3 && (
                <p className="text-xs text-gray-400 mt-1">
                  ... and {block.data.length - 3} more rows
                </p>
              )}
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="space-y-4">
      {/* Evidence Badges */}
      {answer.evidence_badges && (
        <div className="flex flex-wrap gap-1">
          {answer.evidence_badges.has_figure && (
            <span className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded-full text-xs">
              📊 Figures
            </span>
          )}
          {answer.evidence_badges.has_table && (
            <span className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded-full text-xs">
              📋 Tables
            </span>
          )}
          {answer.evidence_badges.has_equation && (
            <span className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded-full text-xs">
              🧮 Equations
            </span>
          )}
          {answer.evidence_badges.has_code && (
            <span className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded-full text-xs">
              💻 Code
            </span>
          )}
        </div>
      )}

      {/* Blocks */}
      {answer.blocks && answer.blocks.length > 0 && (
        <div className="space-y-3">
          {answer.blocks.map((block, index) => renderBlock(block, index))}
        </div>
      )}

      {/* Images */}
      {((answer.image_citations && answer.image_citations.length > 0) || (answer.image_urls && answer.image_urls.length > 0)) && (
        <div className="border-t border-gray-800/20 pt-3">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {/* Display image_citations (from RAG pipeline) */}
            {answer.image_citations?.map((image, index) => (
              <div key={`citation-${index}`} className="relative group">
                <div 
                  className="relative overflow-hidden rounded-lg border border-gray-800/20 bg-gray-800/10 cursor-pointer"
                  onClick={() => openImageSidebar(image.url)}
                >
                  <img
                    src={image.url}
                    alt={`Image ${index + 1}`}
                    className="w-full h-auto max-h-64 object-cover transition-transform duration-200 group-hover:scale-105 cursor-pointer"
                    onClick={(e) => {
                      e.stopPropagation();
                      openImageSidebar(image.url);
                    }}
                    onError={(e) => {
                      const target = e.target as HTMLImageElement;
                      target.style.display = 'none';
                      const fallback = target.nextElementSibling as HTMLElement;
                      if (fallback) fallback.style.display = 'flex';
                    }}
                  />
                  <div 
                    className="hidden items-center justify-center h-32 bg-gray-800/20 text-gray-400 text-sm"
                    style={{ display: 'none' }}
                  >
                    <span>Image failed to load</span>
                  </div>
                  {/* Click indicator */}
                  <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors duration-200 flex items-center justify-center">
                    <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-200 bg-black/70 text-white px-3 py-2 rounded-lg flex items-center gap-2">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                      </svg>
                      <span className="text-sm font-medium">Click to enlarge</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
            
            {/* Display image_urls (from SERP API) */}
            {answer.image_urls?.map((imageUrl, index) => (
              <div key={`serp-${index}`} className="relative group">
                <div 
                  className="relative overflow-hidden rounded-lg border border-gray-800/20 bg-gray-800/10 cursor-pointer"
                  onClick={() => openImageSidebar(imageUrl)}
                >
                  <img
                    src={imageUrl}
                    alt={`SERP Image ${index + 1}`}
                    className="w-full h-auto max-h-64 object-cover transition-transform duration-200 group-hover:scale-105 cursor-pointer"
                    onClick={(e) => {
                      e.stopPropagation();
                      openImageSidebar(imageUrl);
                    }}
                    onError={(e) => {
                      const target = e.target as HTMLImageElement;
                      target.style.display = 'none';
                      const fallback = target.nextElementSibling as HTMLElement;
                      if (fallback) fallback.style.display = 'flex';
                    }}
                  />
                  <div 
                    className="hidden items-center justify-center h-32 bg-gray-800/20 text-gray-400 text-sm"
                    style={{ display: 'none' }}
                  >
                    <span>Image failed to load</span>
                  </div>
                  {/* Click indicator */}
                  <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors duration-200 flex items-center justify-center">
                    <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-200 bg-black/70 text-white px-3 py-2 rounded-lg flex items-center gap-2">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                      </svg>
                      <span className="text-sm font-medium">Click to enlarge</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}


      {/* Confidence Indicator */}
      <div style={{
        marginTop: '12px',
        padding: '8px 12px',
        backgroundColor: 'rgba(30, 33, 51, 0.3)',
        borderRadius: '8px',
        border: '1px solid rgba(62, 142, 222, 0.2)'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          fontSize: '12px'
        }}>
          <span style={{color: 'var(--color-text-secondary)'}}>Confidence:</span>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}>
            {answer.confidence_score !== undefined ? (
              <>
                <div style={{
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  backgroundColor: answer.confidence_score >= 80 ? '#10B981' : 
                                   answer.confidence_score >= 60 ? '#F59E0B' : '#EF4444'
                }} />
                <span style={{
                  color: 'var(--color-text-blue-400)',
                  fontWeight: '500'
                }}>
                  {answer.confidence_score}%
                </span>
              </>
            ) : answer.confident !== undefined ? (
              <>
                <div style={{
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  backgroundColor: answer.confident ? '#10B981' : '#F59E0B'
                }} />
                <span style={{
                  color: 'var(--color-text-blue-400)',
                  fontWeight: '500'
                }}>
                  {answer.confident ? 'High' : 'Low'}
                </span>
              </>
            ) : (
              <span style={{color: 'var(--color-text-secondary)'}}>No confidence data</span>
            )}
          </div>
        </div>
      </div>

      {/* Mini Graph Panel - Removed since context is not in AnswerPayload */}
      
      {/* Image Sidebar */}
      {sidebarImage && (
        <ImageSidebar
          isOpen={!!sidebarImage}
          onClose={closeImageSidebar}
          imageUrl={sidebarImage.url}
          imageTitle={sidebarImage.title}
          imageSource={sidebarImage.source}
        />
      )}
    </div>
  );
}
