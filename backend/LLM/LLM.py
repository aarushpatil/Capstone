# Import necessary modules and libraries for document loading, text splitting, embeddings, vector storage, and other functionalities.
from operator import itemgetter
from typing import Any, Dict, List
from termcolor import colored
import os, sys

# from google.colab import output
# output.enable_custom_widget_manager()

from huggingface_hub import hf_hub_download
model_path = hf_hub_download(repo_id="TheBloke/CapybaraHermes-2.5-Mistral-7B-GGUF", filename="capybarahermes-2.5-mistral-7b.Q4_K_M.gguf", cache_dir=".")

from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

file_paths = [ "/Users/aarushpatil/Code/Capstone/Manuals/INTEGRATION_Manual_1.pdf", "/Users/aarushpatil/Code/Capstone/Manuals/INTEGRATION_Manual_2.pdf"]

# Iterate through a list of file paths and load text content from PDF, DOC, or DOCX files
text_to_split = []

for file in file_paths:
    if file.endswith('.pdf'):
        print(file)
        # Load text content from a PDF file using PyPDFLoader
        loader = PyPDFLoader(file)
        pdf_file = loader.load()
        text_to_split.append(pdf_file)
    elif file.endswith('.doc') or file.endswith('.docx'):
        # Load text content from a DOC or DOCX file using Docx2txtLoader
        loader = Docx2txtLoader(file)
        doc_file = loader.load()
        text_to_split.append(doc_file)



# Initialize an empty list to store the split text chunks
text_splitted = []

# splitter = SentenceTransformersTokenTextSplitter(chunk_overlap=200)

# Choose a text splitter strategy
splitter=RecursiveCharacterTextSplitter(separators=['\n\n', '\n'],
                                    chunk_size=1000,
                                    chunk_overlap=100)


# Iterate through the loaded text content and split it using the chosen text splitter
for t in text_to_split:
    text_chunks = splitter.split_documents(t)
    text_splitted+=  text_chunks


# print(text_splitted)



from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

embeddings = HuggingFaceEmbeddings() # all-mpnet-base-v2

# from google.colab import output
# output.enable_custom_widget_manager()


db=Chroma.from_documents(text_splitted, embeddings)


query = "Alternate Traffic Assignment/Routing methods options"
retriever = db.as_retriever(search_kwargs={"k": 1})
retrieved_docs = retriever.invoke(query)

print(retrieved_docs[0].page_content)
# print("-----------")
# print(retrieved_docs[1].page_content)
# print("-----------")
# print(retrieved_docs[2].page_content)

print(len(retrieved_docs))