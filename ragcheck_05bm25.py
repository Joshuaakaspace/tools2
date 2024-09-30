import os
from dotenv import load_dotenv
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.retrievers import EnsembleRetriever
from langchain.retrievers import BM25Retriever
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import json
import uuid

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

def process_chunk(chunk, retriever, qa):
    # Extract entities from the chunk
    entities_query = "List all important entities (people, organizations, locations) mentioned in this text. Format the output as a JSON object with entity types as keys and lists of entities as values."
    entities_result = qa({"query": entities_query, "context": chunk.page_content})
    entities = json.loads(entities_result['result'])

    details = {}
    for entity_type, entity_list in entities.items():
        for entity in entity_list:
            query = f"Provide a detailed description of {entity}, including their role, significance, and any other relevant information."
            result = qa({"query": query, "context": chunk.page_content})
            if entity not in details:
                details[entity] = []
            details[entity].append({
                "description": result['result'],
                "source": chunk.metadata['source']
            })

    return entities, details

def process_text_file(file_path):
    # Load the text file
    loader = TextLoader(file_path)
    document = loader.load()

    # Split the text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(document)

    # Create embeddings
    embeddings = OpenAIEmbeddings()

    # Create a unique identifier for this file's Chroma collection
    collection_name = f"collection_{uuid.uuid4().hex}"

    # Create Chroma vector store
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=collection_name
    )

    # Create BM25 retriever
    bm25_retriever = BM25Retriever.from_documents(chunks)
    bm25_retriever.k = 3  # Set to retrieve top 3 matches

    # Create EnsembleRetriever
    ensemble_retriever = EnsembleRetriever(
        retrievers=[vectorstore.as_retriever(search_kwargs={"k": 3}), bm25_retriever],
        weights=[0.5, 0.5]
    )

    # Create a ChatOpenAI instance
    chat = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

    # Create a custom prompt template
    template = """
    You are an AI assistant tasked with extracting detailed information about entities and individuals from text content.
    Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.

    Context: {context}

    Question: {question}
    Answer: """

    QA_PROMPT = PromptTemplate(template=template, input_variables=["context", "question"])

    # Create the RetrievalQA chain
    qa = RetrievalQA.from_chain_type(
        llm=chat,
        chain_type="stuff",
        retriever=ensemble_retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": QA_PROMPT}
    )

    all_entities = {}
    all_details = {}

    # Process each chunk
    for chunk in chunks:
        entities, details = process_chunk(chunk, ensemble_retriever, qa)
        
        # Merge entities
        for entity_type, entity_list in entities.items():
            if entity_type not in all_entities:
                all_entities[entity_type] = set()
            all_entities[entity_type].update(entity_list)
        
        # Merge details
        for entity, entity_details in details.items():
            if entity not in all_details:
                all_details[entity] = []
            all_details[entity].extend(entity_details)

    # Convert sets to lists for JSON serialization
    for entity_type in all_entities:
        all_entities[entity_type] = list(all_entities[entity_type])

    # Clean up the Chroma collection
    vectorstore.delete_collection()

    return {
        "file": file_path,
        "entities": all_entities,
        "details": all_details
    }

def main():
    text_files = [
        "path/to/your/file1.txt",
        "path/to/your/file2.txt",
        # Add more file paths as needed
    ]
    
    results = []
    for file_path in text_files:
        result = process_text_file(file_path)
        results.append(result)
    
    with open("entity_extraction_results.json", "w", encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()