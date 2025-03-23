import os
from operator import itemgetter
from typing import Any, Dict, List
from termcolor import colored
import sys
from LLM.chapterSplitting import getManualChunks

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
manuals_dir = os.path.join(BASE_DIR, "./")  # Adjust if needed


def getTextSplitted():
    manual_chapters = getManualChunks()

    # Convert the chapter strings into LangChain Document objects
    from langchain.docstore.document import Document

    text_splitted = [Document(page_content=chapter) for chapter in manual_chapters]

    # If you still want to chunk the chapters further, you can use the RecursiveCharacterTextSplitter
    # on the chapter content.
    splitter = RecursiveCharacterTextSplitter(
        separators=['\n\n', '\n'],
        chunk_size=500,
        chunk_overlap=100
    )

    final_chunks = []
    for doc in text_splitted:
        chunks = splitter.split_documents([doc])
        final_chunks.extend(chunks)

    text_splitted = final_chunks
    return text_splitted


from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

embeddings = HuggingFaceEmbeddings()  # Uses all-mpnet-base-v2 by default.


persist_directory = "./chroma_db"  # Specify a directory to persist the database.
if os.path.exists(persist_directory):
    db = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    print("Loaded existing Chroma database.")
else:
    text_splitted = getTextSplitted()
    db = Chroma.from_documents(text_splitted, embeddings, persist_directory=persist_directory)
    print("Created new Chroma database.")
    db.persist() #persist to disk




# Create a retriever from the vector store.
retriever = db.as_retriever(search_kwargs={"k": 3}) #higher this number is the more info chroma will retrieve

# Define a custom prompt template to constrain the output.

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
from langchain.chains import RetrievalQA

llm = SafeLlamaCpp(
    model_path=model_path,
    n_ctx=10000,
    temperature=0.1,
    max_tokens=256,
    verbose=False
)


#**********This function doesnt use previous context yet. Need to make the prompt nice somehow*
#response quality went down by using context somehow
def get_llm_response(query: str, context = "") -> str:
    """
    Takes a user query string and returns the LLM's best answer 
    using the already-initialized qa_chain.
    """
    from langchain.prompts import PromptTemplate
    prompt_template = """
    You are to act like a traffic simulation assistant. 
    You will be given a question, previous chat history with the user, and information from a traffic simulation manual.
    You need to analyze this information from the manual and answer the question asked.

    If the information provided isn't enough to answer the question asked then respond with "I don't know"

    Answer consicely. 

    Context:
    {context}

    Question: {question}

    Answer:"""

    custom_prompt = PromptTemplate(
        input_variables=[context, query],
        template=prompt_template,
    )


    qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",  # "stuff" works well for short answers.
    retriever=retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": custom_prompt}
    )
    try:
        result = qa_chain.invoke({"query": query})
        
        print("Chroma DB Retrieved Documents: --------")
        for doc in result["source_documents"]:
            print("Page Content:")
            print(doc.page_content)
            print("Metadata:")
            print(doc.metadata)
            print("-" * 20)
        print("Chroma DB Retrieved Documents End: --------")

        return result["result"]
    except Exception as e:
        print("Error in get_llm_response:", str(e))
        return f"Error: {str(e)}"
