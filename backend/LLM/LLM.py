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

# Define available models
def get_model_path(model_name: str) -> str:
    models = {
        "tinyllama": {
            "repo_id": "TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF",
            "filename": "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
        },
        "mistral": {
            "repo_id": "TheBloke/Mistral-7B-Instruct-v0.1-GGUF",
            "filename": "mistral-7b-instruct-v0.1.Q8_0.gguf"
        },
        "wizardlm": {
            "repo_id": "TheBloke/WizardLM-13B-V1.2-GGUF",
            "filename": "wizardlm-13b-v1.2.Q8_0.gguf"
        }
    }

    if model_name not in models:
        print(colored(f"Unknown model '{model_name}'. Choose from: {list(models.keys())}", "red"))
        sys.exit(1)
    cfg = models[model_name]
    print(colored(f"Downloading model '{model_name}' from {cfg['repo_id']}...", "yellow"))
    return hf_hub_download(
        repo_id=cfg["repo_id"],
        filename=cfg["filename"],
        cache_dir="."
    )

# Parse CLI args for model selection
parser = argparse.ArgumentParser(description="Run RetrievalQA with selected LLM model")
parser.add_argument(
    "--model",
    choices=["tinyllama", "mistral", "wizardlm"],
    default="tinyllama",
    help="Model to use"
)
args = parser.parse_args()

# Download selected model
model_path = get_model_path(args.model)

# Dynamically determine the current script directory and set the manuals directory.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
manuals_dir = os.path.join(BASE_DIR, "./") 


def getTextSplitted():
    from langchain.docstore.document import Document
    from langchain.text_splitter import RecursiveCharacterTextSplitter

    manual_chapters = getManualChunks()
    splitter = RecursiveCharacterTextSplitter(
        separators=['\n\n', '\n'],
        chunk_size=500,
        chunk_overlap=30
    )

    final_chunks = []
    for chapter in manual_chapters:
        doc = Document(page_content=chapter)
        chunks = splitter.split_documents([doc])
        final_chunks.extend(chunks)

    return final_chunks



from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

embeddings = HuggingFaceEmbeddings()


persist_directory = "./chroma_db"  # Specify a directory to persist the database.
if os.path.exists(persist_directory):
    db = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    print("Loaded existing Chroma database.")
else:
    text_splitted = getTextSplitted()
    db = Chroma.from_documents(text_splitted, embeddings, persist_directory=persist_directory)
    print("Created new Chroma database.")
    db.persist() # persist to disk




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

llm = SafeLlamaCpp( #for tinyllama
    model_path=model_path,
    n_ctx=2048,
    temperature=0.1,
    max_tokens=256,
    verbose=False
)

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
        input_variables=["context", "query"],
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

        output = "=" * 55
        output += " Chroma DB Retrieved Documents: \n"
        for doc in result["source_documents"]:
            output += "Page Content:\n"
            output += f"{doc.page_content}\n"
            output += "Metadata:\n"
            output += f"{doc.metadata}\n"
            output += "-" * 20 + "\n"

        output += ("=" * 55)

        retVal = result["result"] + "\n\n\n\n\n" + output
        return retVal
    except Exception as e:
        print("Error in get_llm_response:", str(e))
        return f"Error: {str(e)}"
