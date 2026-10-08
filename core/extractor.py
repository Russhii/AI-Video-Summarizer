# Actionable items, decisions, questions
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
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
        temperature=0.2
    )


# ---------------------------------------------------------
# BUILD COMMON CHAIN
# ---------------------------------------------------------

def build_chain(system_prompt: str):

    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                system_prompt
            ),
            (
                "human",
                "{text}"
            ),
        ]
    )

    chain = (
        RunnablePassthrough()
        | RunnableLambda(
            lambda x: {"text": x}
        )
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain


# ---------------------------------------------------------
# ACTION ITEMS
# ---------------------------------------------------------

def extract_action_items(transcript: str) -> str:

    chain = build_chain(
        "You are an expert meeting analyst. "

        "From the meeting transcript, extract all action items. "

        "For each action item provide:\n"

        "- Task description\n"
        "- Owner (who is responsible)\n"
        "- Deadline (if mentioned, otherwise write "
        "'Not specified')\n\n"

        "Format the result as a numbered list.\n"

        "Example format:\n"

        "1. Task: Prepare the project report\n"
        "   Owner: Rahul\n"
        "   Deadline: Friday\n\n"

        "Do not invent owners or deadlines. "

        "If no action items are found, say:\n"
        "'No action items found.'"
    )

    print("Extracting action items...")

    return chain.invoke(transcript)


# ---------------------------------------------------------
# KEY DECISIONS
# ---------------------------------------------------------

def extract_key_decisions(transcript: str) -> str:

    chain = build_chain(
        "You are an expert meeting analyst. "

        "From the meeting transcript, extract all key decisions "
        "that were actually made during the meeting.\n\n"

        "Format the result as a numbered list.\n\n"

        "Only include decisions supported by the transcript. "

        "Do not invent or assume decisions.\n\n"

        "If no key decisions are found, say:\n"
        "'No key decisions found.'"
    )

    print("Extracting key decisions...")

    return chain.invoke(transcript)


# ---------------------------------------------------------
# OPEN QUESTIONS
# ---------------------------------------------------------

def extract_questions(transcript: str) -> str:

    chain = build_chain(
        "You are an expert meeting analyst. "

        "From the meeting transcript, extract all unresolved "
        "questions or topics that require follow-up.\n\n"

        "Format the result as a numbered list.\n\n"

        "Only include questions or unresolved topics supported "
        "by the transcript.\n\n"

        "If no open questions are found, say:\n"
        "'No open questions found.'"
    )

    print("Extracting open questions...")

    return chain.invoke(transcript)