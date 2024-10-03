# Import necessary libraries
import os
from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
import spacy
import neuralcoref
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

# Ensure you've set your OpenAI API key in your environment variables
os.environ["OPENAI_API_KEY"] = "your-api-key-here"

# Initialize components
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
)
embeddings = OpenAIEmbeddings()
llm = OpenAI(temperature=0)

# Setup spaCy with neuralcoref
nlp = spacy.load("en_core_web_sm")
neuralcoref.add_to_pipe(nlp)

# Setup prompt template
entity_prompt = PromptTemplate(
    input_variables=["name", "context"],
    template="""From the provided context, extract details about {name} who is explicitly listed as sanctioned.
    Ignore any mentions of other individuals or entities not under sanctions, even if their details are provided.
    Extract the following fields into a JSON format only, using the exact structure as below:
    {{"name":'{name}', "DOB":'', "POB":'', "Position":'', "rank":'', "nationality":'', "gender":'', "passport_number":'',
    "reasons":'', "date_of_listing":'', "Address":'', "Also known As":'', "other_details":''}}
    If no relevant information is available for a field, leave it blank.
    Important Guidelines:
    Accuracy is critical: Ensure all details are captured accurately and completely. Do not capture incorrect or inferred information.
    Context: {context}"""
)

# Load and preprocess the text
with open('sanctions_data.txt', 'r') as file:
    original_text = file.read()

# Perform coreference resolution
doc = nlp(original_text)
preprocessed_text = doc._.coref_resolved

# Create vector store
docs = text_splitter.create_documents([preprocessed_text])
vector_store = Chroma.from_documents(docs, embeddings)

# Create QA chain
qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=vector_store.as_retriever())

# Split data into buckets
num_buckets = 5
sections = preprocessed_text.split("\n")
bucket_size = max(1, len(sections) // num_buckets)
overlap_size = bucket_size // 2

buckets = []
for i in range(0, len(sections), bucket_size - overlap_size):
    bucket = sections[i:i + bucket_size]
    if bucket:
        bucket[0] = 'INCOMPLETE----' + bucket[0]
    buckets.append(bucket)
    if len(bucket) < bucket_size:
        break

# Extract names from buckets
def extract_names(bucket_data):
    prompt = """From the provided content, extract ONLY the names of individuals or entities who are explicitly listed as
    sanctioned. Provide the output as a Python list of strings. Do not include any other information or explanation."""
    prompt += "\n".join(bucket_data)
    response = llm(prompt)
    try:
        return json.loads(response.replace("'", '"'))
    except json.JSONDecodeError:
        return []

all_names = set()
with ThreadPoolExecutor(max_workers=5) as executor:
    future_to_bucket = {executor.submit(extract_names, bucket): bucket for bucket in buckets}
    for future in as_completed(future_to_bucket):
        try:
            names = future.result()
            all_names.update(names)
        except Exception as exc:
            print(f'A bucket generated an exception: {exc}')

print("Extracted Names:", all_names)

# Extract entity details
def extract_entity_details(name: str):
    result = qa_chain.run(entity_prompt.format(name=name, context=f"Information about {name}"))
    try:
        return json.loads(result)
    except json.JSONDecodeError:
        return {"name": name, "error": "Failed to extract details"}

results = []
with ThreadPoolExecutor(max_workers=5) as executor:
    future_to_name = {executor.submit(extract_entity_details, name): name for name in all_names}
    for future in as_completed(future_to_name):
        name = future_to_name[future]
        try:
            result = future.result()
            results.append(result)
        except Exception as exc:
            print(f'Name {name} generated an exception: {exc}')

# Print results
print("\nExtracted Entity Details:")
for result in results:
    print(json.dumps(result, indent=2))