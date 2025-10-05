'use client';

interface GraphNode {
  id: string;
  label: string;
  type: 'organism' | 'condition' | 'gene' | 'protein' | 'pathway' | 'disease';
  x?: number;
  y?: number;
}

interface GraphEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
  type: 'interacts' | 'regulates' | 'expresses' | 'causes' | 'treats';
  weight?: number;
}

interface MiniGraphPanelProps {
  nodes?: GraphNode[];
  edges?: GraphEdge[];
  title?: string;
}

/**
 * MiniGraphPanel component displays a compact read-only graph preview
 * Shows nodes and edges in a simplified list format
 */
export default function MiniGraphPanel({ 
  nodes = [], 
  edges = [], 
  title = "Knowledge Graph" 
}: MiniGraphPanelProps) {
  
  // Get node type color
  const getNodeTypeColor = (type: string) => {
    switch (type) {
      case 'organism': return 'bg-green-500/20 text-green-400';
      case 'condition': return 'bg-blue-500/20 text-blue-400';
      case 'gene': return 'bg-purple-500/20 text-purple-400';
      case 'protein': return 'bg-orange-500/20 text-orange-400';
      case 'pathway': return 'bg-pink-500/20 text-pink-400';
      case 'disease': return 'bg-red-500/20 text-red-400';
      default: return 'bg-gray-500/20 text-gray-400';
    }
  };

  // Get edge type color
  const getEdgeTypeColor = (type: string) => {
    switch (type) {
      case 'interacts': return 'text-blue-400';
      case 'regulates': return 'text-green-400';
      case 'expresses': return 'text-purple-400';
      case 'causes': return 'text-red-400';
      case 'treats': return 'text-green-400';
      default: return 'text-gray-400';
    }
  };

  // Get edge type icon
  const getEdgeTypeIcon = (type: string) => {
    switch (type) {
      case 'interacts':
        return (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
          </svg>
        );
      case 'regulates':
        return (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        );
      case 'expresses':
        return (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 4V2a1 1 0 011-1h8a1 1 0 011 1v2m0 0V1a1 1 0 011-1h2a1 1 0 011 1v18a1 1 0 01-1 1h-2a1 1 0 01-1-1V4zM7 4v16a1 1 0 001 1h8a1 1 0 001-1V4M7 4H5a1 1 0 00-1 1v14a1 1 0 001 1h2V4z" />
          </svg>
        );
      case 'causes':
        return (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        );
      case 'treats':
        return (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
          </svg>
        );
      default:
        return (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
          </svg>
        );
    }
  };

  // Don't render if no graph data
  if (nodes.length === 0 && edges.length === 0) {
    return null;
  }

  return (
    <div className="bg-surface/30 rounded-xl border border-surface/20 p-4">
      <div className="flex items-center space-x-2 mb-4">
        <svg className="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
        <h3 className="text-md font-medium text-text-primary">{title}</h3>
      </div>

      <div className="space-y-4">
        {/* Nodes Section */}
        {nodes.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-text-secondary mb-2">
              Entities ({nodes.length})
            </h4>
            <div className="space-y-2 max-h-32 overflow-y-auto">
              {nodes.map((node) => (
                <div key={node.id} className="flex items-center space-x-2">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${getNodeTypeColor(node.type)}`}>
                    {node.type}
                  </span>
                  <span className="text-sm text-text-primary truncate">{node.label}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Edges Section */}
        {edges.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-text-secondary mb-2">
              Relationships ({edges.length})
            </h4>
            <div className="space-y-2 max-h-32 overflow-y-auto">
              {edges.map((edge) => {
                const sourceNode = nodes.find(n => n.id === edge.source);
                const targetNode = nodes.find(n => n.id === edge.target);
                
                return (
                  <div key={edge.id} className="flex items-center space-x-2 text-sm">
                    <span className="text-text-primary truncate max-w-20">
                      {sourceNode?.label || edge.source}
                    </span>
                    <div className={`flex items-center space-x-1 ${getEdgeTypeColor(edge.type)}`}>
                      {getEdgeTypeIcon(edge.type)}
                      <span className="text-xs">
                        {edge.label || edge.type}
                      </span>
                    </div>
                    <span className="text-text-primary truncate max-w-20">
                      {targetNode?.label || edge.target}
                    </span>
                    {edge.weight && (
                      <span className="text-xs text-text-secondary">
                        ({Math.round(edge.weight * 100)}%)
                      </span>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Graph Summary */}
      <div className="mt-4 pt-3 border-t border-surface/20">
        <div className="flex items-center justify-between text-xs text-text-secondary">
          <span>{nodes.length} entities</span>
          <span>{edges.length} relationships</span>
        </div>
      </div>
    </div>
  );
}
