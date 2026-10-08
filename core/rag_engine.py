from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import (
    RunnablePassthrough,
    RunnableLambda
)

from core.vector_store import (
    COLLECTION_NAME,
    build_vector_store,
    load_vector_store,
    get_retriever
)

import os
from dotenv import load_dotenv


load_dotenv()


# =========================================================
# GROQ LLM
# =========================================================

def get_llm():

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set in environment / .env"
        )

    return ChatGroq(
        model="openai/gpt-oss-20b",
        api_key=api_key,
        temperature=0.3
    )


# =========================================================
# FORMAT RETRIEVED DOCUMENTS
# =========================================================

def format_docs(docs):

    return "\n\n".join(
        [
            doc.page_content
            for doc in docs
        ]
    )


# =========================================================
# BUILD RAG CHAIN FROM NEW TRANSCRIPT
# =========================================================

def build_rag_chain(
    transcript: str,
    collection_name: str = COLLECTION_NAME,
):

    print("Building vector store...")

    vector_store = build_vector_store(transcript, collection_name)

    print("Creating retriever...")

    retriever = get_retriever(
        vector_store,
        k=4
    )

    llm = get_llm()

    # -----------------------------------------------------
    # RAG PROMPT
    # -----------------------------------------------------

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are an expert meeting assistant.

Answer the user's question based ONLY on the meeting
transcript context provided below.

If the answer is not found in the context, say:

"I could not find this information in the meeting transcript."

Always be concise and precise.

Do not make up information.

If quoting someone, mention it clearly.

Context from meeting transcript:

{context}
"""
            ),
            (
                "human",
                "{question}"
            ),
        ]
    )

    # -----------------------------------------------------
    # RAG CHAIN
    # -----------------------------------------------------

    rag_chain = (
        {
            "context": retriever | RunnableLambda(format_docs),
            "question": RunnablePassthrough()
        }
        | prompt| llm | StrOutputParser()
    )

    return rag_chain


# =========================================================
# LOAD EXISTING RAG VECTOR STORE
# =========================================================

def load_rag_chain(collection_name: str = COLLECTION_NAME):

    print("Loading vector store...")

    vector_store = load_vector_store(collection_name)

    print("Creating retriever...")

    retriever = get_retriever(
        vector_store,
        k=4
    )

    llm = get_llm()

    # -----------------------------------------------------
    # RAG PROMPT
    # -----------------------------------------------------

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are an expert meeting assistant.

Answer the user's question based ONLY on the meeting
transcript context provided below.

If the answer is not found in the context, say:

"I could not find this information in the meeting transcript."

Always be concise and precise.

Do not make up information.

If quoting someone, mention it clearly.

Context from meeting transcript:

{context}
"""
            ),
            (
                "human",
                "{question}"
            ),
        ]
    )

    # -----------------------------------------------------
    # RAG CHAIN
    # -----------------------------------------------------

    rag_chain = (
        {
            "context": retriever | RunnableLambda(format_docs),
            "question": RunnablePassthrough()
        }
        | prompt | llm | StrOutputParser()
    )

    return rag_chain


# =========================================================
# ASK QUESTION
# =========================================================

def ask_question(rag_chain, question: str) -> str:

    print(f"\nQuestion: {question}")

    answer = rag_chain.invoke(question)

    print(f"\nAnswer: {answer}")

    return answer