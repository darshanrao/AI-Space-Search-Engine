// Block and citation types for document structure
export interface Span {
  text: string;
  start: number;
  end: number;
  type?: string;
}

export interface ParagraphBlock {
  type: 'paragraph';
  text: string;
  spans?: Span[];
}

export interface FigureBlock {
  type: 'figure';
  caption: string;
  figure_id: string;
  figure_url?: string;
  spans?: Span[];
}

export interface TableBlock {
  type: 'table';
  caption?: string;
  table_id: string;
  data: string[][];
  spans?: Span[];
}

export type Block = ParagraphBlock | FigureBlock | TableBlock;

export interface Citation {
  id: string;
  url: string;
  why_relevant: string;
}

export interface EvidenceBadges {
  has_figure: boolean;
  has_table: boolean;
  has_equation: boolean;
  has_code: boolean;
}

export interface ImageCitation {
  id: string;
  url: string;
  why_relevant: string;
}

export interface AnswerPayload {
  answer: string;
  citations: (Citation | string)[];
  image_citations?: ImageCitation[];
  image_urls?: string[];
  context_ids?: string[];
  confident?: boolean;
  blocks?: Block[];
  evidence_badges?: EvidenceBadges;
  confidence_score?: number;
}

// API response types
export interface SearchResponse {
  hits: {
    paper_id: string;
    title: string;
    year: number;
    score: number;
    snippet: string;
    sections: string[];
  }[];
  total: number;
  facets?: any;
  context?: any;
}

export interface ThreadResponse {
  thread_id: string;
  messages?: {
    role: 'user' | 'assistant';
    text?: string;
    answer?: string;
  }[];
  context?: any;
}
