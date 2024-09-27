from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

# Load the model and tokenizer from Hugging Face
model_name = "vectara/hallucination_evaluation_model"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name, trust_remote_code=True)

# Define a list of premise-hypothesis pairs
pairs = [
    ("The capital of France is Berlin.", "The capital of France is Paris."),
    ("I am in California", "I am in the United States."),
    ("Mark Wahlberg was a fan of Manny.", "Manny was a fan of Mark Wahlberg.")
]

# Prepare the input prompt
prompt_template = "<pad> Determine if the hypothesis is true given the premise?\n\nPremise: {premise}\n\nHypothesis: {hypothesis}"
input_pairs = [prompt_template.format(premise=p[0], hypothesis=p[1]) for p in pairs]

# Use the pipeline for text classification
classifier = pipeline("text-classification", model=model, tokenizer=tokenizer, top_k=None)

# Get the hallucination scores for both labels (hallucinated and consistent)
results = classifier(input_pairs)

# Extract the scores for the 'consistent' label
consistent_scores = [
    score['score'] for result in results for score in result if score['label'] == 'consistent'
]

print("Factual consistency scores:", consistent_scores)
