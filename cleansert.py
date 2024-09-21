def split_data(data: str, num_buckets: int, overlap_size: int):
    sections = data.split('\n')
    bucket_size = max(1, len(sections) // num_buckets)
    buckets = []
    
    for i in range(0, len(sections), bucket_size - overlap_size):
        # Collect the paragraphs to form a bucket
        bucket = sections[i:i + bucket_size]
        current_text = '\n'.join(bucket)
        
        # Check if the current bucket is larger than the token limit (approximated by characters)
        if len(current_text) > 3500:  # This check may need adjustment based on the actual token size
            # Split the text further into smaller parts if too large
            smaller_buckets = split_large_bucket(current_text)
            buckets.extend(smaller_buckets)
        else:
            buckets.append(current_text)
        
        if len(bucket) < bucket_size:
            break

    return buckets

def split_large_bucket(text: str):
    # This function splits a large bucket into smaller parts without exceeding the token limit
    words = text.split()
    max_length = 3500  # Max characters, not tokens (approximation)
    small_buckets = []
    current_bucket = []
    
    for word in words:
        if sum(len(w) + 1 for w in current_bucket + [word]) > max_length:
            small_buckets.append(' '.join(current_bucket))
            current_bucket = [word]
        else:
            current_bucket.append(word)
    
    # Add the last bucket if it contains any words
    if current_bucket:
        small_buckets.append(' '.join(current_bucket))
    
    return small_buckets

# Usage of the function
data = "your_large_text_here"
num_buckets = 30
sections = data.split("\n")
bucket_size = max(1, len(sections) // num_buckets)
overlap_size = bucket_size // 2

buckets = split_data(data, num_buckets, overlap_size)
bucketed_extracted_json = []

for bucket in buckets:
    extracted_json = extract_data_from_llm(bucket)
    bucketed_extracted_json.append(extracted_json)
