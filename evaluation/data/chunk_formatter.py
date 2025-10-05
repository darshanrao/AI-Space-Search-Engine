import json
import os

def format_chunks_for_llm(jsonl_path):
    """
    Convert JSONL into a readable format for an LLM, and save it to a .txt file
    in a subdirectory named 'formatted_docs'.
    """
    chunks = []
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            chunks.append(json.loads(line))
    
    if not chunks:
        return None, None, None, None

    paper_id = chunks[0]['pmcid']
    paper_url = chunks[0]['url']
    
    sections = {}
    for chunk in chunks:
        section = chunk.get('section', 'Unknown')
        if section not in sections:
            sections[section] = []
        sections[section].append(chunk)
    
    output = []
    output.append(f"PAPER ID: {paper_id}")
    output.append(f"URL: {paper_url}\n")
    
    for section_name, section_chunks in sorted(sections.items()):
        output.append(f"\n{'='*80}")
        output.append(f"SECTION: {section_name}")
        output.append(f"{'='*80}\n")
        for chunk in section_chunks:
            output.append(f"[CHUNK ID: {chunk['id']}]")
            output.append(f"Type: {chunk['kind']}")
            output.append(f"Content: {chunk['text']}\n")
    
    formatted_text = "\n".join(output)

    base_name = os.path.splitext(os.path.basename(jsonl_path))[0]  # e.g., "article_571"
    output_filename = f"{base_name}.txt"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, 'formatted_docs')
    os.makedirs(output_dir, exist_ok=True)
    output_filepath = os.path.join(output_dir, output_filename)

    with open(output_filepath, 'w', encoding='utf-8') as f_out:
        f_out.write(formatted_text)

    return formatted_text, paper_id, paper_url, output_filepath


# --- NEW MAIN LOGIC ---
if __name__ == "__main__":
    # Path to your sampled paper list
    sampled_json_path = "evaluation/data/sampled_papers_for_queries.json"

    # Load article numbers
    with open(sampled_json_path, 'r', encoding='utf-8') as f:
        sampled_data = json.load(f)

    # Extract and adjust article numbers
    article_numbers = [paper["article_number"] - 1 for paper in sampled_data["papers"]]

    print(f"Found {len(article_numbers)} sampled papers.")
    print(f"Article indices to process (JSONL files): {article_numbers}\n")

    # Directory containing your JSONL files
    jsonl_base_dir = "evaluation/data/outputs_sentence_robust"

    processed = 0
    failed = []

    for num in article_numbers:
        jsonl_path = os.path.join(jsonl_base_dir, f"article_{num}.jsonl")
        if not os.path.exists(jsonl_path):
            print(f"⚠️  Missing file: {jsonl_path}")
            failed.append(num)
            continue

        try:
            _, paper_id, _, output_path = format_chunks_for_llm(jsonl_path)
            print(f"✅ Processed article_{num}.jsonl → {output_path}")
            processed += 1
        except Exception as e:
            print(f"❌ Error processing article_{num}.jsonl: {e}")
            failed.append(num)

    print("\n--- SUMMARY ---")
    print(f"Total processed: {processed}/{len(article_numbers)}")
    if failed:
        print(f"Failed ({len(failed)}): {failed}")
    else:
        print("All papers processed successfully!")
