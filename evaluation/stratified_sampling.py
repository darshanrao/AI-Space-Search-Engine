import json
import random
from collections import defaultdict

# Set random seed for reproducibility
random.seed(42)

# Read the categorized papers
with open('evaluation/data/nasa_bioscience_categorized.json', 'r') as f:
    data = json.load(f)

# Extract metadata and papers
total_papers = data['metadata']['total_papers']
papers = data['papers']

# Group papers by subfield
subfield_papers = defaultdict(list)
for paper in papers:
    subfield_papers[paper['subfield']].append(paper)

# Calculate subfield counts
subfield_counts = {subfield: len(papers) for subfield, papers in subfield_papers.items()}

print("Subfield Distribution:")
print("-" * 60)
for subfield, count in sorted(subfield_counts.items(), key=lambda x: x[1], reverse=True):
    percentage = (count / total_papers) * 100
    print(f"{subfield:30s}: {count:3d} papers ({percentage:5.2f}%)")
print("-" * 60)
print(f"Total: {total_papers} papers\n")

# Target total samples
target_total = 48

# Calculate proportional samples per subfield
min_samples_per_subfield = 2
subfield_samples = {}

# First pass: calculate proportional samples
for subfield, count in subfield_counts.items():
    proportional = round((count / total_papers) * target_total)
    # Ensure minimum of 2 papers per subfield
    subfield_samples[subfield] = max(min_samples_per_subfield, proportional)

# Adjust to hit target total
current_total = sum(subfield_samples.values())
print(f"Initial allocation: {current_total} papers")

# If we're over target, reduce from largest subfields
if current_total > target_total:
    excess = current_total - target_total
    # Sort by sample size (descending) and reduce
    sorted_subfields = sorted(subfield_samples.items(), key=lambda x: x[1], reverse=True)
    for subfield, _ in sorted_subfields:
        if excess == 0:
            break
        if subfield_samples[subfield] > min_samples_per_subfield:
            reduction = min(excess, subfield_samples[subfield] - min_samples_per_subfield)
            subfield_samples[subfield] -= reduction
            excess -= reduction

# If we're under target, add to largest subfields
elif current_total < target_total:
    shortage = target_total - current_total
    sorted_subfields = sorted(subfield_samples.items(), key=lambda x: subfield_counts[x[0]], reverse=True)
    for subfield, _ in sorted_subfields:
        if shortage == 0:
            break
        # Only add if we won't exceed available papers
        if subfield_samples[subfield] < subfield_counts[subfield]:
            subfield_samples[subfield] += 1
            shortage -= 1

final_total = sum(subfield_samples.values())
print(f"Final allocation: {final_total} papers\n")

print("Sampling Plan:")
print("-" * 60)
for subfield in sorted(subfield_samples.keys()):
    count = subfield_counts[subfield]
    sample = subfield_samples[subfield]
    percentage = (sample / final_total) * 100
    print(f"{subfield:30s}: {sample:2d} / {count:3d} papers ({percentage:5.2f}% of sample)")
print("-" * 60)
print(f"Total: {final_total} papers\n")

# Perform stratified random sampling
sampled_papers = []
for subfield, sample_size in subfield_samples.items():
    available_papers = subfield_papers[subfield]
    sampled = random.sample(available_papers, min(sample_size, len(available_papers)))
    sampled_papers.extend(sampled)

# Create output structure
output = {
    "metadata": {
        "total_sampled": len(sampled_papers),
        "original_total": total_papers,
        "sampling_method": "stratified_random",
        "random_seed": 42,
        "target_samples": target_total,
        "sampling_date": data['metadata']['categorization_date'],
        "subfield_distribution": {}
    },
    "papers": sampled_papers
}

# Add subfield distribution to metadata
for subfield, sample_size in subfield_samples.items():
    output['metadata']['subfield_distribution'][subfield] = {
        "sampled": sample_size,
        "total": subfield_counts[subfield],
        "percentage_of_sample": round((sample_size / final_total) * 100, 2)
    }

# Save to output file
output_path = 'evaluation/data/sampled_papers_for_queries.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"✓ Sampling complete!")
print(f"✓ Saved {len(sampled_papers)} papers to {output_path}")
print(f"\nSample verification:")
for subfield in sorted(subfield_samples.keys()):
    sampled_count = sum(1 for p in sampled_papers if p['subfield'] == subfield)
    print(f"  {subfield:30s}: {sampled_count} papers")
