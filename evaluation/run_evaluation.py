"""
Main orchestration script for RAG system evaluation.
Loads test cases, runs RAG, and calculates metrics.
"""

import os
import sys
import json
import re
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict

# Add backend to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from backend.generation.api import query_rag_debug
from evaluator import RAGEvaluator


class RAGEvaluationRunner:
    def __init__(self, use_cache: bool = False):
        """
        Initialize evaluation runner.

        Args:
            use_cache: If True, use cached RAG outputs; if False, run fresh queries
        """
        self.use_cache = use_cache
        self.evaluator = RAGEvaluator()

        # Paths
        self.base_dir = Path(__file__).parent
        self.test_set_dir = self.base_dir / "data" / "test_set"
        self.formatted_docs_dir = self.base_dir / "data" / "formatted_docs"
        self.rag_outputs_dir = self.base_dir / "data" / "rag_outputs"
        self.results_dir = self.base_dir / "results"

        # Create directories if they don't exist
        self.rag_outputs_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def extract_article_number(self, filename: str) -> Optional[int]:
        """Extract article number from test case filename."""
        match = re.search(r'article_(\d+)_test_cases', filename)
        if match:
            return int(match.group(1))
        return None

    def get_rag_output_path(self, article_num: int, question_num: int) -> Path:
        """Get path for storing/retrieving RAG output."""
        article_dir = self.rag_outputs_dir / f"article_{article_num}"
        article_dir.mkdir(exist_ok=True)
        return article_dir / f"Q{question_num}_output.txt"

    def get_result_path(self, article_num: int, question_num: int) -> Path:
        """Get path for storing individual result JSON."""
        article_dir = self.results_dir / f"article_{article_num}"
        article_dir.mkdir(exist_ok=True)
        return article_dir / f"question_{question_num}.json"

    def run_rag_query(self, question: str, output_path: Path) -> str:
        """
        Run RAG query using query_rag_debug.

        Args:
            question: The question to ask
            output_path: Path where the output file should be saved

        Returns:
            Path to output file as string
        """
        print(f"    Running RAG query...")

        # Call query_rag_debug with the specific output path
        output_file = query_rag_debug(question, output_file=str(output_path))

        return output_file

    def parse_rag_output(self, output_file: str) -> Dict[str, Any]:
        """
        Parse RAG output text file to extract JSON answer and retrieved chunk IDs.

        Args:
            output_file: Path to RAG output text file

        Returns:
            Dict with answer_markdown, citations, and retrieved_chunks
        """
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract all retrieved chunk IDs from the RETRIEVED DOCUMENTS section
        retrieved_chunk_ids = []
        citation_id_pattern = r'Citation ID:\s*([^\s\n]+)'
        for match in re.finditer(citation_id_pattern, content):
            chunk_id = match.group(1)
            retrieved_chunk_ids.append(chunk_id)

        # Find the JSON blob after " GENERATED ANSWER"
        # Look for the JSON object that contains answer_markdown and citations
        json_match = re.search(r'\{[\s\S]*"answer_markdown"[\s\S]*"citations"[\s\S]*\}', content)

        if not json_match:
            raise ValueError(f"Could not find JSON answer in output file: {output_file}")

        json_str = json_match.group(0)
        rag_output = json.loads(json_str)

        # Add retrieved chunks to the output
        rag_output['retrieved_chunks'] = retrieved_chunk_ids

        return rag_output

    def evaluate_test_case(self, test_case: Dict[str, Any], article_num: int) -> Dict[str, Any]:
        """
        Evaluate a single test case.

        Args:
            test_case: Test case dict with id, question, ground_truth
            article_num: Article number

        Returns:
            Dict with evaluation results
        """
        # Extract question number from ID (e.g., "PMC4095884_Q1" -> 1)
        question_id = test_case['id']
        q_match = re.search(r'_Q(\d+)$', question_id)
        question_num = int(q_match.group(1)) if q_match else 0

        print(f"  [{question_id}] {test_case['question'][:80]}...")

        # Get RAG output path
        rag_output_path = self.get_rag_output_path(article_num, question_num)

        # Check if cached output exists
        if self.use_cache and rag_output_path.exists():
            print(f"    Using cached output: {rag_output_path}")
            output_file = str(rag_output_path)
        else:
            # Run fresh query, saving directly to the standardized location
            output_file = self.run_rag_query(test_case['question'], rag_output_path)

        # Parse RAG output
        try:
            rag_output = self.parse_rag_output(output_file)
        except Exception as e:
            print(f"    L ERROR parsing output: {e}")
            return None

        # Combine ground truth from retrieval and answer sections
        ground_truth = {
            'must_retrieve': test_case['ground_truth']['retrieval']['must_retrieve'],
            'should_retrieve': test_case['ground_truth']['retrieval']['should_retrieve'],
            'may_retrieve': test_case['ground_truth']['retrieval']['may_retrieve'],
            'answer_markdown': test_case['ground_truth']['answer']['answer_markdown'],
            'citations': [c['id'] for c in test_case['ground_truth']['answer']['citations']],
            'key_facts': test_case['ground_truth']['answer']['key_facts']
        }

        # Evaluate
        print(f"    Calculating metrics...")
        metrics = self.evaluator.evaluate_single_case(rag_output, ground_truth)

        # Build result object
        result = {
            'article_number': article_num,
            'test_case_id': question_id,
            'question': test_case['question'],
            'question_type': test_case['question_type'],
            'difficulty': test_case['difficulty'],
            **metrics
        }

        # Save individual result
        result_path = self.get_result_path(article_num, question_num)
        with open(result_path, 'w') as f:
            json.dump(result, f, indent=2)

        print(f"     Overall score: {result['overall_score']:.4f}")

        return result

    def run_evaluation(self) -> tuple[List[Dict], Dict]:
        """
        Run evaluation on all test cases.

        Returns:
            Tuple of (per_case_results, aggregate_results)
        """
        print("Starting RAG Evaluation...")
        print(f"Cache mode: {'ENABLED' if self.use_cache else 'DISABLED (fresh queries)'}\n")

        all_results = []

        # Find all test case files
        test_files = sorted(self.test_set_dir.glob("article_*_test_cases.json"))

        if not test_files:
            print("L No test case files found!")
            return [], {}

        print(f"Found {len(test_files)} test case file(s)\n")

        # Process each test file
        for test_file in test_files:
            article_num = self.extract_article_number(test_file.name)

            if article_num is None:
                print(f"�  Skipping {test_file.name} - couldn't extract article number")
                continue

            print(f"Processing Article {article_num} ({test_file.name})")

            # Load test cases
            with open(test_file, 'r') as f:
                test_data = json.load(f)

            test_cases = test_data.get('test_cases', [])
            print(f"  Found {len(test_cases)} test case(s)\n")

            # Evaluate each test case
            for test_case in test_cases:
                try:
                    result = self.evaluate_test_case(test_case, article_num)
                    if result:
                        all_results.append(result)
                except Exception as e:
                    print(f"  L ERROR evaluating {test_case['id']}: {e}")
                    continue

            print()

        # Calculate aggregate metrics
        print("\nCalculating aggregate metrics...")
        aggregate = self.calculate_aggregate_metrics(all_results)

        return all_results, aggregate

    def calculate_aggregate_metrics(self, results: List[Dict]) -> Dict[str, Any]:
        """Calculate aggregate statistics across all results."""
        if not results:
            return {}

        # Overall averages
        total_cases = len(results)

        avg_retrieval_scores = []
        avg_answer_scores = []
        avg_citation_scores = []
        avg_overall_scores = []

        for r in results:
            # Calculate component scores from sub-metrics
            retrieval_score = (
                r['retrieval']['strict_recall_at_k'] +
                r['retrieval']['soft_recall_at_k']
            ) / 2.0

            answer_score = (
                r['answer']['semantic_similarity'] +
                r['answer']['key_facts_coverage']
            ) / 2.0

            citation_accuracy = 1.0 if r['citations']['accuracy'] == 'PASS' else 0.0
            citation_score = (
                r['citations']['precision'] +
                r['citations']['recall'] +
                citation_accuracy
            ) / 3.0

            avg_retrieval_scores.append(retrieval_score)
            avg_answer_scores.append(answer_score)
            avg_citation_scores.append(citation_score)
            avg_overall_scores.append(r['overall_score'])

        # Group by question type
        by_question_type = defaultdict(list)
        for r in results:
            by_question_type[r['question_type']].append(r['overall_score'])

        question_type_stats = {
            qtype: {
                'avg_score': round(sum(scores) / len(scores), 4),
                'count': len(scores)
            }
            for qtype, scores in by_question_type.items()
        }

        # Group by difficulty
        by_difficulty = defaultdict(list)
        for r in results:
            by_difficulty[r['difficulty']].append(r['overall_score'])

        difficulty_stats = {
            diff: {
                'avg_score': round(sum(scores) / len(scores), 4),
                'count': len(scores)
            }
            for diff, scores in by_difficulty.items()
        }

        # Group by article
        by_article = defaultdict(list)
        for r in results:
            by_article[str(r['article_number'])].append(r['overall_score'])

        article_stats = {
            article: {
                'avg_score': round(sum(scores) / len(scores), 4),
                'count': len(scores)
            }
            for article, scores in by_article.items()
        }

        return {
            'total_test_cases': total_cases,
            'overall': {
                'avg_retrieval_score': round(sum(avg_retrieval_scores) / total_cases, 4),
                'avg_answer_score': round(sum(avg_answer_scores) / total_cases, 4),
                'avg_citation_score': round(sum(avg_citation_scores) / total_cases, 4),
                'avg_overall_score': round(sum(avg_overall_scores) / total_cases, 4)
            },
            'by_question_type': question_type_stats,
            'by_difficulty': difficulty_stats,
            'by_article': article_stats
        }

    def save_results(self, per_case_results: List[Dict], aggregate_results: Dict):
        """Save final results to JSON files."""
        # Save per-case results
        per_case_path = self.results_dir / "per_case_results.json"
        with open(per_case_path, 'w') as f:
            json.dump(per_case_results, f, indent=2)
        print(f" Saved per-case results to: {per_case_path}")

        # Save aggregate results
        aggregate_path = self.results_dir / "aggregate_results.json"
        with open(aggregate_path, 'w') as f:
            json.dump(aggregate_results, f, indent=2)
        print(f" Saved aggregate results to: {aggregate_path}")

        # Print summary
        print("\n" + "="*80)
        print("EVALUATION SUMMARY")
        print("="*80)
        print(f"Total test cases: {aggregate_results['total_test_cases']}")
        print(f"\nOverall Scores:")
        print(f"  Retrieval: {aggregate_results['overall']['avg_retrieval_score']:.4f}")
        print(f"  Answer:    {aggregate_results['overall']['avg_answer_score']:.4f}")
        print(f"  Citation:  {aggregate_results['overall']['avg_citation_score']:.4f}")
        print(f"  OVERALL:   {aggregate_results['overall']['avg_overall_score']:.4f}")
        print("="*80 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run RAG system evaluation")
    cache_group = parser.add_mutually_exclusive_group()
    cache_group.add_argument(
        '--use-cache',
        action='store_true',
        help='Use cached RAG outputs if available'
    )
    cache_group.add_argument(
        '--fresh',
        action='store_true',
        default=True,
        help='Run fresh RAG queries (default)'
    )

    args = parser.parse_args()

    # Determine cache setting (default to fresh)
    use_cache = args.use_cache

    # Run evaluation
    runner = RAGEvaluationRunner(use_cache=use_cache)
    per_case_results, aggregate_results = runner.run_evaluation()

    # Save results
    if per_case_results:
        runner.save_results(per_case_results, aggregate_results)
    else:
        print("L No results to save!")


if __name__ == "__main__":
    main()
