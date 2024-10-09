import json
from transformers import BertTokenizerFast, BertForTokenClassification
import torch

# Load the fine-tuned model and tokenizer
model_dir = "./ner_model_new_trail"  # Directory where the fine-tuned model is saved
tokenizer = BertTokenizerFast.from_pretrained(model_dir)
model = BertForTokenClassification.from_pretrained(model_dir)

# Set the model to evaluation mode
model.eval()

# Define a function to perform NER on a given text
def perform_ner_on_text(text):
    # Tokenize the input text
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, is_split_into_words=False)

    # Perform NER using the model
    with torch.no_grad():
        outputs = model(**inputs)

    # Get predictions (logits) and convert them into label IDs
    predictions = torch.argmax(outputs.logits, dim=2)

    # Simplified label list without B- and I- prefixes
    label_list = ["O", "NAME", "NAME", "ALSO_KNOWN_AS", "ALSO_KNOWN_AS", "DATE_OF_BIRTH", 
                  "DATE_OF_BIRTH", "OTHER_INFORMATION", "OTHER_INFORMATION"]

    # Convert token IDs back to tokens
    tokens = tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])

    # Convert predicted label IDs back to label names (without B- and I- prefixes)
    predicted_labels = [label_list[p.item()] for p in predictions[0]]

    # Filter out special tokens [CLS] and [SEP] and their corresponding labels
    filtered_tokens = []
    filtered_labels = []
    for token, label in zip(tokens, predicted_labels):
        if token not in ["[CLS]", "[SEP]"]:  # Skip [CLS] and [SEP] tokens
            filtered_tokens.append(token)
            filtered_labels.append(label)

    # Group subword tokens and their labels
    output = []
    current_entity = []
    current_label = None

    for i, (token, label) in enumerate(zip(filtered_tokens, filtered_labels)):
        if token.startswith("##"):  # Handle subword tokens
            current_entity[-1] = current_entity[-1] + token[2:]  # Merge subword with previous token
        elif label != "O":  # If it's an entity label
            if label == current_label:  # Continue collecting tokens for the same entity
                current_entity.append(token)
            else:
                # Check if the previous token was "[SEP]" and avoid adding a trailing ['NAME']
                if current_entity and not (i > 0 and filtered_labels[i - 1] == "O" and current_label == "NAME"):
                    # Finalize the previous entity
                    output.append(f"{' '.join(current_entity)} ['{current_label}']")
                # Start a new entity
                current_entity = [token]
                current_label = label
        else:
            # If it's "O" and we have a current entity, finalize it
            if current_entity:
                output.append(f"{' '.join(current_entity)} ['{current_label}']")
                current_entity = []
                current_label = None

    # Finalize the last entity if it exists
    if current_entity:
        output.append(f"{' '.join(current_entity)} ['{current_label}']")

    # Join the tokens into a sentence with spaces
    output_text = " ".join(output)
    return output_text

# Function to process a list of dictionaries in a JSON file for a specific field
def apply_ner_to_json_list(json_file_path, field_name, output_file_path):
    # Load the JSON file
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    # Check if the data is a list
    if not isinstance(data, list):
        raise ValueError("The JSON file should contain a list of dictionaries.")

    # Iterate through each dictionary in the list and update the specified field
    field_exists = False
    for item in data:
        if isinstance(item, dict) and field_name in item:
            field_exists = True
            # Perform NER on the specified field
            item[f"{field_name}_ner"] = perform_ner_on_text(item[field_name])
        else:
            print(f"Skipping item: {item} (either not a dictionary or missing the field '{field_name}')")

    # Check if the specified field was found in at least one dictionary
    if not field_exists:
        raise ValueError(f"The field '{field_name}' does not exist in any of the dictionaries in the JSON file.")

    # Save the updated data back to a new JSON file
    with open(output_file_path, 'w') as file:
        json.dump(data, file, indent=4)

    print(f"NER results have been saved to {output_file_path}")

# Example usage
# Assuming the JSON file contains a list of dictionaries with a 'name' field
json_file_path = 'input_data.json'
output_file_path = 'output_data_with_ner.json'
field_name = 'name'

apply_ner_to_json_list(json_file_path, field_name, output_file_path)
