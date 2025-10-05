"""
Generate test cases for all formatted documents using Gemini API.
Reads formatted_docs/*.json and creates test_set/*_test_cases.json
"""

import os
import json
import time
import re
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from evaluation/.env
load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")

genai.configure(api_key=GEMINI_API_KEY)


PROMPT_TEMPLATE = """You are creating test cases for evaluating a RAG (Retrieval-Augmented Generation) system on scientific papers. I've attached chunks from a paper. Each chunk has a unique ID that you MUST use exactly as written.

YOUR TASK: Generate exactly 5 test questions with diverse characteristics:

1. **FACTUAL** (easy): Single-chunk answer, tests retrieval precision
   Example: "What percentage of bone volume was lost in microgravity?"

2. **COMPARATIVE** (medium): Requires synthesizing multiple chunks
   Example: "How do osteoclast and osteocyte mechanisms differ in bone loss?"

3. **COMPLEX** (hard): Requires reasoning across multiple sections
   Example: "What pathways connect microgravity exposure to bone degradation?"

4. **SPECIFIC** (medium): Narrow topic, tests precise retrieval
   Example: "Which matrix metalloproteinases were upregulated in spaceflight?"

5. **BROAD** (hard): Comprehensive overview requiring many chunks
   Example: "What are the main cellular and molecular mechanisms of bone loss?"

OUTPUT FORMAT (JSON only, no other text):
```json
{{
  "paper_id": "{paper_id}",
  "paper_title": "<extract from first chunk>",
  "paper_url": "{paper_url}",

  "test_cases": [
    {{
      "id": "{paper_id}_Q1",
      "question": "<your factual question>",
      "question_type": "factual",
      "difficulty": "easy",

      "ground_truth": {{
        "retrieval": {{
          "must_retrieve": [
            "PMC3630201:results:791ff47c"
          ],
          "should_retrieve": [
            "PMC3630201:abstract:7387dd27"
          ],
          "may_retrieve": []
        }},

        "answer": {{
          "answer_markdown": "Your answer here with **bold** for key facts and inline citations [1], [2].",

          "citations": [
            {{
              "id": "PMC3630201:results:791ff47c",
              "url": "{paper_url}",
              "why_relevant": "SPECIFIC explanation of why this chunk is relevant - not generic!"
            }},
            {{
              "id": "PMC3630201:abstract:7387dd27",
              "url": "{paper_url}",
              "why_relevant": "Another SPECIFIC explanation"
            }}
          ],

          "used_context_ids": [
            "PMC3630201:results:791ff47c",
            "PMC3630201:abstract:7387dd27",
            "PMC3630201:discussion:71589e17"
          ],

          "key_facts": [
            "Specific fact 1 with numbers",
            "Specific fact 2 with methods",
            "Specific fact 3 with findings"
          ],

          "confident": true
        }}
      }}
    }},
    {{
      "id": "{paper_id}_Q2",
      "question": "<your comparative question>",
      "question_type": "comparative",
      "difficulty": "medium",
      "ground_truth": {{
        "retrieval": {{ ... }},
        "answer": {{ ... }}
      }}
    }},
    {{
      "id": "{paper_id}_Q3",
      "question": "<your complex question>",
      "question_type": "complex",
      "difficulty": "hard",
      "ground_truth": {{
        "retrieval": {{ ... }},
        "answer": {{ ... }}
      }}
    }},
    {{
      "id": "{paper_id}_Q4",
      "question": "<your specific question>",
      "question_type": "specific",
      "difficulty": "medium",
      "ground_truth": {{
        "retrieval": {{ ... }},
        "answer": {{ ... }}
      }}
    }},
    {{
      "id": "{paper_id}_Q5",
      "question": "<your broad question>",
      "question_type": "broad",
      "difficulty": "hard",
      "ground_truth": {{
        "retrieval": {{ ... }},
        "answer": {{ ... }}
      }}
    }}
  ]
}}
```

Here is the paper document with all chunks:

{document}

Generate the 5 test cases now. Output ONLY the JSON, no explanations or other text.
"""


class TestCaseGenerator:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.formatted_docs_dir = self.base_dir / "data" / "formatted_docs"
        self.test_set_dir = self.base_dir / "data" / "test_set"

        # Create test_set directory if it doesn't exist
        self.test_set_dir.mkdir(parents=True, exist_ok=True)

        # Initialize Gemini model (using Flash for speed and 1M token context)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def extract_article_number(self, filename: str) -> int:
        """Extract article number from filename like 'article_10.txt'"""
        match = re.search(r'article_(\d+)\.txt', filename)
        if match:
            return int(match.group(1))
        return None

    def generate_test_cases(self, formatted_doc_path: Path, max_retries: int = 3) -> dict:
        """
        Generate test cases for a single formatted document.

        Args:
            formatted_doc_path: Path to formatted document text file

        Returns:
            Dict with generated test cases
        """
        # Read the entire formatted document
        with open(formatted_doc_path, 'r', encoding='utf-8') as f:
            document_content = f.read()

        # Extract paper_id and paper_url from the first few lines
        paper_id = 'UNKNOWN'
        paper_url = 'UNKNOWN'

        lines = document_content.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            if line.startswith('PAPER ID:'):
                paper_id = line.replace('PAPER ID:', '').strip()
            elif line.startswith('URL:'):
                paper_url = line.replace('URL:', '').strip()

        # Create the prompt
        prompt = PROMPT_TEMPLATE.format(
            paper_id=paper_id,
            paper_url=paper_url,
            document=document_content
        )

        # Call Gemini API with retries
        for attempt in range(max_retries):
            try:
                print(f"  Calling Gemini API... (attempt {attempt + 1}/{max_retries})")
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.3,  # Lower temperature for more consistent output
                        max_output_tokens=16384,  # Increased for full JSON response
                    )
                )

                # Extract JSON from response
                response_text = response.text.strip()

                # Remove code fence markers if present
                if response_text.startswith('```json'):
                    response_text = response_text[7:]  # Remove ```json
                elif response_text.startswith('```'):
                    response_text = response_text[3:]  # Remove ```

                if response_text.endswith('```'):
                    response_text = response_text[:-3]  # Remove trailing ```

                json_str = response_text.strip()

                # Parse JSON
                test_cases = json.loads(json_str)

                # Success!
                return test_cases

            except json.JSONDecodeError as e:
                print(f"  ⚠️  JSON parse error on attempt {attempt + 1}: {e}")
                print(f"  First 500 chars of response: {response_text[:500]}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1, 2, 4 seconds
                    print(f"  Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise

            except Exception as e:
                print(f"  ⚠️  API error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"  Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise

    def save_test_cases(self, test_cases: dict, article_num: int):
        """Save test cases to test_set directory."""
        output_file = self.test_set_dir / f"article_{article_num}_test_cases.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(test_cases, f, indent=2, ensure_ascii=False)

        print(f"  ✓ Saved to: {output_file}")

    def process_all_documents(self, limit: int = None):
        """
        Process all formatted documents and generate test cases.

        Args:
            limit: If set, only process first N documents (for testing)
        """
        # Find all formatted documents
        formatted_docs = sorted(self.formatted_docs_dir.glob("article_*.txt"))

        if not formatted_docs:
            print("❌ No formatted documents found!")
            return

        if limit:
            formatted_docs = formatted_docs[:limit]

        print(f"Found {len(formatted_docs)} formatted document(s)")
        print("=" * 80)

        success_count = 0
        error_count = 0

        for i, doc_path in enumerate(formatted_docs, 1):
            article_num = self.extract_article_number(doc_path.name)

            if article_num is None:
                print(f"⚠️  Skipping {doc_path.name} - couldn't extract article number")
                continue

            # Check if test cases already exist for this article
            output_file = self.test_set_dir / f"article_{article_num}_test_cases.json"
            if output_file.exists():
                print(f"\n[{i}/{len(formatted_docs)}] Skipping article {article_num} - test cases already exist")
                continue

            print(f"\n[{i}/{len(formatted_docs)}] Processing article {article_num} ({doc_path.name})")

            try:
                # Generate test cases
                test_cases = self.generate_test_cases(doc_path)

                # Save to test_set
                self.save_test_cases(test_cases, article_num)

                success_count += 1

                # Rate limiting - wait a bit between API calls
                if i < len(formatted_docs):
                    time.sleep(2)  # 2 second delay between requests

            except Exception as e:
                print(f"  ❌ ERROR: {e}")
                error_count += 1
                continue

        print("\n" + "=" * 80)
        print(f"SUMMARY: {success_count} succeeded, {error_count} failed")
        print("=" * 80)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate test cases using Gemini API")
    parser.add_argument(
        '--limit',
        type=int,
        help='Process only first N documents (for testing)'
    )

    args = parser.parse_args()

    generator = TestCaseGenerator()
    generator.process_all_documents(limit=args.limit)


if __name__ == "__main__":
    main()
