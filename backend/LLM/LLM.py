# Import necessary modules for document loading, text splitting, embeddings, vector storage, and LLM integration.
from operator import itemgetter
from typing import Any, Dict, List
from termcolor import colored
import os, sys

# Download the local model from Hugging Face Hub
from huggingface_hub import hf_hub_download
model_path = hf_hub_download(
    repo_id="TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF",
    filename="tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
    cache_dir="."
)

# Document loaders and text splitting
from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Dynamically determine the current script directory and set the manuals directory.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
manuals_dir = os.path.join(BASE_DIR, "../")  # Adjust if needed

# List of document file names.
file_names = ["INTEGRATION_Manual_1.pdf", "INTEGRATION_Manual_2.pdf"]

# Create full file paths.
file_paths = [os.path.join(manuals_dir, f) for f in file_names]

# Load the documents.
text_to_split = []
for file in file_paths:
    if file.endswith('.pdf'):
        print("Loading:", file)
        loader = PyPDFLoader(file)
        pdf_file = loader.load()
        text_to_split.append(pdf_file)
    elif file.endswith('.doc') or file.endswith('.docx'):
        loader = Docx2txtLoader(file)
        doc_file = loader.load()
        text_to_split.append(doc_file)

# Split the loaded documents into chunks.
text_splitted = []
splitter = RecursiveCharacterTextSplitter(
    separators=['\n\n', '\n'],
    chunk_size=500,
    chunk_overlap=100
)
for t in text_to_split:
    text_chunks = splitter.split_documents(t)
    text_splitted += text_chunks

# Create embeddings and build the vector store.
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

embeddings = HuggingFaceEmbeddings()  # Uses all-mpnet-base-v2 by default.
db = Chroma.from_documents(text_splitted, embeddings)

# Create a retriever from the vector store.
retriever = db.as_retriever(search_kwargs={"k": 1})

# Define a custom prompt template to constrain the output.
from langchain.prompts import PromptTemplate
prompt_template = """
You are a concise and factual assistant. Use ONLY the context provided below to answer the question.
Do not include any additional questions, extraneous text, or Q&A pairs.
Provide a single, clear, and direct answer. Do not add notes following the question as well.

Context:
{context}

Question: {question}

Answer:"""

custom_prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=prompt_template,
)

# Patch the LlamaCpp class to avoid the destructor error.
from langchain_community.llms import LlamaCpp as BaseLlamaCpp

class SafeLlamaCpp(BaseLlamaCpp):
    def __del__(self):
        try:
            # Attempt to call the underlying client's destructor if available.
            if hasattr(self, "client") and hasattr(self.client, "__del__"):
                self.client.__del__()
        except Exception:
            pass

# Integrate the local LLM into a RetrievalQA chain using the patched class.
llm = SafeLlamaCpp(
    model_path=model_path,
    n_ctx=2048,
    temperature=0.7,
    max_tokens=512,
    verbose=True
)

from langchain.chains import RetrievalQA

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",  # "stuff" works well for short answers.
    retriever=retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": custom_prompt}
)

# Query the chain using the new invoke() method.
query = "How does setting the en-route path update interval to 0 affect vehicle routing for different routing methods?"
result = qa_chain.invoke({"query": query})

# Print out only the answer.
print("Answer:")
print(result["result"])

# Note: The explicit llm.close() call has been removed since SafeLlamaCpp handles cleanup.
