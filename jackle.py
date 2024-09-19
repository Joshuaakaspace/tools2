import spacy
import json
from fuzzywuzzy import fuzz

# Load spaCy's pre-trained model for NER
nlp = spacy.load('en_core_web_sm')

# Function to extract names (entities) from HTML text
def extract_names_from_html(text):
    doc = nlp(text)
    names = []
    
    # Iterate over sentences in the document
    for sent in doc.sents:
        # Check if the first token in the sentence is a 'PERSON' entity
        if sent.ents:
            for ent in sent.ents:
                if ent.label_ == 'PERSON':
                    # Only consider the entity if it's at the beginning of the sentence or paragraph
                    if ent.start == 0 or ent.text == sent[0].text:  # Entity appears first
                        names.append((ent.text, 'name'))
                    break  # Stop after the first valid 'PERSON' entity in the sentence
    return names

# Function to extract names (entities) from the LLM JSON output
def extract_names_from_json(llm_output):
    names = []
    for entry in llm_output:
        if 'name' in entry:
            names.append((entry['name'], 'name'))
    return names

# Function to compare names from both sources (HTML and LLM output)
def compare_names(ground_truth, extracted):
    true_positives = 0
    false_negatives = 0
    false_positives = 0
    
    gt_matched = []  # Track matched ground truth entities
    ext_matched = []  # Track matched extracted entities

    # Check true positives by fuzzy matching between ground truth and extracted entities
    for gt_entity in ground_truth:
        matched = False
        for ext_entity in extracted:
            if fuzz.ratio(gt_entity[0], ext_entity[0]) > 85:  # Compare text with fuzzy matching
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

    return true_positives, false_positives, false_negatives

# Function to calculate precision, recall, and F1-score
def calculate_metrics(true_positives, false_positives, false_negatives):
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    return precision, recall, f1_score

# Example usage

html_text = """
John Doe is the CEO of XYZ Corporation. He was born on January 1, 1980, in the USA.
Doe joined XYZ Corporation in 2010. Under his leadership, the company has grown significantly.
Jane Doe, on the other hand, serves as the Chief Operating Officer (COO) at ABC Corporation.
"""

llm_output_json = '''
[
    {"name": "John Doe", "DOB": "01-01-1980", "POB": "USA", "position": "CEO", "nationality": "American"},
    {"name": "Jane Doe", "DOB": "02-02-1975", "POB": "UK", "position": "COO", "nationality": "British"}
]
'''

# Extract names from HTML text
html_names = extract_names_from_html(html_text)

# Load LLM output from JSON
llm_output = json.loads(llm_output_json)

# Extract names from LLM output
llm_names = extract_names_from_json(llm_output)

# Run the comparison
tp, fp, fn = compare_names(html_names, llm_names)

# Calculate precision, recall, and F1-score
precision, recall, f1_score = calculate_metrics(tp, fp, fn)

print(f"Precision: {precision:.2f}")
print(f"Recall: {recall:.2f}")
print(f"F1 Score: {f1_score:.2f}")
