import os

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

CHROMA_DIR = "vector_db"

COLLECTION_NAME = "meeting_transcript"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"


# ---------------------------------------------------------
# EMBEDDINGS
# ---------------------------------------------------------

def get_embeddings():

    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={
            "device": "cpu"
        },
        encode_kwargs={
            "normalize_embeddings": True
        }
    )


# ---------------------------------------------------------
# BUILD VECTOR STORE
# ---------------------------------------------------------

def build_vector_store(
    transcript: str,
    collection_name: str = COLLECTION_NAME,
) -> Chroma:

    print("Building vector store...")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    chunks = splitter.split_text(transcript)

    print(f"Created {len(chunks)} chunks.")

    docs = [
        Document(
            page_content=chunk,
            metadata={
                "chunk_index": i
            }
        )
        for i, chunk in enumerate(chunks)
    ]

    print("Loading embedding model...")

    embeddings = get_embeddings()

    print("Creating Chroma vector store...")

    vector_store = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        collection_name=collection_name,
        persist_directory=CHROMA_DIR
    )

    print("Vector store created successfully.")

    return vector_store


# ---------------------------------------------------------
# LOAD EXISTING VECTOR STORE
# ---------------------------------------------------------

def load_vector_store(collection_name: str = COLLECTION_NAME) -> Chroma:

    print("Loading existing vector store...")

    embeddings = get_embeddings()

    vector_store = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR
    )

    print("Vector store loaded successfully.")

    return vector_store


# ---------------------------------------------------------
# RETRIEVER
# ---------------------------------------------------------

def get_retriever(
    vector_store: Chroma,
    k: int = 4
):

    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": k
        }
    )