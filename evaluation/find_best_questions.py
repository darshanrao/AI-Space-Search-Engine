import json
import os
from pathlib import Path

# Read all question results
results = []
results_dir = Path('evaluation/results')

for article_dir in results_dir.iterdir():
    if article_dir.is_dir() and article_dir.name.startswith('article_'):
        article_id = article_dir.name.replace('article_', '')
        for question_file in article_dir.glob('question_*.json'):
            with open(question_file, 'r') as f:
                data = json.load(f)
                question_num = question_file.stem.replace('question_', '')
                # Extract retrieval scores
                retrieval = data.get('retrieval', {})
                retrieval_score = (retrieval.get('strict_recall_at_k', 0) + retrieval.get('soft_recall_at_k', 0)) / 2

                # Extract answer scores
                answer = data.get('answer', {})
                answer_score = (answer.get('semantic_similarity', 0) + answer.get('key_facts_coverage', 0)) / 2

                # Extract citation scores
                citations = data.get('citations', {})
                citation_score = (citations.get('precision', 0) + citations.get('recall', 0)) / 2

                results.append({
                    'article_id': article_id,
                    'question_num': question_num,
                    'file_path': str(question_file),
                    'question': data.get('question', ''),
                    'overall_score': data.get('overall_score', 0),
                    'retrieval_score': retrieval_score,
                    'answer_score': answer_score,
                    'citation_score': citation_score,
                    'question_type': data.get('question_type', ''),
                    'difficulty': data.get('difficulty', ''),
                })

# Sort by overall score
results.sort(key=lambda x: x['overall_score'], reverse=True)

# Print top 20 for analysis
print("=" * 100)
print("TOP 20 QUESTIONS BY OVERALL SCORE")
print("=" * 100)
for i, r in enumerate(results[:20], 1):
    print(f"\n{i}. Score: {r['overall_score']:.3f} | Article: {r['article_id']} | Q{r['question_num']} | Type: {r['question_type']} | Difficulty: {r['difficulty']}")
    print(f"   R: {r['retrieval_score']:.2f} | A: {r['answer_score']:.2f} | C: {r['citation_score']:.2f}")
    print(f"   Question: {r['question'][:120]}...")
    print(f"   File: {r['file_path']}")

# Find diverse set
print("\n\n" + "=" * 100)
print("DIVERSE SET OF TOP QUESTIONS (Different types and topics)")
print("=" * 100)

diverse_set = []
used_types = set()
used_articles = set()

# Get one excellent example from each question type
question_types = ['factual', 'comparative', 'complex', 'specific', 'broad']

for q_type in question_types:
    for result in results:
        if result['overall_score'] >= 0.95 and result['question_type'] == q_type:
            if result['article_id'] not in used_articles:
                diverse_set.append(result)
                used_types.add(q_type)
                used_articles.add(result['article_id'])
                break

# If we don't have 5 yet, add more high scoring ones from different articles
if len(diverse_set) < 5:
    for result in results:
        if len(diverse_set) >= 5:
            break
        if result not in diverse_set and result['overall_score'] >= 0.95:
            if result['article_id'] not in used_articles:
                diverse_set.append(result)
                used_articles.add(result['article_id'])

for i, r in enumerate(diverse_set, 1):
    print(f"\n{i}. Score: {r['overall_score']:.3f} | Article: {r['article_id']} | Q{r['question_num']} | Type: {r['question_type']} | Difficulty: {r['difficulty']}")
    print(f"   Retrieval: {r['retrieval_score']:.2f} | Answer: {r['answer_score']:.2f} | Citation: {r['citation_score']:.2f}")
    print(f"   Question: {r['question']}")
    print(f"   File: {r['file_path']}")
