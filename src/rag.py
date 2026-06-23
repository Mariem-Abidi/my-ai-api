from dotenv import load_dotenv
load_dotenv()

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_huggingface import HuggingFaceEmbeddings
import os

DOCUMENTS_DIR = "documents"
CHROMA_DIR = "chroma_db"

def get_embeddings():
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def load_documents():
    docs = []
    for file in os.listdir(DOCUMENTS_DIR):
        if file.endswith(".txt"):
            loader = TextLoader(f"{DOCUMENTS_DIR}/{file}", encoding="utf-8")
            docs.extend(loader.load())
    return docs

def build_vectorstore():
    docs = load_documents()
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)
    vectorstore = Chroma.from_documents(chunks, get_embeddings(), persist_directory=CHROMA_DIR)
    return vectorstore

def get_vectorstore():
    if os.path.exists(CHROMA_DIR):
        return Chroma(persist_directory=CHROMA_DIR, embedding_function=get_embeddings())
    return build_vectorstore()

def retrieve_context(query, k=3):
    vectorstore = get_vectorstore()
    results = vectorstore.similarity_search(query, k=k)
    return "\n\n".join([doc.page_content for doc in results])