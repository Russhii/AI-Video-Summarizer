from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

import os
from dotenv import load_dotenv

load_dotenv()


# ---------------------------------------------------------
# GROK LLM
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# SPLIT TRANSCRIPT
# ---------------------------------------------------------

def split_transcript(transcript: str) -> list:

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=3000,
        chunk_overlap=200
    )

    return splitter.split_text(transcript)


# ---------------------------------------------------------
# SUMMARIZE TRANSCRIPT
# ---------------------------------------------------------

def summarize(transcript: str) -> str:

    llm = get_llm()

    # Prompt for individual transcript chunks
    map_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an expert meeting summarizer. "
                "Summarize this portion of a meeting transcript "
                "concisely while preserving important information, "
                "decisions, discussions, and facts."
            ),
            (
                "human",
                "{text}"
            ),
        ]
    )

    map_chain = map_prompt | llm | StrOutputParser()

    # Split transcript
    chunks = split_transcript(transcript)

    print(f"Transcript split into {len(chunks)} chunks.")

    # Summarize every chunk
    chunk_summaries = []

    for i, chunk in enumerate(chunks):

        print(
            f"Summarizing transcript chunk "
            f"{i + 1}/{len(chunks)}..."
        )

        summary = map_chain.invoke(
            {
                "text": chunk
            }
        )

        chunk_summaries.append(summary)

    # Combine partial summaries
    combined = "\n\n".join(chunk_summaries)

    # Final summarization prompt
    combined_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an expert meeting summarizer. "
                "Combine the following partial meeting summaries "
                "into one final professional meeting summary.\n\n"

                "Requirements:\n"
                "- Use clear bullet points.\n"
                "- Include the main topics discussed.\n"
                "- Include important conclusions.\n"
                "- Include important decisions.\n"
                "- Do not invent information.\n"
                "- Do not repeat the same information.\n"
                "- Keep the summary concise but useful."
            ),
            (
                "human",
                "{text}"
            ),
        ]
    )

    combined_chain = (
        RunnablePassthrough()
        | RunnableLambda(lambda x: {"text": x})
        | combined_prompt
        | llm
        | StrOutputParser()
    )

    print("Generating final meeting summary...")

    final_summary = combined_chain.invoke(combined)

    print("Summary generation complete.")

    return final_summary


# ---------------------------------------------------------
# GENERATE MEETING TITLE
# ---------------------------------------------------------

def generate_title(transcript: str) -> str:

    llm = get_llm()

    title_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Based on the meeting transcript, generate a "
                "short professional meeting title "
                "(maximum 8 words). "
                "Only return the title, nothing else."
            ),
            (
                "human",
                "{text}"
            ),
        ]
    )

    title_chain = (
        title_prompt
        | llm
        | StrOutputParser()
    )

    title = title_chain.invoke(
        transcript[:2000]
    )

    return title.strip()