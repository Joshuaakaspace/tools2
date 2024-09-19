import json
from fuzzywuzzy import fuzz

# Function to extract entities from JSON (both for ground truth and LLM output)
def extract_names_from_json(json_data):
    entities = []
    for entry in json_data:
        if 'name' in entry:
            entities.append((entry['name'], 'name'))
        if 'DOB' in entry:
            entities.append((entry['DOB'], 'DOB'))
        if 'POB' in entry:
            entities.append((entry['POB'], 'POB'))
        # Add other fields as needed, like 'nationality', etc.
    return entities

# Compare entities using fuzzy matching
def compare_entities(ground_truth, extracted):
    """
    Compare two lists of entities using fuzzy matching.
    Returns true positives, false positives, and false negatives.
    """
    true_positives = 0
    false_negatives = 0
    false_positives = 0
    
    gt_matched = []  # Track matched ground truth entities
    ext_matched = []  # Track matched extracted entities

    # Check true positives by fuzzy matching between ground truth and extracted entities
    for gt_entity in ground_truth:
        matched = False
        for ext_entity in extracted:
            if fuzz.ratio(gt_entity[0], ext_entity[0]) > 85 and gt_entity[1] == ext_entity[1]:  # Compare text and label
                true_positives += 1
                gt_matched.append(gt_entity)
                ext_matched.append(ext_entity)
                matched = True
                break
        if not matched:
            false_negatives += 1

    # Check false positives (extracted entities not in ground truth)
    for ext_entity in extracted:
        if ext_entity not in ext_matched:
            false_positives += 1

    # Return the counts for true positives, false positives, and false negatives
    return true_positives, false_positives, false_negatives

# Calculate precision, recall, and F1-score
def calculate_metrics(true_positives, false_positives, false_negatives):
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    return precision, recall, f1_score

# Example ground truth JSON
ground_truth_json = '''
[
    {"name": "John Doe", "DOB": "01-Jan-1980", "POB": "USA"},
    {"name": "Jane Doe", "DOB": "02-Feb-1975", "POB": "UK"}
]
'''

# Example LLM output JSON
llm_output_json = '''
[
    {"name": "John Doe", "DOB": "01-01-1980", "POB": "United States"},
    {"name": "Jane Doe", "DOB": "02-02-1975", "POB": "UK"}
]
'''

# Load the JSON data
ground_truth = json.loads(ground_truth_json)
llm_output = json.loads(llm_output_json)

# Extract entities from both JSON files
ground_truth_entities = extract_names_from_json(ground_truth)
llm_output_entities = extract_names_from_json(llm_output)

# Run the comparison
tp, fp, fn = compare_entities(ground_truth_entities, llm_output_entities)

# Calculate precision, recall, and F1-score
precision, recall, f1_score = calculate_metrics(tp, fp, fn)

print(f"Precision: {precision:.2f}")
print(f"Recall: {recall:.2f}")
print(f"F1 Score: {f1_score:.2f}")
