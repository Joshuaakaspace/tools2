!ollama pull llama3
!ollama pull nomic-embed-text
# install poppler id strategy is hi_res


import os
from unstructured.partition.pdf import partition_pdf
from unstructured.chunking.title import chunk_by_title
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.chat_models import ChatOllama
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


#  preprocess pdfs inside pdfs directory (whatever PDFs you like)
def preprocess_pdfs(directory):
  elements = []
  for root, _, files in os.walk(directory):
    for file in files:
        if file.endswith(".pdf"):
            elems = partition_pdf(filename=os.path.join(root,file), languages=['eng'], strategy="fast")
            elements.extend(elems)
  return elements


pdf_elements = preprocess_pdfs("pdfs")


# chunking
chunked_elements = chunk_by_title(pdf_elements)

documents = []
for element in chunked_elements:
    metadata = element.metadata.to_dict()
    documents.append(Document(page_content=element.text,
                              metadata=metadata))

print(documents)

db = FAISS.from_documents(documents, OllamaEmbeddings(model="nomic-embed-text",show_progress=True))
retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 4})

# Set up the local model:
local_model = "llama3"
llm = ChatOllama(model=local_model, num_predict=400,
                 stop=["<|start_header_id|>", "<|end_header_id|>", "<|eot_id|>"])

# Set up the RAG chain:
prompt_template = """
<|start_header_id|>user<|end_header_id|>
Responds user questions taking into accoun the given context, give a precise 
answer.
Question: {question}
Context: {context}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""

prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=prompt_template,
)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# Querying the LLM (oviously to test here you must ask a relevant question of your data)
question = "What is car?"
print(question)
print(rag_chain.invoke(question))