'use client';

import { Block, Citation, EvidenceBadges } from '@/lib/types';

interface AnswerCardProps {
  answer: string;
  blocks: Block[];
  citations: Citation[];
  evidenceBadges: EvidenceBadges;
  confidenceScore?: number;
}

/**
 * AnswerCard component renders the complete answer with blocks, citations, and evidence badges
 * Handles different block types: paragraphs, figures, and tables
 */
export default function AnswerCard({ 
  answer, 
  blocks, 
  citations, 
  evidenceBadges, 
  confidenceScore 
}: AnswerCardProps) {
  
  // Render spans within text blocks
  const renderSpans = (text: string, spans?: any[]) => {
    if (!spans || spans.length === 0) {
      return text;
    }

    let result = [];
    let lastIndex = 0;

    spans.forEach((span, index) => {
      // Add text before span
      if (span.start > lastIndex) {
        result.push(text.slice(lastIndex, span.start));
      }
      
      // Add highlighted span
      result.push(
        <mark key={index} className="bg-primary/20 text-primary px-1 rounded">
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
  const renderBlock = (block: Block, index: number) => {
    switch (block.type) {
      case 'paragraph':
        return (
          <div key={index} className="mb-4">
            <p className="text-text-primary leading-relaxed">
              {renderSpans(block.text, block.spans)}
            </p>
          </div>
        );

      case 'figure':
        return (
          <div key={index} className="mb-6 p-4 bg-surface/50 rounded-lg border border-surface/20">
            <div className="flex items-center space-x-2 mb-2">
              <svg className="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <span className="text-sm font-medium text-text-secondary">Figure {block.figure_id}</span>
            </div>
            {block.figure_url && (
              <img 
                src={block.figure_url} 
                alt={block.caption}
                className="w-full max-w-md mx-auto rounded-lg border border-surface/20"
              />
            )}
            <p className="text-sm text-text-secondary mt-2 italic">
              {renderSpans(block.caption, block.spans)}
            </p>
          </div>
        );

      case 'table':
        return (
          <div key={index} className="mb-6 p-4 bg-surface/50 rounded-lg border border-surface/20">
            <div className="flex items-center space-x-2 mb-3">
              <svg className="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M3 14h18m-9-4v8m-7 0V6a2 2 0 012-2h14a2 2 0 012 2v12a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
              </svg>
              <span className="text-sm font-medium text-text-secondary">Table {block.table_id}</span>
            </div>
            {block.caption && (
              <p className="text-sm text-text-secondary mb-3 italic">
                {renderSpans(block.caption, block.spans)}
              </p>
            )}
            <div className="overflow-x-auto">
              <table className="w-full text-sm border-collapse border border-surface/20">
                <tbody>
                  {block.data.map((row, rowIndex) => (
                    <tr key={rowIndex}>
                      {row.map((cell, cellIndex) => (
                        <td 
                          key={cellIndex} 
                          className="border border-surface/20 px-3 py-2 text-text-primary"
                        >
                          {cell}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="bg-surface/30 rounded-xl border border-surface/20 p-6 space-y-6">
      {/* Main Answer */}
      <div>
        <h2 className="text-lg font-semibold text-text-primary mb-3">Answer</h2>
        <p className="text-text-primary leading-relaxed">{answer}</p>
        {confidenceScore && (
          <div className="mt-3 flex items-center space-x-2">
            <span className="text-sm text-text-secondary">Confidence:</span>
            <div className="flex items-center space-x-1">
              <div className="w-20 h-2 bg-surface rounded-full overflow-hidden">
                <div 
                  className="h-full bg-primary transition-all duration-300"
                  style={{ width: `${confidenceScore * 100}%` }}
                />
              </div>
              <span className="text-sm text-text-secondary">
                {Math.round(confidenceScore * 100)}%
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Evidence Badges */}
      <div>
        <h3 className="text-md font-medium text-text-primary mb-3">Evidence Types</h3>
        <div className="flex flex-wrap gap-2">
          {evidenceBadges.has_figure && (
            <span className="px-3 py-1 bg-primary/20 text-primary rounded-full text-sm">
              📊 Figures
            </span>
          )}
          {evidenceBadges.has_table && (
            <span className="px-3 py-1 bg-primary/20 text-primary rounded-full text-sm">
              📋 Tables
            </span>
          )}
          {evidenceBadges.has_equation && (
            <span className="px-3 py-1 bg-primary/20 text-primary rounded-full text-sm">
              🧮 Equations
            </span>
          )}
          {evidenceBadges.has_code && (
            <span className="px-3 py-1 bg-primary/20 text-primary rounded-full text-sm">
              💻 Code
            </span>
          )}
        </div>
      </div>

      {/* Blocks */}
      {blocks.length > 0 && (
        <div>
          <h3 className="text-md font-medium text-text-primary mb-3">Supporting Content</h3>
          <div className="space-y-4">
            {blocks.map((block, index) => renderBlock(block, index))}
          </div>
        </div>
      )}

      {/* Citations */}
      {citations.length > 0 && (
        <div>
          <h3 className="text-md font-medium text-text-primary mb-3">References</h3>
          <div className="space-y-3">
            {citations.map((citation, index) => (
              <div key={index} className="p-3 bg-surface/50 rounded-lg border border-surface/20">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="font-medium text-text-primary mb-1">
                      {citation.title}
                    </h4>
                    <p className="text-sm text-text-secondary mb-1">
                      {citation.authors.join(', ')} ({citation.year})
                    </p>
                    {citation.venue && (
                      <p className="text-sm text-text-secondary">
                        {citation.venue}
                      </p>
                    )}
                  </div>
                  <div className="flex space-x-2 ml-4">
                    {citation.doi && (
                      <a 
                        href={`https://doi.org/${citation.doi}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary hover:text-primary/80 text-sm"
                      >
                        DOI
                      </a>
                    )}
                    {citation.url && (
                      <a 
                        href={citation.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary hover:text-primary/80 text-sm"
                      >
                        Link
                      </a>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
