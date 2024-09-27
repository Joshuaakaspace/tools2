from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

# Load the Vectara Hallucination Evaluation Model and tokenizer
hem_model_name = "vectara/hallucination_evaluation_model"
hem_tokenizer = AutoTokenizer.from_pretrained(hem_model_name)
hem_model = AutoModelForSequenceClassification.from_pretrained(hem_model_name, trust_remote_code=True)

# Add hallucination check with Vectara model
def check_hallucination(input_text, output_text):
    prompt = f"<pad> Determine if the hypothesis is true given the premise?\n\nPremise: {input_text}\n\nHypothesis: {output_text}"
    
    # Use the pipeline for text classification
    classifier = pipeline("text-classification", model=hem_model, tokenizer=hem_tokenizer, top_k=None)
    
    # Get the factual consistency score
    result = classifier(prompt)[0]  # Assume it returns the top label score
    consistency_score = result['score'] if result['label'] == 'consistent' else 0
    
    return consistency_score

# Call LLM for each bucket and validate with hallucination check
def extract_data_from_llm(bucket_data):
    prompt = create_prompt(bucket_data)
    
    # Call LLM with the generated prompt
    response = ora.chat(msg=prompt)
    
    # Assuming the response is already a dictionary
    if isinstance(response, dict):
        # Convert bucket_data (input) to a single text block for comparison
        input_text = "\n".join(bucket_data)
        output_text = response.get("text", "")
        
        # Check for hallucination
        consistency_score = check_hallucination(input_text, output_text)
        
        if consistency_score > 0.75:  # Set a threshold for factual consistency
            return response
        else:
            print(f"Hallucination detected with consistency score: {consistency_score}. Ignoring output.")
            return []
    else:
        print(f"Unexpected LLM response format: {response}")
        return []

# Rest of the code remains unchanged...
