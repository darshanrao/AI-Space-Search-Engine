"""
Core evaluation metrics for RAG system.
Calculates retrieval, answer, and citation metrics.
"""

import re
import string
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class RAGEvaluator:
    def __init__(self):
        """Initialize evaluator with semantic similarity model."""
        self.similarity_model = SentenceTransformer('all-MiniLM-L6-v2')

    # ==================== RETRIEVAL METRICS ====================

    def calculate_strict_recall_at_k(self, rag_citations: List[str], must_retrieve: List[str]) -> float:
        """
        Calculate strict recall: # of RAG citations in must_retrieve / total must_retrieve
        """
        if not must_retrieve:
            return 1.0  # No required chunks = perfect recall

        rag_set = set(rag_citations)
        must_set = set(must_retrieve)

        found = len(rag_set.intersection(must_set))
        return found / len(must_set)

    def calculate_soft_recall_at_k(self, rag_citations: List[str],
                                    must_retrieve: List[str],
                                    should_retrieve: List[str]) -> float:
        """
        Calculate soft recall: # of RAG citations in (must + should) / total (must + should)
        """
        combined_relevant = must_retrieve + should_retrieve
        if not combined_relevant:
            return 1.0

        rag_set = set(rag_citations)
        combined_set = set(combined_relevant)

        found = len(rag_set.intersection(combined_set))
        return found / len(combined_set)

    def calculate_retrieval_score(self, rag_citations: List[str], ground_truth: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate all retrieval metrics and return combined score.
        Returns dict with strict_recall, soft_recall, and retrieval_score.
        Note: Precision removed since fixed K > relevant docs makes it meaningless.
        """
        must_retrieve = ground_truth.get('must_retrieve', [])
        should_retrieve = ground_truth.get('should_retrieve', [])

        strict_recall = self.calculate_strict_recall_at_k(rag_citations, must_retrieve)
        soft_recall = self.calculate_soft_recall_at_k(rag_citations, must_retrieve, should_retrieve)

        retrieval_score = (strict_recall + soft_recall) / 2.0

        return {
            'strict_recall_at_k': round(strict_recall, 4),
            'soft_recall_at_k': round(soft_recall, 4),
            'retrieval_score': round(retrieval_score, 4)
        }

    # ==================== ANSWER METRICS ====================

    def calculate_semantic_similarity(self, rag_answer: str, ground_truth_answer: str) -> float:
        """
        Calculate cosine similarity between RAG answer and ground truth using sentence-transformers.
        """
        if not rag_answer or not ground_truth_answer:
            return 0.0

        # Embed both answers
        embeddings = self.similarity_model.encode([rag_answer, ground_truth_answer])

        # Calculate cosine similarity
        similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
        return float(similarity)

    def calculate_key_facts_coverage(self, rag_answer: str, key_facts: List[str], threshold: float = 0.5) -> float:
        """
        Calculate what fraction of key facts are covered in RAG answer using semantic similarity.

        Compares each fact to individual sentences in the answer (not the whole answer),
        and uses the maximum similarity score.

        Args:
            rag_answer: The generated RAG answer
            key_facts: List of key facts from ground truth
            threshold: Minimum similarity score to consider a fact as covered (default 0.5)

        Returns:
            Fraction of key facts covered (0.0 to 1.0)
        """
        if not key_facts:
            return 1.0  # No facts to check = perfect coverage

        if not rag_answer:
            return 0.0

        # Split answer into sentences (simple split on . ! ?)
        import re
        sentences = re.split(r'[.!?]+', rag_answer)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return 0.0

        # Encode all sentences and facts
        sentence_embeddings = self.similarity_model.encode(sentences)
        fact_embeddings = self.similarity_model.encode(key_facts)

        # Check each fact against the most similar sentence
        found_count = 0
        for fact_embedding in fact_embeddings:
            # Calculate similarity with each sentence
            similarities = cosine_similarity([fact_embedding], sentence_embeddings)[0]
            max_similarity = np.max(similarities)

            if max_similarity >= threshold:
                found_count += 1

        return found_count / len(key_facts)

    def calculate_answer_score(self, rag_answer: str, ground_truth: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate all answer metrics and return combined score.
        Returns dict with semantic_similarity, key_facts_coverage, and answer_score.
        """
        ground_truth_answer = ground_truth.get('answer_markdown', '')
        key_facts = ground_truth.get('key_facts', [])

        semantic_sim = self.calculate_semantic_similarity(rag_answer, ground_truth_answer)
        facts_coverage = self.calculate_key_facts_coverage(rag_answer, key_facts)

        answer_score = (semantic_sim + facts_coverage) / 2.0

        return {
            'semantic_similarity': round(semantic_sim, 4),
            'key_facts_coverage': round(facts_coverage, 4),
            'answer_score': round(answer_score, 4)
        }

    # ==================== CITATION METRICS ====================

    def calculate_citation_precision(self, rag_citations: List[str], ground_truth_citations: List[str]) -> float:
        """
        Citation precision: # of RAG citations in ground truth / total RAG citations
        """
        if not rag_citations:
            return 0.0

        rag_set = set(rag_citations)
        gt_set = set(ground_truth_citations)

        correct = len(rag_set.intersection(gt_set))
        return correct / len(rag_citations)

    def calculate_citation_recall(self, rag_citations: List[str], ground_truth_citations: List[str]) -> float:
        """
        Citation recall: # of ground truth citations in RAG / total ground truth citations
        """
        if not ground_truth_citations:
            return 1.0

        rag_set = set(rag_citations)
        gt_set = set(ground_truth_citations)

        found = len(gt_set.intersection(rag_set))
        return found / len(ground_truth_citations)

    def validate_citation_format(self, citations: List[str]) -> bool:
        """
        Check if all citations follow format: PMCID:section:hash
        Returns True if all valid, False otherwise.
        """
        pattern = r'^PMC\d+:[^:]+:[a-f0-9]+$'
        for citation in citations:
            if not re.match(pattern, citation):
                return False
        return True

    def calculate_citation_score(self, rag_citations: List[str], ground_truth_citations: List[str]) -> Dict[str, Any]:
        """
        Calculate all citation metrics and return combined score.
        Returns dict with precision, recall, accuracy, and citation_score.
        """
        precision = self.calculate_citation_precision(rag_citations, ground_truth_citations)
        recall = self.calculate_citation_recall(rag_citations, ground_truth_citations)
        accuracy_valid = self.validate_citation_format(rag_citations)
        accuracy = "PASS" if accuracy_valid else "FAIL"
        accuracy_numeric = 1.0 if accuracy_valid else 0.0

        citation_score = (precision + recall + accuracy_numeric) / 3.0

        return {
            'precision': round(precision, 4),
            'recall': round(recall, 4),
            'accuracy': accuracy,
            'citation_score': round(citation_score, 4)
        }

    # ==================== OVERALL SCORE ====================

    def calculate_overall_score(self, retrieval_score: float, answer_score: float, citation_score: float) -> float:
        """
        Calculate weighted overall score:
        0.35 * retrieval + 0.45 * answer + 0.20 * citation

        Weights prioritize answer quality while giving significant weight to retrieval
        since it's the foundation of the RAG system.
        """
        overall = 0.35 * retrieval_score + 0.45 * answer_score + 0.20 * citation_score
        return round(overall, 4)

    # ==================== MAIN EVALUATION ====================

    def evaluate_single_case(self, rag_output: Dict[str, Any], ground_truth: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a single test case.

        Args:
            rag_output: Dict with 'answer_markdown', 'citations' (list of dicts with 'id'),
                       and 'retrieved_chunks' (list of chunk IDs from vector search)
            ground_truth: Dict with test case data (must_retrieve, answer_markdown, key_facts, etc.)

        Returns:
            Dict with all metrics and overall score
        """
        # Extract RAG data
        rag_citation_ids = [c['id'] for c in rag_output.get('citations', [])]
        rag_retrieved_ids = rag_output.get('retrieved_chunks', [])
        rag_answer = rag_output.get('answer_markdown', '')

        # Extract ground truth citation IDs
        gt_citations = ground_truth.get('citations', [])

        # Calculate all metrics
        # Use retrieved chunks for retrieval metrics, not citations!
        retrieval_metrics = self.calculate_retrieval_score(rag_retrieved_ids, ground_truth)
        answer_metrics = self.calculate_answer_score(rag_answer, ground_truth)
        citation_metrics = self.calculate_citation_score(rag_citation_ids, gt_citations)

        # Calculate overall score
        overall_score = self.calculate_overall_score(
            retrieval_metrics['retrieval_score'],
            answer_metrics['answer_score'],
            citation_metrics['citation_score']
        )

        # Remove intermediate scores, keep only component metrics
        retrieval_display = {k: v for k, v in retrieval_metrics.items() if k != 'retrieval_score'}
        answer_display = {k: v for k, v in answer_metrics.items() if k != 'answer_score'}
        citation_display = {k: v for k, v in citation_metrics.items() if k != 'citation_score'}

        return {
            'retrieval': retrieval_display,
            'answer': answer_display,
            'citations': citation_display,
            'overall_score': overall_score
        }
