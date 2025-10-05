'use client';

import { AnswerPayload } from '@/lib/types';
import MiniGraphPanel from './MiniGraphPanel';

interface ChatAnswerProps {
  answer: AnswerPayload;
}

/**
 * ChatAnswer component displays answer details within chat bubbles
 * Shows blocks, citations, and evidence badges in a compact format
 */
export default function ChatAnswer({ answer }: ChatAnswerProps) {
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
        <mark key={index} className="bg-primary/30 text-primary px-1 rounded">
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
  const renderBlock = (block: any, index: number) => {
    switch (block.type) {
      case 'paragraph':
        return (
          <div key={index} className="mb-3 last:mb-0">
            <p className="text-sm leading-relaxed">
              {renderSpans(block.text, block.spans)}
            </p>
          </div>
        );

      case 'figure':
        return (
          <div key={index} className="mb-3 p-2 bg-surface/30 rounded-lg border border-surface/20">
            <div className="flex items-center space-x-1 mb-2">
              <svg className="w-3 h-3 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <span className="text-xs font-medium text-primary">Figure {block.figure_id}</span>
            </div>
            {block.figure_url && (
              <img 
                src={block.figure_url} 
                alt={block.caption}
                className="w-full max-w-xs mx-auto rounded border border-surface/20"
              />
            )}
            <p className="text-xs text-text-secondary mt-2 italic">
              {renderSpans(block.caption, block.spans)}
            </p>
          </div>
        );

      case 'table':
        return (
          <div key={index} className="mb-3 p-2 bg-surface/30 rounded-lg border border-surface/20">
            <div className="flex items-center space-x-1 mb-2">
              <svg className="w-3 h-3 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M3 14h18m-9-4v8m-7 0V6a2 2 0 012-2h14a2 2 0 012 2v12a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
              </svg>
              <span className="text-xs font-medium text-primary">Table {block.table_id}</span>
            </div>
            {block.caption && (
              <p className="text-xs text-text-secondary mb-2 italic">
                {renderSpans(block.caption, block.spans)}
              </p>
            )}
            <div className="overflow-x-auto">
              <table className="w-full text-xs border-collapse border border-surface/20">
                <tbody>
                  {block.data.slice(0, 3).map((row: string[], rowIndex: number) => (
                    <tr key={rowIndex}>
                      {row.map((cell: string, cellIndex: number) => (
                        <td 
                          key={cellIndex} 
                          className="border border-surface/20 px-2 py-1 text-text-primary"
                        >
                          {cell}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
              {block.data.length > 3 && (
                <p className="text-xs text-text-secondary mt-1">
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
            <span className="px-2 py-1 bg-primary/20 text-primary rounded-full text-xs">
              📊 Figures
            </span>
          )}
          {answer.evidence_badges.has_table && (
            <span className="px-2 py-1 bg-primary/20 text-primary rounded-full text-xs">
              📋 Tables
            </span>
          )}
          {answer.evidence_badges.has_equation && (
            <span className="px-2 py-1 bg-primary/20 text-primary rounded-full text-xs">
              🧮 Equations
            </span>
          )}
          {answer.evidence_badges.has_code && (
            <span className="px-2 py-1 bg-primary/20 text-primary rounded-full text-xs">
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

      {/* Citations */}
      {answer.citations && answer.citations.length > 0 && (
        <div className="border-t border-surface/20 pt-3">
          <h4 className="text-xs font-medium text-text-secondary mb-2">
            References ({answer.citations.length})
          </h4>
          <div className="space-y-2 max-h-32 overflow-y-auto">
            {answer.citations.slice(0, 3).map((citation, index) => (
              <div key={index} className="p-2 bg-surface/30 rounded border border-surface/20">
                <h5 className="text-xs font-medium text-text-primary line-clamp-1 mb-1">
                  <a 
                    href={citation.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-primary hover:text-primary/80 underline"
                  >
                    {citation.id}
                  </a>
                </h5>
                <p className="text-xs text-text-secondary">
                  {citation.why_relevant}
                </p>
              </div>
            ))}
            {answer.citations.length > 3 && (
              <p className="text-xs text-text-secondary">
                ... and {answer.citations.length - 3} more references
              </p>
            )}
          </div>
        </div>
      )}

      {/* Confidence Indicator */}
      {answer.confident !== undefined && (
        <div className="flex items-center space-x-2 text-xs">
          <span className="text-text-secondary">Confidence:</span>
          <div className="flex items-center space-x-1">
            <div className={`w-2 h-2 rounded-full ${answer.confident ? 'bg-green-500' : 'bg-yellow-500'}`} />
            <span className="text-text-secondary">
              {answer.confident ? 'High' : 'Low'}
            </span>
          </div>
        </div>
      )}

      {/* Mini Graph Panel */}
      {answer.context?.graph && (
        <div className="border-t border-surface/20 pt-3">
          <MiniGraphPanel
            nodes={answer.context.graph.nodes}
            edges={answer.context.graph.edges}
            title="Knowledge Graph"
          />
        </div>
      )}
    </div>
  );
}
