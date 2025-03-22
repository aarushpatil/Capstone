from operator import itemgetter
from typing import Any, Dict, List
from termcolor import colored
import os, sys

from huggingface_hub import hf_hub_download
model_path = hf_hub_download(
    repo_id="TheBloke/CapybaraHermes-2.5-Mistral-7B-GGUF",
    filename="capybarahermes-2.5-mistral-7b.Q4_K_M.gguf",
    cache_dir="."
)

from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

file_paths = [
    r"C:\Users\ramig\OneDrive - Virginia Tech\CS 4624\Capstone\Capstone\backend\INTEGRATION_Manual_1.pdf",
    r"C:\Users\ramig\OneDrive - Virginia Tech\CS 4624\Capstone\Capstone\backend\INTEGRATION_Manual_2.pdf"
]

text_to_split = []

for file in file_paths:
    if file.endswith('.pdf'):
        print(file)
        loader = PyPDFLoader(file)
        pdf_file = loader.load()
        text_to_split.append(pdf_file)
    elif file.endswith('.doc') or file.endswith('.docx'):
        loader = Docx2txtLoader(file)
        doc_file = loader.load()
        text_to_split.append(doc_file)

text_splitted = []

splitter = RecursiveCharacterTextSplitter(
    separators=['\n\n', '\n'],
    chunk_size=1000,
    chunk_overlap=100
)

for t in text_to_split:
    text_chunks = splitter.split_documents(t)
    text_splitted += text_chunks

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

embeddings = HuggingFaceEmbeddings()
CHROMA_PATH = "./chroma_db"

if os.path.exists(CHROMA_PATH) and len(os.listdir(CHROMA_PATH)) > 0:
    print("Loading cached ChromaDB...")
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
else:
    print("Building new ChromaDB from scratch...")
    db = Chroma.from_documents(
        documents=text_splitted,
        embedding=embeddings,
        persist_directory=CHROMA_PATH
    )
    db.persist()
    print("ChromaDB cached.")

query = "Alternate Traffic Assignment/Routing methods options"
retriever = db.as_retriever(search_kwargs={"k": 1})
retrieved_docs = retriever.invoke(query)

print(retrieved_docs[0].page_content)
print(len(retrieved_docs))
