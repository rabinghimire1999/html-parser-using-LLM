"""
app.py
"""
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq


def split_documents(documents, chunk_size=1000, chunk_overlap=100):
    text_splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunked_documents = text_splitter.split_text(documents)
    return chunked_documents

def initialize_embeddings(model_name="BAAI/bge-base-en-v1.5"):
    embed_model = FastEmbedEmbeddings(model_name=model_name)
    return embed_model

def create_vectorstore(documents, embed_model):
    vectorstore = FAISS.from_texts(documents, embed_model)
    return vectorstore

def initialize_chat_model(temperature=0, model_name="llama3-8b-8192", api_key=None):
    chat_model = ChatGroq(temperature=temperature, model_name=model_name, api_key=api_key)
    return chat_model
