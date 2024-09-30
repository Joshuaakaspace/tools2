import os
from typing import List
from dotenv import load_dotenv
from ora import ora  # Assuming you have already installed and set up the ora library
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import json

# Load environment variables
load_dotenv()

# Ensure you have set OPENAI_API_KEY in your environment variables
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Split data based on two empty lines
def split_data(data: str, num_buckets: int):
    sections = data.split("\n\n")
    bucket_size = max(1, len(sections) // num_buckets)
    buckets = [sections[i:i + bucket_size] for i in range(0, len(sections), bucket_size)]
    return buckets

# Create prompt for LLM
def create_prompt(bucket_data):
    prompt = "Extract the following fields from the data into JSON format: name, case_number, details.\n\n"
    prompt += "\n".join(bucket_data)
    return prompt

# Call LLM for each bucket and add bucket index to the extracted data
def extract_data_from_llm(bucket_data, bucket_index):
    prompt = create_prompt(bucket_data)
    # Call LLM with the generated prompt
    response = ora.chat(msg=prompt)
    
    # Assuming the response is a list of dictionaries (the extracted data)
    if isinstance(response, list):
        # Add a "bucket_index" field to each extracted entry
        for entry in response:
            if isinstance(entry, dict):  # Ensure it's a dictionary before adding the field
                entry['bucket_index'] = bucket_index
                entry['source'] = 'llm'
        return response
    elif isinstance(response, dict):
        # If response is a single dict, wrap it in a list and add the bucket index
        response['bucket_index'] = bucket_index
        response['source'] = 'llm'
        return [response]
    else:
        print(f"Unexpected LLM response format: {response}")
        return []

# Refine the data by sending it back with original bucket data
def refine_data_with_llm(bucket_data, extracted_data):
    prompt = f"Refine the extraction based on the following data and correct any mistakes:\n\nOriginal Data:\n{bucket_data}\n\nExtracted Data:\n{extracted_data}"
    response = ora.chat(msg=prompt)
    
    # Assuming the response is a refined version of the extracted data
    if isinstance(response, list):
        return response
    elif isinstance(response, dict):
        return [response]
    else:
        return [response]

# Set up RAG
def setup_rag(data):
    # Create embeddings
    embeddings = OpenAIEmbeddings()

    # Create Chroma vector store
    vectorstore = Chroma.from_texts(
        texts=data.split("\n\n"),
        embedding=embeddings,
    )

    # Create a ChatOpenAI instance
    chat = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

    # Create custom prompt template for RAG
    rag_template = """
    You are an AI assistant tasked with extracting detailed information about cases from text content.
    Use the following piece of context to answer the question at the end. Extract the following fields: name, case_number, details.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.

    Context: {context}

    Question: {question}
    Answer: """

    RAG_PROMPT = PromptTemplate(template=rag_template, input_variables=["context", "question"])

    # Create the RetrievalQA chain
    qa = RetrievalQA.from_chain_type(
        llm=chat,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        return_source_documents=True,
        chain_type_kwargs={"prompt": RAG_PROMPT}
    )

    return qa

# Extract data using RAG
def extract_data_from_rag(qa, bucket_data, bucket_index):
    query = "Extract the name, case_number, and details from this text."
    result = qa({"query": query, "context": "\n".join(bucket_data)})
    
    try:
        extracted_data = json.loads(result['result'])
        if isinstance(extracted_data, dict):
            extracted_data = [extracted_data]
        
        for entry in extracted_data:
            entry['bucket_index'] = bucket_index
            entry['source'] = 'rag'
        
        return extracted_data
    except json.JSONDecodeError:
        print(f"Failed to parse RAG response as JSON: {result['result']}")
        return []

# Process data with both LLM and RAG approaches
def process_data(data: str, num_buckets: int):
    buckets = split_data(data, num_buckets)
    rag_qa = setup_rag(data)
    
    combined_extracted_json = []
    
    for index, bucket in enumerate(buckets):
        # LLM extraction
        llm_extracted = extract_data_from_llm(bucket, index)
        llm_refined = refine_data_with_llm(bucket, llm_extracted)
        for entry in llm_refined:
            entry['source'] = 'llm'
        
        # RAG extraction
        rag_extracted = extract_data_from_rag(rag_qa, bucket, index)
        
        # Combine results
        combined_extracted_json.extend(llm_refined)
        combined_extracted_json.extend(rag_extracted)
    
    return combined_extracted_json

# Example Usage
if __name__ == "__main__":
    # Simulate some large text data
    data = """name: John Doe
case_number: 12345
details: Some details here.

name: Jane Smith
case_number: 67890
details: Other details here.

name: Someone Else
case_number: 11121
details: Different details."""
    
    # Process data with both LLM and RAG approaches
    results = process_data(data, 3)
    
    # Print the results
    print(json.dumps(results, indent=2))